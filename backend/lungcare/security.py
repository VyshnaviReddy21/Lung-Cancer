import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from functools import wraps
from bson import ObjectId
from flask import current_app, request, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from .health import transaction_capable

def now(): return datetime.now(timezone.utc)
def oid(value):
    if not ObjectId.is_valid(value): abort(404, description='Record not found.')
    return ObjectId(value)
def db():
    client = current_app.extensions.get('mongo')
    if client is None: abort(503, description='MongoDB is not configured.')
    try:
        client.admin.command('ping')
        if not transaction_capable(client):
            abort(503, description='MongoDB requires a replica set or sharded cluster with transaction support.')
    except HTTPException:
        raise
    except Exception: abort(503, description='MongoDB is unavailable. Please try again.')
    return client[current_app.config['MONGODB_DATABASE']]
def public_user(user): return {'id':str(user['_id']), 'full_name':user['full_name'], 'email':user['email'], 'role':user['role'], **({'availability':user.get('availability','unavailable')} if user['role']=='doctor' else {})}
def authorized(*roles):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            token = request.cookies.get('lungcare_session', '')
            session = db().auth_sessions.find_one({'token_hash':hashlib.sha256(token.encode()).hexdigest(), 'expires_at':{'$gt':now()}}) if token else None
            if not session: abort(401,description='Please sign in.')
            user = db().users.find_one({'_id':session['user_id']})
            if not user or (roles and user['role'] not in roles): abort(403,description='Access denied.')
            g.user = user; g.auth_session = session
            return fn(*args, **kwargs)
        return wrapped
    return decorate

def session_response(user):
    from flask import jsonify
    token = secrets.token_urlsafe(48)
    db().auth_sessions.insert_one({'token_hash':hashlib.sha256(token.encode()).hexdigest(),'user_id':user['_id'],'expires_at':now()+timedelta(hours=current_app.config['SESSION_HOURS'])})
    response = jsonify(user=public_user(user))
    response.set_cookie('lungcare_session',token,httponly=True,secure=current_app.config['COOKIE_SECURE'],samesite=current_app.config['COOKIE_SAMESITE'],max_age=current_app.config['SESSION_HOURS']*3600,path='/')
    return response

def case_access(case_id):
    case = db().cases.find_one({'_id':oid(case_id)})
    if not case: abort(404,description='Case not found.')
    u = g.user
    if u['role']=='patient' and case['patient_id']!=u['_id']: abort(403,description='Access denied.')
    if u['role']=='doctor' and case.get('doctor_id')!=u['_id']: abort(403,description='Access denied.')
    return case

def text(data,key,min_length=1,max_length=300):
    value = data.get(key,'')
    if not isinstance(value,str) or not min_length<=len(value.strip())<=max_length: abort(400,description=f'Invalid {key.replace("_"," ")}.')
    return value.strip()
