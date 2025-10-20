from apscheduler.schedulers.background import BackgroundScheduler
from app.models import get_session, RetryQueue
from app.handlers import send_email, send_telegram, send_facebook
from app.utils import report_error
from datetime import datetime, timedelta
import json

scheduler = BackgroundScheduler()

def add_to_retry_queue(channel: str, recipient: str, message: str):
    db = get_session()
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    retry_item = RetryQueue(
        channel=channel,
        recipient=recipient,
        message=message,
        attempts=0,
        next_retry=datetime.utcnow() + timedelta(seconds=config['retry']['base_delay'])
    )
    db.add(retry_item)
    db.commit()
    db.close()

def process_retry_queue():
    db = get_session()
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    max_attempts = config['retry']['max_attempts']
    base_delay = config['retry']['base_delay']
    max_delay = config['retry']['max_delay']
    
    items = db.query(RetryQueue).filter(
        RetryQueue.next_retry <= datetime.utcnow(),
        RetryQueue.attempts < max_attempts
    ).all()
    
    for item in items:
        result = None
        
        if item.channel == 'email':
            result = send_email(item.recipient, item.message)
        elif item.channel == 'telegram':
            result = send_telegram(item.recipient, item.message)
        elif item.channel == 'facebook':
            result = send_facebook(item.recipient, item.message)
        
        if result and result['status'] == 'sent':
            db.delete(item)
        else:
            item.attempts += 1
            delay = min(base_delay * (2 ** item.attempts), max_delay)
            item.next_retry = datetime.utcnow() + timedelta(seconds=delay)
            
            if item.attempts >= max_attempts:
                report_error(
                    f"Failed to send {item.channel} message to {item.recipient} "
                    f"after {max_attempts} attempts. Message: {item.message[:50]}..."
                )
                db.delete(item)
    
    db.commit()
    db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(process_retry_queue, 'interval', seconds=30)
        scheduler.start()
