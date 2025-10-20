# AlertBot Project

## Overview
AlertBot is a production-ready Flask-based alert delivery system supporting Email, Telegram, and Facebook Messenger channels. It features a secure API with API key authentication, admin dashboard, automatic retry queue with exponential backoff, and C++ encryption for sensitive credentials.

## Project Structure
- `app/`: Main Flask application
  - `handlers/`: Channel-specific message handlers (email, telegram, facebook)
  - `models.py`: SQLAlchemy database models (API keys, message logs, retry queue)
  - `routes.py`: API routes, admin endpoints, and Facebook webhook
  - `queue.py`: Message retry queue with APScheduler and exponential backoff
  - `templates/`: HTML templates with Cyber Black & Blue theme
  - `utils/`: C++ encryption integration and error reporting
- `cpp_modules/`: C++ encryption module using pybind11 (XOR cipher)
- `config.json`: Admin credentials and system configuration
- `key.txt`: Default API keys (loaded on first run)
- `encrypt_credentials.py`: Utility to encrypt sensitive values
- Docker configuration for production deployment

## Recent Changes (2025-10-16)
### Core Implementation
- ✅ Flask backend with complete multi-channel alert delivery
- ✅ C++ encryption module built with pybind11 and integrated into all handlers
- ✅ PostgreSQL/SQLite support with SQLAlchemy ORM
- ✅ Email handler with SMTP and Cyber-themed HTML templates
- ✅ Telegram bot with /start, /getid, /help commands and inline buttons
- ✅ Facebook Messenger webhook with Get Started flow and /getpsid command
- ✅ Central /send API endpoint with API key validation
- ✅ Automatic retry queue with exponential backoff (3 attempts, 2-60s delay)
- ✅ Error reporting to admin via both Telegram and Facebook
- ✅ Rate limiting (60 req/min on /send, 200/day global)

### UI & Documentation
- ✅ Public API documentation page with Cyber Black & Blue styling
- ✅ Admin dashboard with authentication, message logs, and test buttons
- ✅ API key generation and management in admin panel
- ✅ All pages display "Powered by AlertBot" watermark

### Production Fixes
- ✅ Scheduler and Telegram bot initialization moved to create_app() for Gunicorn compatibility
- ✅ Encryption module integrated into all credential loading (load_env_encrypted)
- ✅ Docker and docker-compose configuration
- ✅ Deployment guide for Render and other platforms

## Tech Stack
- **Backend**: Flask (Python 3.11) with Flask-Limiter, Flask-CORS
- **Database**: PostgreSQL (production) / SQLite (development)
- **Encryption**: C++ with pybind11
- **Message Queue**: APScheduler for retry processing
- **Telegram**: python-telegram-bot with async support
- **Deployment**: Docker, Gunicorn (4 workers)

## Environment Configuration
Required environment variables:
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` (Email)
- `TELEGRAM_BOT_TOKEN` (Telegram bot)
- `FACEBOOK_PAGE_TOKEN`, `FACEBOOK_VERIFY_TOKEN` (Facebook Messenger)
- `SECRET_KEY` (Flask and encryption key)
- `DATABASE_URL` (auto-configured on Replit/Render)

Sensitive values can be encrypted using `encrypt_credentials.py` and stored with `ENC:` prefix.

## Admin Configuration (config.json)
- Admin username/password for dashboard access
- Admin Telegram chat ID for error notifications
- Admin Facebook PSID for error notifications
- Rate limiting and retry settings

## Deployment Status
✅ **Production Ready**
- Scheduler runs under Gunicorn
- Telegram bot polling starts automatically
- Encryption integrated for all sensitive credentials
- Docker configuration tested
- Rate limiting configured
- Error handling and reporting operational

## Next Steps for User
1. Set environment variables (SMTP, Telegram token, Facebook token)
2. Update admin credentials in config.json
3. (Optional) Encrypt sensitive values using encrypt_credentials.py
4. Deploy to Render or run with Docker
5. Configure Facebook webhook URL
6. Test all channels via admin dashboard
