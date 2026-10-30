import hashlib
import re
import uuid
import os
from datetime import timedelta
from flask import Blueprint, request, jsonify, current_app, g, abort, send_file
from PIL import Image, UnidentifiedImageError
from werkzeug.security import generate_password_hash, check_password_hash
from .security import authorized, db, now, oid, text, public_user, session_response, case_access
from .workflows import ACTIVE_STATUSES, persist_prediction, save_review, reassign, run_review_session, notify, audit
from .reports import generate_report
from .model import ModelUnavailable
from .health import service_health
bp=Blueprint('api',__name__)
def data():
    payload=request.get_json(silent=True)
    if not isinstance(payload,dict): abort(400,description='A JSON object is required.')
    return payload
def email(payload):
    value=text(payload,'email').lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',value): abort(400,description='Invalid email address.')
    return value
def rate_limit(name,limit):
    database=db();bucket=int(now().timestamp())//900
    key=hashlib.sha256(f'{name}:{request.remote_addr}:{bucket}'.encode()).hexdigest()
    record=database.rate_limits.find_one_and_update({'_id':key},{'$inc':{'count':1},'$setOnInsert':{'expires_at':now()+timedelta(minutes=30)}},upsert=True,return_document=True)
    if record['count']>limit: abort(429,description='Too many attempts. Try again later.')
def case_json(case):
    database=db();prediction=database.predictions.find_one({'case_id':case['_id']});review=database.doctor_reviews.find_one({'case_id':case['_id']});doctor=database.users.find_one({'_id':case.get('doctor_id')}) if case.get('doctor_id') else None
    result={'id':str(case['_id']),'created_at':case['created_at'],'status':case['status'],'assigned_doctor_name':doctor['full_name'] if doctor else None}
    if prediction: result['prediction']={k:v for k,v in prediction.items() if k not in ('_id','case_id')}
    if review: result['review']={k:v for k,v in review.items() if k not in ('_id','case_id','doctor_id')}
    return result
def own_filter():
    return {'patient_id':g.user['_id']} if g.user['role']=='patient' else {'doctor_id':g.user['_id']} if g.user['role']=='doctor' else {}
def paginated_cases():
    filters=own_filter();status=request.args.get('status');search=request.args.get('search','')[:100]
    if status: filters['status']=status
    if search:
        if len(search)==24:
            from bson import ObjectId
            if ObjectId.is_valid(search): filters['_id']=ObjectId(search)
            else: return jsonify(cases=[],total=0)
        else:
            # Safe suffix matching without arbitrary regex from client.
            filters['public_id']={'$regex':re.escape(search),'$options':'i'}
    try: page=max(1,min(int(request.args.get('page',1)),100000))
    except ValueError: abort(400,description='Invalid page.')
    database=db();rows=list(database.cases.find(filters).sort('created_at',-1).skip((page-1)*20).limit(20))
    return jsonify(cases=[case_json(c) for c in rows],total=database.cases.count_documents(filters))
@bp.get('/health')
def health():
    return jsonify(service_health(current_app))
@bp.get('/health/ready')
def readiness():
    result=service_health(current_app)
    return jsonify(result),200 if result['ready'] else 503
@bp.post('/api/auth/register')
def register():
    rate_limit('register',10);payload=data();name=text(payload,'full_name',2,120);address=email(payload);password=text(payload,'password',12,256)
    if payload.get('privacy_acknowledged') is not True: abort(400,description='Privacy acknowledgment is required.')
    if payload.get('confirm_password')!=payload['password']: abort(400,description='Passwords do not match.')
    user={'full_name':name,'email':address,'password_hash':generate_password_hash(password,method='pbkdf2:sha256:600000'),'role':'patient','created_at':now(),'privacy_acknowledged_at':now()}
    def work(database,session):
        user['_id']=database.users.insert_one(user,session=session).inserted_id
        database.patients.insert_one({'user_id':user['_id'],'created_at':now()},session=session)
    from .workflows import transaction
    transaction(work)
    response=session_response(user);response.status_code=201;return response
@bp.post('/api/auth/login')
def login():
    rate_limit('login',30);payload=data();address=email(payload);password=text(payload,'password',1,256)
    user=db().users.find_one({'email':address})
    if not user or not check_password_hash(user['password_hash'],password): abort(401,description='Invalid email or password.')
    old=request.cookies.get('lungcare_session')
    if old: db().auth_sessions.delete_one({'token_hash':hashlib.sha256(old.encode()).hexdigest()})
    return session_response(user)
@bp.get('/api/auth/me')
@authorized()
def me(): return jsonify(user=public_user(g.user))
@bp.patch('/api/auth/me')
@authorized()
def profile():
    name=text(data(),'full_name',2,120);db().users.update_one({'_id':g.user['_id']},{'$set':{'full_name':name,'updated_at':now()}});return jsonify(ok=True)
