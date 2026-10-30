"""Use interactive passwords, never source-controlled demo credentials."""
import argparse
import getpass
from werkzeug.security import generate_password_hash
from lungcare import create_app, initialize_indexes
from lungcare.security import db,now
from lungcare.workflows import run_review_session,transaction
parser=argparse.ArgumentParser();parser.add_argument('command',choices=['init-db','seed-doctors','create-admin','run-session','recover-processing']);args=parser.parse_args()
app=create_app()
with app.app_context():
    database=db()
    if args.command=='init-db': initialize_indexes(database);print('Indexes initialized.')
    elif args.command in ('seed-doctors','create-admin'):
        names=['Doctor A','Doctor B','Doctor C'] if args.command=='seed-doctors' else ['Coordinator']
        for name in names:
            address=input(f'{name} email: ').strip().lower();password=getpass.getpass(f'{name} password (12+ characters): ')
            if len(password)<12 or '@' not in address:raise SystemExit('Invalid email or password.')
            role='doctor' if name.startswith('Doctor') else 'admin'
            existing=database.users.find_one({'email':address})
            if existing:
                if existing['role']!=role or existing['full_name']!=name:raise SystemExit('Existing account has a different identity or role.')
                print(f'{name} already exists; left unchanged.');continue
            password_hash=generate_password_hash(password,method='pbkdf2:sha256:600000')
            def provision(database,session):
                ident=database.users.insert_one({'full_name':name,'email':address,'role':role,'availability':'available' if role=='doctor' else None,'password_hash':password_hash,'created_at':now()},session=session).inserted_id
                if role=='doctor':database.doctors.insert_one({'user_id':ident,'created_at':now(),'academic_demo':True},session=session)
            transaction(provision)
            print(f'{name} provisioned.')
    elif args.command=='run-session':
        time=now();slot=int(time.timestamp())//7200;print('Session completed:',run_review_session(f'scheduled:{slot}',time))
    elif args.command=='recover-processing':
        from datetime import timedelta
        cutoff=now()-timedelta(minutes=30)
        rows=database.cases.find({'status':'ai_processing','processing_started_at':{'$lt':cutoff}})
        count=0
        for case in rows:
            if database.predictions.find_one({'case_id':case['_id']}):continue
            count+=database.cases.update_one({'_id':case['_id'],'status':'ai_processing'},{'$set':{'status':'processing_failed','updated_at':now()}}).modified_count
        print('Stale cases recovered:',count)
