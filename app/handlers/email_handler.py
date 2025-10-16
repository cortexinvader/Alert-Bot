import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.utils import load_env_encrypted

def get_html_template(message: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
                color: #00d4ff;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(0, 0, 0, 0.6);
                border: 1px solid #00d4ff;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            }}
            .message {{
                background: rgba(0, 50, 100, 0.3);
                padding: 20px;
                border-left: 4px solid #00d4ff;
                margin: 20px 0;
                line-height: 1.6;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 12px;
                color: #0088cc;
            }}
            h2 {{
                color: #00d4ff;
                text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔔 Alert Notification</h2>
            <div class="message">{message}</div>
            <div class="footer">Powered by AlertBot</div>
        </div>
    </body>
    </html>
    """

def send_email(recipient: str, message: str, subject: str = "AlertBot Notification") -> dict:
    try:
        smtp_server = load_env_encrypted('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(load_env_encrypted('SMTP_PORT', '587'))
        smtp_user = load_env_encrypted('SMTP_USERNAME', '')
        smtp_pass = load_env_encrypted('SMTP_PASSWORD', '')
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = recipient
        
        html_content = get_html_template(message)
        msg.attach(MIMEText(message, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        return {"status": "sent", "details": "Email sent successfully"}
    except Exception as e:
        return {"status": "failed", "details": str(e)}
