# AlertBot Project

## Overview
AlertBot is a complete Flask-based alert delivery system supporting Email, Telegram, and Facebook Messenger channels. It features a secure API with API key authentication, admin dashboard, automatic retry queue with exponential backoff, and C++ encryption for credentials.

## Project Structure
- `app/`: Main Flask application
  - `handlers/`: Channel-specific message handlers (email, telegram, facebook)
  - `models.py`: SQLAlchemy database models
  - `routes.py`: API routes and admin endpoints
  - `queue.py`: Message retry queue with scheduler
  - `templates/`: HTML templates with Cyber Black & Blue theme
  - `utils/`: Encryption and error reporting utilities
- `cpp_modules/`: C++ encryption module using pybind11
- `config.json`: Admin credentials and configuration
- `key.txt`: Default API keys
- Docker configuration for deployment

## Recent Changes (2025-10-16)
- Initial project setup with Flask backend
- C++ encryption module built with pybind11
- Database models for API keys, message logs, and retry queue
- Email, Telegram, and Facebook handlers implemented
- Central /send API endpoint with API key validation
- Automatic retry queue with exponential backoff
- Error reporting to admin via Telegram and Facebook
- Public documentation page and admin dashboard
- Docker configuration for deployment

## Tech Stack
- Backend: Flask (Python)
- Database: SQLite with SQLAlchemy ORM
- Encryption: C++ with pybind11
- Message Queue: APScheduler
- Deployment: Docker, Gunicorn

## Configuration Needed
- Environment variables for SMTP, Telegram token, Facebook token
- Admin credentials in config.json
- Telegram chat ID and Facebook PSID for error notifications

## Deployment
- Dockerized for easy deployment to Render or similar platforms
- Uses Gunicorn for production WSGI server
