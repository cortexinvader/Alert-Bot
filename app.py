from app import create_app
from app.queue import start_scheduler
from app.handlers import setup_telegram_bot
from app.models import get_session, APIKey
import threading

app = create_app()

def init_default_keys():
    db = get_session()
    existing_keys = db.query(APIKey).count()
    
    if existing_keys == 0:
        with open('key.txt', 'r') as f:
            keys = [line.strip() for line in f if line.strip()]
        
        for key in keys:
            api_key = APIKey(key=key)
            db.add(api_key)
        
        db.commit()
    db.close()

def run_telegram_bot():
    setup_telegram_bot()

if __name__ == '__main__':
    init_default_keys()
    start_scheduler()
    
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