@bp.post('/api/auth/logout')
@authorized()
def logout():
    db().auth_sessions.delete_one({'_id':g.auth_session['_id']});response=jsonify(ok=True);response.delete_cookie('lungcare_session',path='/',secure=current_app.config['COOKIE_SECURE'],httponly=True,samesite=current_app.config['COOKIE_SAMESITE']);return response
@bp.post('/api/contact')
def contact():
    rate_limit('contact',10);payload=data();record={k:text(payload,k,10 if k=='message' else 1,5000 if k=='message' else 300) for k in ('name','subject','message')};record['email']=email(payload);record['created_at']=now();db().contact_messages.insert_one(record);return jsonify(ok=True),201
@bp.get('/api/patients/dashboard')
@authorized('patient')
def patient_dashboard(): return dashboard()
@bp.get('/api/doctors/dashboard')
@authorized('doctor')
def doctor_dashboard(): return dashboard()
@bp.get('/api/admin/dashboard')
@authorized('admin')
def admin_dashboard(): return dashboard()
def dashboard():
    database=db();filters=own_filter();counts={'total_cases':database.cases.count_documents(filters),'completed_ai_analyses':database.predictions.count_documents({'case_id':{'$in':[c['_id'] for c in database.cases.find(filters,{'_id':1})]}}),'awaiting_assignment':database.cases.count_documents({**filters,'status':'awaiting_assignment'}),'awaiting_review':database.cases.count_documents({**filters,'status':{'$in':ACTIVE_STATUSES}}),'completed_demo_reviews':database.cases.count_documents({**filters,'status':'demo_review_completed'}),'unread_notifications':database.notifications.count_documents({'user_id':g.user['_id'],'read':False})}
    recent=list(database.cases.find(filters).sort('created_at',-1).limit(5));last=database.review_sessions.find_one(sort=[('scheduled_at',-1)])
    return jsonify(counts=counts,recent_cases=[case_json(c) for c in recent],next_session=last.get('next_run_at') if last else None)
@bp.post('/api/cases/upload')
@authorized('patient')
def upload():
    rate_limit('upload',30);image=request.files.get('image')
    if not image: abort(400,description='Choose an image.')
    filename=image.filename or '';extension=filename.rsplit('.',1)[-1].lower()
    if extension not in ('jpg','jpeg','png'): abort(400,description='Only JPG, JPEG, and PNG images are accepted.')
    from bson import ObjectId
    ident=ObjectId();path=current_app.config['UPLOAD_DIRECTORY']/f'{ident}.{extension}'
    try:
        image.save(path)
        if path.stat().st_size==0 or path.stat().st_size>current_app.config['MAX_CONTENT_LENGTH']: abort(413,description='Image size exceeds the configured limit.')
        with Image.open(path) as im:
            if im.format not in ('JPEG','PNG') or im.width*im.height>25_000_000: abort(400,description='Invalid image content or dimensions.')
            im.verify()
        with Image.open(path) as im: im.load()
        os.chmod(path,0o600)
        db().cases.insert_one({'_id':ident,'public_id':str(ident),'patient_id':g.user['_id'],'image_path':str(path),'status':'uploaded','created_at':now(),'updated_at':now()})
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
        path.unlink(missing_ok=True);abort(400,description='The file is not a readable JPG or PNG image.')
    except Exception:
        path.unlink(missing_ok=True);raise
    audit(db(),'image_uploaded',ident,g.user['_id']);return jsonify(case_id=str(ident)),201
@bp.post('/api/cases/<case_id>/predict')
@authorized('patient')
def predict(case_id):
    case=case_access(case_id);database=db()
    existing=database.predictions.find_one({'case_id':case['_id']})
    if existing: return jsonify(prediction={k:v for k,v in existing.items() if k not in ('_id','case_id')})
    claimed=database.cases.find_one_and_update({'_id':case['_id'],'status':{'$in':['uploaded','processing_failed']}},{'$set':{'status':'ai_processing','processing_started_at':now(),'updated_at':now()}})
    if not claimed: abort(409,description='Analysis is already in progress or this case cannot be analyzed.')
    try:
        prediction=current_app.extensions['model'].predict(case['image_path']);persist_prediction(case['_id'],prediction)
    except Exception:
        # Only processing state is downgraded: never overwrite a committed prediction.
        database.cases.update_one({'_id':case['_id'],'status':'ai_processing'},{'$set':{'status':'processing_failed','updated_at':now()}})
        raise
    return jsonify(prediction=prediction)
