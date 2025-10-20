# AlertBot Deployment Guide

## Prerequisites

- Docker and Docker Compose
- Telegram Bot Token ([Get from BotFather](https://t.me/botfather))
- Facebook Page Access Token ([Meta Developers](https://developers.facebook.com/))
- SMTP Email Server Access

## Quick Start with Docker

### 1. Clone and Configure

```bash
git clone <your-repo>
cd alertbot
```

### 2. Set Environment Variables

Create a `.env` file with the following:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Facebook Messenger
FACEBOOK_PAGE_TOKEN=your-page-access-token
FACEBOOK_VERIFY_TOKEN=alertbot_verify

# Flask Secret
SECRET_KEY=generate-a-secure-random-key-here
```

### 3. Configure Admin Settings

Edit `config.json`:

```json
{
  "admin": {
    "username": "admin",
    "password": "change-this-password",
    "telegram_chat_id": "your-telegram-chat-id",
    "facebook_psid": "your-facebook-psid"
  },
  "encryption": {
    "enabled": true
  },
  "rate_limit": {
    "requests_per_minute": 60
  },
  "retry": {
    "max_attempts": 3,
    "base_delay": 2,
    "max_delay": 60
  }
}
```

### 4. Build and Run

```bash
docker-compose up -d
```

The application will be available at `http://localhost:5000`

## Deploying to Render

### 1. Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your Git repository

### 2. Configure Service

- **Name**: AlertBot
- **Environment**: Docker
- **Branch**: main
- **Plan**: Choose your plan

### 3. Add Environment Variables

Add all variables from your `.env` file in the Render dashboard:

- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `FACEBOOK_PAGE_TOKEN`
- `FACEBOOK_VERIFY_TOKEN`
- `SECRET_KEY`
- `DATABASE_URL` (automatically provided by Render if you add a PostgreSQL database)

### 4. Add PostgreSQL Database (Optional)

1. Go to your service → "Environment" tab
2. Click "New Database"
3. Select PostgreSQL
4. The `DATABASE_URL` will be automatically added to your environment

### 5. Deploy

Click "Create Web Service" and Render will automatically:
- Build the Docker image
- Deploy your application
- Provide a public URL

### 6. Configure Facebook Webhook

Once deployed, configure your Facebook webhook:

1. Go to [Meta Developers](https://developers.facebook.com/)
2. Select your app → Messenger → Settings
3. Add webhook:
   - **Callback URL**: `https://your-app.onrender.com/webhook/facebook`
   - **Verify Token**: `alertbot_verify` (or your custom token)
4. Subscribe to `messages` and `messaging_postbacks` events

## Getting User IDs

### Telegram User ID

Users can get their Telegram ID by:
1. Starting a chat with your bot
2. Sending `/getid` command
3. Or clicking "Get My ID" button

### Facebook PSID

Users can get their PSID by:
1. Sending a message to your Facebook Page
2. Clicking "Get Started"
3. Or sending `/getpsid` command

## Testing the Setup

### 1. Access Documentation

Visit `https://your-app.onrender.com/` to see the API documentation.

### 2. Login to Admin Panel

Visit `https://your-app.onrender.com/admin` and login with your credentials from `config.json`.

### 3. Test Channels

Use the admin panel test buttons to verify:
- Email sending works
- Telegram bot responds
- Facebook Messenger delivers messages

### 4. Test API

```bash
curl -X POST https://your-app.onrender.com/send \
  -H "X-API-Key: alertbot_default_key_001" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "test@example.com",
    "message": "Test alert from AlertBot"
  }'
```

## Monitoring

### Check Logs

```bash
# Docker
docker-compose logs -f

# Render
# Go to your service → Logs tab
```

### Admin Dashboard

- View message logs
- Monitor delivery status
- Check retry queue
- Review error reports

## Security Checklist

- [ ] Change default admin password in `config.json`
- [ ] Use strong `SECRET_KEY` in environment variables
- [ ] Enable HTTPS (automatic on Render)
- [ ] Rotate API keys regularly
- [ ] Use app-specific passwords for Gmail
- [ ] Keep tokens and credentials secure
- [ ] Monitor rate limiting logs

## Troubleshooting

### Email Not Sending

- Check SMTP credentials
- For Gmail, use [App Password](https://support.google.com/accounts/answer/185833)
- Verify SMTP server and port

### Telegram Bot Not Responding

- Verify bot token is correct
- Check if bot is running in logs
- Ensure webhook is not set (use polling mode)

### Facebook Webhook Verification Failed

- Check verify token matches in both Facebook settings and `.env`
- Ensure webhook URL is publicly accessible
- Verify SSL certificate is valid

### Database Connection Issues

- Check `DATABASE_URL` is set correctly
- For PostgreSQL, ensure database is created
- For SQLite (local), check file permissions

## Support

For issues or questions:
- Check the README.md
- Review admin dashboard logs
- Contact support (errors are sent to admin via Telegram/Facebook)

---

**Powered by AlertBot**
