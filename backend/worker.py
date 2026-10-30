"""Single durable polling worker. Transactions + unique job keys make duplicate workers safe."""
import time
from datetime import datetime,timezone
from lungcare import create_app
from lungcare.security import db, now
from lungcare.workflows import run_review_session
app=create_app()
while True:
    try:
        with app.app_context():
            slot=int(now().timestamp())//7200
            scheduled=datetime.fromtimestamp(slot*7200,timezone.utc)
            run_review_session(f'scheduled:{slot}',scheduled)
    except Exception as error:
        app.logger.warning('Scheduler attempt failed (%s); will retry.',type(error).__name__)
        try:
            with app.app_context():db().scheduler_errors.insert_one({'created_at':now(),'error_type':type(error).__name__})
        except Exception:pass
    time.sleep(60)