@bp.get('/api/cases')
@authorized('patient')
def cases():return paginated_cases()
@bp.get('/api/doctors/cases')
@authorized('doctor')
def doctor_cases():return paginated_cases()
@bp.get('/api/admin/cases')
@authorized('admin')
def admin_cases():return paginated_cases()
@bp.get('/api/cases/<case_id>')
@authorized()
def get_case(case_id):return jsonify(case=case_json(case_access(case_id)))
@bp.get('/api/cases/<case_id>/prediction')
@authorized()
def get_prediction(case_id):
    case=case_access(case_id);prediction=db().predictions.find_one({'case_id':case['_id']})
    if not prediction:abort(404,description='No successful prediction exists.')
    return jsonify(prediction={k:v for k,v in prediction.items() if k not in ('_id','case_id')})
@bp.get('/api/cases/<case_id>/image')
@authorized()
def image(case_id):
    case=case_access(case_id);response=send_file(case['image_path']);response.headers['Cache-Control']='private, no-store';return response
@bp.get('/api/cases/<case_id>/gradcam')
@authorized()
def gradcam(case_id):
    case_access(case_id);abort(404,description='A verified Grad-CAM feature/gradient path is not available for this SavedModel.')
@bp.patch('/api/doctors/availability')
@authorized('doctor')
def availability():
    value=data().get('availability')
    if value not in ('available','busy','unavailable'):abort(400,description='Invalid availability.')
    db().users.update_one({'_id':g.user['_id']},{'$set':{'availability':value,'updated_at':now()}});audit(db(),'doctor_availability_changed',actor_id=g.user['_id']);return jsonify(ok=True)
@bp.post('/api/cases/<case_id>/reviews')
@authorized('doctor')
def review(case_id):
    case=case_access(case_id);payload=data();decision=text(payload,'decision');assessment=text(payload,'assessment',10,5000);notes=payload.get('notes','')
    if not isinstance(notes,str) or len(notes)>5000:abort(400,description='Invalid notes.')
    save_review(case['_id'],g.user['_id'],decision,assessment,notes.strip());return jsonify(ok=True),201
@bp.get('/api/notifications')
@authorized()
def notifications():
    rows=list(db().notifications.find({'user_id':g.user['_id']}).sort('created_at',-1).limit(100));return jsonify(notifications=[{'id':str(r['_id']),'message':r['message'],'created_at':r['created_at'],'read':r['read']} for r in rows])
@bp.patch('/api/notifications/<notification_id>/read')
@authorized()
def mark_read(notification_id):
    result=db().notifications.update_one({'_id':oid(notification_id),'user_id':g.user['_id']},{'$set':{'read':True}})
    if not result.matched_count:abort(404,description='Notification not found.')
    return jsonify(ok=True)
@bp.post('/api/admin/assignments')
@bp.post('/api/admin/reassignments')
@authorized('admin')
def assignment():
    payload=data();reassign(text(payload,'case_id'),text(payload,'doctor_id'),text(payload,'reason',10,1000),g.user['_id']);return jsonify(ok=True)
@bp.get('/api/admin/doctors')
@authorized('admin')
def doctors():
    database=db();rows=list(database.users.find({'role':'doctor'}).sort('full_name',1));return jsonify(doctors=[{**public_user(d),'active_workload':database.cases.count_documents({'doctor_id':d['_id'],'status':{'$in':ACTIVE_STATUSES}})} for d in rows])
@bp.get('/api/admin/sessions')
@authorized('admin')
def sessions():return jsonify(sessions=[{'id':str(r['_id']),**{k:v for k,v in r.items() if k!='_id'}} for r in db().review_sessions.find().sort('scheduled_at',-1).limit(100)])
@bp.get('/api/admin/audit')
@authorized('admin')
def audits():return jsonify(audit=[{'id':str(r['_id']),**{k:v for k,v in r.items() if k!='_id'}} for r in db().audit_events.find().sort('created_at',-1).limit(100)])
@bp.post('/api/admin/review-sessions')
@authorized('admin')
def start_session():
    ident=run_review_session('manual:'+uuid.uuid4().hex,now());return jsonify(session_id=ident),201
@bp.get('/api/reports')
@authorized('patient')
def reports():return jsonify(reports=[{'id':str(r['_id']),'case_id':str(r['case_id']),'created_at':r['created_at']} for r in db().reports.find({'patient_id':g.user['_id']}).sort('created_at',-1).limit(100)])
@bp.route('/api/cases/<case_id>/report',methods=['GET','POST'])
@authorized()
def report(case_id):
    case=case_access(case_id)
    if request.method=='POST':
        try:generate_report(case)
        except ValueError as error:abort(409,description=str(error))
        return jsonify(ok=True)
    record=db().reports.find_one({'case_id':case['_id']})
    if not record:abort(404,description='Generate a report first.')
    response=send_file(record['path'],as_attachment=True,download_name=f'LungCare-{case_id}.pdf');response.headers['Cache-Control']='private, no-store';return response
