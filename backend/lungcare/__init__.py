import logging
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from flask import Flask, jsonify, request
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError
from werkzeug.exceptions import HTTPException
from .config import Config
from .model import SavedModelService, ModelUnavailable
class JSONProvider(DefaultJSONProvider):
    def default(self,obj):
        if isinstance(obj,ObjectId): return str(obj)
        if isinstance(obj,datetime): return obj.isoformat().replace('+00:00','Z')
        return super().default(obj)
def create_app(overrides=None):
    app=Flask(__name__);app.config.from_object(Config)
    if overrides: app.config.update(overrides)
    app.json=JSONProvider(app)
    if not app.config['SECRET_KEY'] or len(app.config['SECRET_KEY'])<32:
        raise RuntimeError('Configure a server-only SECRET_KEY of at least 32 characters.')
    origin=app.config['FRONTEND_ORIGIN']
    if not origin or (app.config['COOKIE_SECURE'] and not origin.startswith('https://')): raise RuntimeError('Configure the exact authorized HTTPS FRONTEND_ORIGIN.')
    if app.config['COOKIE_SAMESITE'] not in ('None','Lax','Strict') or (app.config['COOKIE_SAMESITE']=='None' and not app.config['COOKIE_SECURE']):
        raise RuntimeError('SameSite=None requires secure cookies; use Lax for local HTTP development.')
    if app.config['SESSION_HOURS'] <= 0 or app.config['MAX_UPLOAD_MB'] <= 0:
        raise RuntimeError('Session duration and upload limit must be positive.')
    if app.config['COOKIE_SECURE'] and not app.config['MONGODB_TLS']:
        raise RuntimeError('Production MongoDB connections require TLS.')
    CORS(app,origins=[origin],supports_credentials=True,allow_headers=['Content-Type','X-LungCare-Request'],methods=['GET','POST','PATCH','OPTIONS'])
    @app.before_request
    def csrf():
        if request.method not in ('GET','HEAD','OPTIONS') and (request.headers.get('Origin')!=origin or request.headers.get('X-LungCare-Request')!='1'):
            return jsonify(error='Request origin verification failed.'),403
    @app.after_request
    def private_headers(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        return response
    app.extensions['mongo']=MongoClient(app.config['MONGODB_URI'],tls=app.config['MONGODB_TLS'],serverSelectionTimeoutMS=3000,maxPoolSize=30,tz_aware=True) if app.config['MONGODB_URI'] else None
    app.extensions['model']=SavedModelService(app.config)
    for key in ('UPLOAD_DIRECTORY','REPORT_DIRECTORY'):
        app.config[key]=Path(app.config[key])
        try: app.config[key].mkdir(parents=True,exist_ok=True,mode=0o700)
        except OSError: app.logger.warning('Private storage directory unavailable.')
    from .routes import bp
    app.register_blueprint(bp)
    @app.errorhandler(HTTPException)
    def http_error(error): return jsonify(error=error.description),error.code
    @app.errorhandler(DuplicateKeyError)
    def duplicate(error): return jsonify(error='This account or operation already exists.'),409
    @app.errorhandler(PyMongoError)
    def mongo_error(error):
        app.logger.warning('Database operation failed (%s).',type(error).__name__)
        return jsonify(error='Database operation unavailable. Confirm MongoDB connectivity and replica-set transaction support.'),503
    @app.errorhandler(ModelUnavailable)
    def model_error(error): return jsonify(error=str(error)),503
    @app.errorhandler(Exception)
    def unknown(error):
        app.logger.warning('Operation failed (%s).',type(error).__name__)
        return jsonify(error='The operation could not be completed. Check server diagnostics.'),500
    return app

def initialize_indexes(database):
    database.users.create_index('email',unique=True)
    database.auth_sessions.create_index('token_hash',unique=True)
    database.auth_sessions.create_index('expires_at',expireAfterSeconds=0)
    database.rate_limits.create_index('expires_at',expireAfterSeconds=0)
    database.predictions.create_index('case_id',unique=True)
    database.doctor_reviews.create_index('case_id',unique=True)
    database.reports.create_index('case_id',unique=True)
    database.review_sessions.create_index('job_key',unique=True)
    database.cases.create_index([('patient_id',ASCENDING),('created_at',ASCENDING)])
    database.cases.create_index([('doctor_id',ASCENDING),('status',ASCENDING)])
    database.notifications.create_index([('user_id',ASCENDING),('read',ASCENDING)])
    for name in ('patients','doctors','case_assignment_history','audit_events','contact_messages'):
        database[name].create_index('created_at')
