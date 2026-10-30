import pytest
import numpy as np
from lungcare.model import validate_manifest, probabilities, ModelUnavailable, SavedModelService
from lungcare.workflows import valid_transition, DECISIONS, ACTIVE_STATUSES
from lungcare import create_app

@pytest.fixture
def app(tmp_path):
    return create_app({'SECRET_KEY':'test-only-key-not-a-production-secret-1234','FRONTEND_ORIGIN':'http://localhost:8080','COOKIE_SECURE':False,'COOKIE_SAMESITE':'Lax','MONGODB_URI':'','AI_MODEL_PATH':'','MODEL_MANIFEST_PATH':'','MODEL_VERSION':'','UPLOAD_DIRECTORY':tmp_path/'uploads','REPORT_DIRECTORY':tmp_path/'reports','TESTING':True})
def test_required_four_categories_and_order():
    manifest={'verified_from_training':True,'classes':['adenocarcinoma','large.cell.carcinoma','normal','squamous.cell.carcinoma'],'input_name':'input','output_name':'out','height':224,'width':224,'channels':3,'dtype':'float32','color_order':'RGB','interpolation':'bilinear','preprocessing':'divide_255','output_semantics':'probabilities'}
    assert validate_manifest(manifest)['classes'][2]=='normal'
    manifest['classes']=['normal']*4
    with pytest.raises(ModelUnavailable): validate_manifest(manifest)
def test_no_assumed_training_preprocessing():
    with pytest.raises(ModelUnavailable):validate_manifest({'verified_from_training':False})
def test_valid_probabilities(): assert probabilities([.1,.2,.6,.1],'probabilities').tolist()==[.1,.2,.6,.1]
@pytest.mark.parametrize('raw',[[float('nan'),0,0,1],[1,1,1,1],[-.1,.2,.3,.6],[1,0,0]])
def test_invalid_outputs_fail_closed(raw):
    with pytest.raises(ModelUnavailable):probabilities(raw,'probabilities')
def test_missing_model_is_not_success(app):
    model=app.extensions['model'];assert model.ready is False
    with pytest.raises(ModelUnavailable):model.predict('/missing/image.png')
def test_statuses_do_not_complete_failed_operations():
    assert valid_transition('ai_processing','processing_failed')
    assert not valid_transition('processing_failed','demo_review_completed')
    assert not valid_transition('uploaded','assigned')
def test_three_review_decisions():assert DECISIONS==('agree','disagree','further_investigation')
def test_workload_counts_only_active_reviews():assert ACTIVE_STATUSES==('assigned','under_review')
def test_health_reports_actual_missing_services(app):
    result=app.test_client().get('/health');assert result.status_code==200
    assert result.json['mongodb']=='unavailable';assert result.json['model']=='unavailable';assert result.json['storage']=='ready';assert result.json['max_upload_mb']==10
@pytest.mark.parametrize('path',['/api/auth/me','/api/cases','/api/admin/doctors','/api/doctors/cases','/api/reports'])
def test_private_endpoints_reject_signed_out_access(app,path):assert app.test_client().get(path).status_code==401
def test_csrf_origin_rejected(app):
    result=app.test_client().post('/api/auth/login',json={'email':'test@example.com','password':'invalid'},headers={'Origin':'https://untrusted.invalid','X-LungCare-Request':'1'})
    assert result.status_code==403
def test_csrf_custom_header_required(app):
    assert app.test_client().post('/api/contact',json={},headers={'Origin':'http://localhost:8080'}).status_code==403
def test_db_unavailable_never_pretends_contact_saved(app):
    response=app.test_client().post('/api/contact',json={'name':'Test'},headers={'Origin':'http://localhost:8080','X-LungCare-Request':'1'})
    assert response.status_code==503

def test_readiness_fails_without_database_and_model(app):
    result=app.test_client().get('/health/ready')
    assert result.status_code==503
    assert result.json['ready'] is False
    assert result.json['transactions']=='unavailable'

def test_standalone_database_rejected_before_writes(app):
    from lungcare.security import db
    from werkzeug.exceptions import ServiceUnavailable
    class Admin:
        def command(self, command):
            return {'ok':1,'logicalSessionTimeoutMinutes':30}
    class Client:
        admin=Admin()
        def __getitem__(self, key):
            raise AssertionError('Standalone database must not be used')
    app.extensions['mongo']=Client()
    with app.app_context(), pytest.raises(ServiceUnavailable,match='replica set'):
        db()

def test_production_database_requires_tls(app):
    with pytest.raises(RuntimeError,match='require TLS'):
        create_app({**app.config,'FRONTEND_ORIGIN':'https://frontend.example.test','COOKIE_SECURE':True,'MONGODB_TLS':False})

def test_storage_probe_rejects_non_directory(tmp_path):
    from lungcare.health import storage_writable
    file=tmp_path/'not-a-directory';file.write_text('content')
    assert storage_writable(file) is False
