"""Transactions serialize assignment via a shared coordinator document.
MongoDB replica set is required; standalone MongoDB fails closed.
"""
import uuid
from datetime import timedelta
from flask import abort, g
from .security import db, now, oid
ACTIVE_STATUSES = ('assigned','under_review')
DECISIONS = ('agree','disagree','further_investigation')
TRANSITIONS = {'uploaded':('ai_processing',),'processing_failed':('ai_processing',),'ai_processing':('ai_completed','processing_failed'),'ai_completed':('assigned','awaiting_assignment'),'awaiting_assignment':('assigned',),'assigned':('under_review','demo_review_completed'),'under_review':('demo_review_completed',),'demo_review_completed':()}
def valid_transition(old,new): return new in TRANSITIONS.get(old,())
def notify(database,user_id,message,case_id=None,session=None):
    database.notifications.insert_one({'user_id':user_id,'message':message,'case_id':case_id,'created_at':now(),'read':False},session=session)
def audit(database,action,case_id=None,actor_id=None,session=None,**extra):
    database.audit_events.insert_one({'action':action,'case_id':case_id,'actor_id':actor_id,'created_at':now(),**extra},session=session)
def serialize_lock(database,session):
    database.coordination.update_one({'_id':'assignment'}, {'$inc':{'revision':1}}, upsert=True,session=session)
def assign_case(database,case,session,doctor_id=None,reason=None):
    if case.get('doctor_id') and not doctor_id: return
    if case['status']=='demo_review_completed': abort(409,description='Completed reviews cannot be reassigned.')
    doctor = database.users.find_one({'_id':doctor_id,'role':'doctor'},session=session) if doctor_id else None
    if doctor_id and not doctor: abort(400,description='Invalid doctor.')
    if doctor is None:
        doctors = list(database.users.find({'role':'doctor','availability':'available'},session=session))
        ranked = [(database.cases.count_documents({'doctor_id':d['_id'],'status':{'$in':ACTIVE_STATUSES}},session=session),str(d['_id']),d) for d in doctors]
        doctor = min(ranked,key=lambda x:(x[0],x[1]))[2] if ranked else None
    old = case.get('doctor_id')
    if not doctor:
        database.cases.update_one({'_id':case['_id']},{'$set':{'status':'awaiting_assignment','updated_at':now()}},session=session)
        for admin in database.users.find({'role':'admin'},session=session): notify(database,admin['_id'],'A case is awaiting an available demo doctor.',case['_id'],session)
        return
    database.cases.update_one({'_id':case['_id']},{'$set':{'doctor_id':doctor['_id'],'status':'assigned','updated_at':now()}},session=session)
    database.case_assignment_history.insert_one({'case_id':case['_id'],'previous_doctor_id':old,'doctor_id':doctor['_id'],'reason':reason or 'Lowest active workload; deterministic ID tie-break.','created_at':now()},session=session)
    notify(database,doctor['_id'],'A case has been assigned to you for academic review.',case['_id'],session)
    notify(database,case['patient_id'],f"Your case is assigned to {doctor['full_name']} for academic review.",case['_id'],session)
    audit(database,'reassignment' if old else 'assignment',case['_id'],session=session,reason=reason)

def transaction(callback):
    database = db()
    with database.client.start_session() as session:
        return session.with_transaction(lambda s: callback(database,s))

def persist_prediction(case_id,prediction):
    def work(database,session):
        serialize_lock(database,session)
        case = database.cases.find_one({'_id':case_id,'status':'ai_processing'},session=session)
        if not case: abort(409,description='Case state changed during analysis.')
        existing = database.predictions.find_one({'case_id':case_id},session=session)
        if existing: abort(409,description='Prediction already exists.')
        database.predictions.insert_one({'case_id':case_id,'created_at':now(),**prediction},session=session)
        database.cases.update_one({'_id':case_id},{'$set':{'status':'ai_completed','updated_at':now()}},session=session)
        case['status']='ai_completed'
        notify(database,case['patient_id'],'Your AI-assisted analysis is available.',case_id,session)
        assign_case(database,case,session)
        audit(database,'prediction_saved',case_id,session=session)
    transaction(work)

def reassign(case_id,doctor_id,reason,actor_id):
    def work(database,session):
        serialize_lock(database,session)
        case = database.cases.find_one({'_id':oid(case_id)},session=session)
        if not case or not database.predictions.find_one({'case_id':case['_id']},session=session): abort(409,description='A persisted successful prediction is required.')
        assign_case(database,case,session,oid(doctor_id),reason)
        audit(database,'coordinator_assignment',case['_id'],actor_id,session,reason=reason)
    transaction(work)

def save_review(case_id,doctor_id,decision,assessment,notes):
    if decision not in DECISIONS: abort(400,description='Invalid review decision.')
    def work(database,session):
        case = database.cases.find_one({'_id':case_id,'doctor_id':doctor_id,'status':{'$in':ACTIVE_STATUSES}},session=session)
        if not case: abort(409,description='Case is not assigned to you for an active review.')
        database.doctor_reviews.insert_one({'case_id':case_id,'doctor_id':doctor_id,'decision':decision,'assessment':assessment,'notes':notes,'created_at':now(),'academic_demo':True},session=session)
        database.cases.update_one({'_id':case_id,'status':case['status']},{'$set':{'status':'demo_review_completed','updated_at':now()}},session=session)
        notify(database,case['patient_id'],'Your academic doctor review has been completed.',case_id,session)
        audit(database,'demo_review_completed',case_id,doctor_id,session)
    transaction(work)

def run_review_session(key,scheduled_at):
    """A session assigns awaiting cases and reminds doctors; it NEVER invents reviews."""
    def work(database,session):
        serialize_lock(database,session)
        existing = database.review_sessions.find_one({'job_key':key},session=session)
        if existing and existing['status']=='completed': return str(existing['_id'])
        ident = existing['_id'] if existing else database.review_sessions.insert_one({'job_key':key,'scheduled_at':scheduled_at,'status':'running','created_at':now()},session=session).inserted_id
        processed = 0
        for case in database.cases.find({'status':'awaiting_assignment'},session=session):
            assign_case(database,case,session); processed += 1
        for doctor in database.users.find({'role':'doctor'},session=session):
            if database.cases.count_documents({'doctor_id':doctor['_id'],'status':{'$in':ACTIVE_STATUSES}},session=session):
                notify(database,doctor['_id'],'An academic review session is open. Review your assigned cases.',session=session)
        next_run = scheduled_at + timedelta(hours=2)
        database.review_sessions.update_one({'_id':ident},{'$set':{'status':'completed','completed_at':now(),'processed_cases':processed,'errors':[],'next_run_at':next_run}},session=session)
        audit(database,'demo_review_session',session=session,session_id=ident)
        return str(ident)
    return transaction(work)
