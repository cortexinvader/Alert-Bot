from flask import request, jsonify, render_template, session, redirect, url_for
from app.models import get_session, APIKey, MessageLog
from app.handlers import send_email, send_telegram, send_facebook
from app.utils import report_error
from functools import wraps
import json
from datetime import datetime


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        db = get_session()
        key_obj = db.query(APIKey).filter_by(key=api_key, is_active=True).first()
        db.close()

        if not key_obj:
            return jsonify({"error": "Invalid API key"}), 401

        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def register_routes(app):
    from app import limiter

    @app.route('/')
    def index():
        return render_template('docs.html')

    @app.route('/send', methods=['POST', 'GET'])
    @limiter.limit("60 per minute")
    @require_api_key
    def send_message():
        try:
            if request.method == 'POST':
                data = request.json
                channel = data.get('channel')
                recipient = data.get('recipient')
                message = data.get('message')
            else:  # GET request
                channel = request.args.get('channel')
                recipient = request.args.get('recipient')
                message = request.args.get('message')

            if not all([channel, recipient, message]):
                return jsonify({"error": "Missing required fields"}), 400

            result = None
            if channel == 'email':
                result = send_email(recipient, message)
            elif channel == 'telegram':
                result = send_telegram(recipient, message)
            elif channel == 'facebook':
                result = send_facebook(recipient, message)
            else:
                return jsonify({"error": "Invalid channel"}), 400

            db = get_session()
            log = MessageLog(
                channel=channel,
                recipient=recipient,
                message=message,
                status=result['status'],
                details=result.get('details', '')
            )
            db.add(log)
            db.commit()
            db.close()

            if result['status'] == 'failed':
                from app.queue import add_to_retry_queue
                add_to_retry_queue(channel, recipient, message)

            return jsonify(result)

        except Exception as e:
            report_error(f"Error in /send endpoint: {str(e)}")
            return jsonify({"status": "failed", "details": str(e)}), 500

    @app.route('/webhook', methods=['GET', 'POST'])
    def facebook_webhook():
        from app.utils import load_env_encrypted
        if request.method == 'GET':
            verify_token = load_env_encrypted('FACEBOOK_VERIFY_TOKEN', 'alertbot_verify')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')

            if token == verify_token:
                return challenge
            return 'Invalid verification token', 403

        elif request.method == 'POST':
            from app.handlers.facebook_handler import handle_messenger_event
            data = request.json
            handle_messenger_event(data)
            return 'OK', 200

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            with open('config.json', 'r') as f:
                config = json.load(f)

            username = request.form.get('username')
            password = request.form.get('password')

            if (username == config['admin']['username'] and
                    password == config['admin']['password']):
                session['admin_logged_in'] = True
                return redirect(url_for('admin_dashboard'))

            return render_template('admin_login.html', error="Invalid credentials")

        return render_template('admin_login.html')

    @app.route('/cortex')
    @require_admin
    def admin_dashboard():
        db = get_session()
        logs = db.query(MessageLog).order_by(MessageLog.created_at.desc()).limit(100).all()
        api_keys = db.query(APIKey).all()
        db.close()

        return render_template('admin.html', logs=logs, api_keys=api_keys)

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('admin_logged_in', None)
        return redirect(url_for('admin_login'))

    @app.route('/admin/generate-key', methods=['POST'])
    @require_admin
    def generate_api_key():
        import secrets

        random_part = secrets.token_hex(4)
        new_key = f"ALB-{random_part}"

        db = get_session()
        api_key = APIKey(key=new_key)
        db.add(api_key)
        db.commit()
        db.close()

        return jsonify({"key": new_key})

    @app.route('/admin/test/<channel>', methods=['POST'])
    @require_admin
    def test_channel(channel):
        data = request.json
        recipient = data.get('recipient')
        message = data.get('message', 'Test message from AlertBot')

        result = None
        if channel == 'email':
            result = send_email(recipient, message)
        elif channel == 'telegram':
            result = send_telegram(recipient, message)
        elif channel == 'facebook':
            result = send_facebook(recipient, message)

        return jsonify(result)
