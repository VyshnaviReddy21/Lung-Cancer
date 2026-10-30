import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', '')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'lungcare')
    MONGODB_TLS = os.getenv('MONGODB_TLS', 'true').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    AI_MODEL_PATH = os.getenv('AI_MODEL_PATH', '')
    MODEL_MANIFEST_PATH = os.getenv('MODEL_MANIFEST_PATH', '')
    MODEL_VERSION = os.getenv('MODEL_VERSION', '')
    UPLOAD_DIRECTORY = Path(os.getenv('UPLOAD_DIRECTORY', '/data/uploads'))
    REPORT_DIRECTORY = Path(os.getenv('REPORT_DIRECTORY', '/data/reports'))
    FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', '').rstrip('/')
    MAX_UPLOAD_MB = int(os.getenv('MAX_UPLOAD_MB', '10'))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'true').lower() == 'true'
    COOKIE_SAMESITE = os.getenv('COOKIE_SAMESITE', 'None')
    SESSION_HOURS = int(os.getenv('SESSION_HOURS', '8'))
