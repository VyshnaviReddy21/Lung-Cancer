"""Secret-free dependency checks; no patient records are returned or created."""
import os
import tempfile


def transaction_capable(client):
    hello = client.admin.command('hello')
    return hello.get('logicalSessionTimeoutMinutes') is not None and bool(
        hello.get('setName') or hello.get('msg') == 'isdbgrid'
    )


def storage_writable(directory):
    try:
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b'lungcare-storage-check')
            probe.flush()
            os.fsync(probe.fileno())
        return True
    except OSError:
        return False


def service_health(app):
    client = app.extensions['mongo']
    mongo = False
    transactions = False
    if client is not None:
        try:
            client.admin.command('ping')
            mongo = True
            if transaction_capable(client):
                # Execute an actual read in a transaction, then abort: no state changes.
                with client.start_session() as session:
                    with session.start_transaction():
                        client[app.config['MONGODB_DATABASE']].coordination.find_one(
                            {'_id': 'assignment'}, {'_id': 1}, session=session
                        )
                        session.abort_transaction()
                transactions = True
        except Exception:
            pass
    model = app.extensions['model']
    storage = all([storage_writable(app.config[key]) for key in ('UPLOAD_DIRECTORY', 'REPORT_DIRECTORY')])
    ready = mongo and transactions and model.ready and storage
    return dict(api='ok', ready=ready,
                mongodb='connected' if mongo else 'unavailable',
                transactions='verified' if transactions else 'unavailable',
                model='ready' if model.ready else 'unavailable', model_message=model.reason,
                storage='ready' if storage else 'unavailable', max_upload_mb=app.config['MAX_UPLOAD_MB'])