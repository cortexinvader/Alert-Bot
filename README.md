# AlertBot

A secure, multi-channel alert delivery system with Email, Telegram, and Facebook Messenger support.

## Features

- 📧 **Email**: HTML templates with Cyber Black & Blue theme
- 💬 **Telegram Bot**: Commands (/start, /getid, /help) with inline buttons
- 📱 **Facebook Messenger**: Webhook integration with PSID retrieval
- 🔐 **Secure API**: API key authentication
- 🔄 **Auto Retry**: Exponential backoff for failed messages
- 📊 **Admin Dashboard**: Message logs, test controls, API key management
- 🚨 **Error Reporting**: Admin notifications via Telegram & Facebook
- 🐳 **Docker Ready**: Easy deployment with Docker Compose

## Setup

### Environment Variables

The following environment variables need to be configured:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Facebook Messenger
FACEBOOK_PAGE_TOKEN=your-facebook-page-token
FACEBOOK_VERIFY_TOKEN=alertbot_verify

# Flask (Change in production!)
SECRET_KEY=your-secret-key-here
```

### Encrypting Sensitive Credentials (Optional)

For enhanced security, you can encrypt sensitive values using the C++ encryption module:

```bash
# Build the encryption module first
python setup.py build_ext --inplace

# Encrypt a value
python encrypt_credentials.py "your-secret-value"

# Output: ENC:4a5b6c7d8e9f... (encrypted value)
```

Add the encrypted value to your `.env` file with the `ENC:` prefix:

```env
SMTP_PASSWORD=ENC:4a5b6c7d8e9f...
TELEGRAM_BOT_TOKEN=ENC:1a2b3c4d5e6f...
```

The system will automatically decrypt these values on startup using your `SECRET_KEY`.

### Configuration

Edit `config.json` to set admin credentials and notification settings:

```json
{
  "admin": {
    "username": "admin",
    "password": "admin123",
    "telegram_chat_id": "your-telegram-chat-id",
    "facebook_psid": "your-facebook-psid"
  }
}
```

### Running with Docker

```bash
docker-compose up -d
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Build C++ encryption module
python setup.py build_ext --inplace

# Run the application
python app.py
```

## API Usage

### Send Message

**Endpoint:** `POST /send`

**Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "channel": "email" | "telegram" | "facebook",
  "recipient": "address_or_id",
  "message": "Your message here"
}
```

**Response:**
```json
{
  "status": "sent" | "failed",
  "details": "..."
}
```

### Examples

#### Email
```bash
curl -X POST http://localhost:5000/send \
  -H "X-API-Key: alertbot_default_key_001" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "message": "Test alert from AlertBot"
  }'
```

#### Telegram
```bash
curl -X POST http://localhost:5000/send \
  -H "X-API-Key: alertbot_default_key_001" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "telegram",
    "recipient": "123456789",
    "message": "Test alert from AlertBot"
  }'
```

## Admin Dashboard

Access the admin panel at `/admin` with the credentials from `config.json`:

- View message logs
- Test all channels
- Generate new API keys
- Monitor system status

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your repository
3. Set environment variables in Render dashboard
4. Deploy!

Render will automatically detect the Dockerfile and deploy your application.

## Security Features

- ✅ C++ encrypted credential storage
- ✅ API key authentication
- ✅ Rate limiting on /send endpoint
- ✅ Automatic retry with exponential backoff
- ✅ Admin error notifications

## Architecture

```
AlertBot/
├── app/
│   ├── handlers/          # Channel-specific handlers
│   ├── models.py          # Database models
│   ├── routes.py          # API routes
│   ├── queue.py           # Retry queue manager
│   ├── templates/         # HTML templates
│   └── utils/             # Utilities & encryption
├── cpp_modules/           # C++ encryption module
├── config.json            # Admin configuration
├── key.txt                # Default API keys
├── Dockerfile             # Docker configuration
└── docker-compose.yml     # Docker Compose setup
```

## Powered by AlertBot

All messages and UIs display the "Powered by AlertBot" watermark.
