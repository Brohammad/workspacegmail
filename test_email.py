#!/usr/bin/env python3
"""Quick test to verify email configuration works"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

def test_email():
    """Send a test email to verify configuration"""
    
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    recipient = os.environ.get("EMAIL_RECIPIENT")
    
    if not sender:
        print("❌ ERROR: EMAIL_SENDER not set")
        print("   Set it with: export EMAIL_SENDER='your-email@gmail.com'")
        return False
    
    if not password:
        print("❌ ERROR: EMAIL_PASSWORD not set")
        print("   Set it with: export EMAIL_PASSWORD='your-app-password'")
        return False
    
    if not recipient:
        print("❌ ERROR: EMAIL_RECIPIENT not set")
        print("   Set it with: export EMAIL_RECIPIENT='recipient@example.com'")
        return False
    
    print(f"📧 Testing email configuration...")
    print(f"   Sender: {sender}")
    print(f"   Recipient: {recipient}")
    
    # Create test message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '✅ ZenBot Email Test - Configuration Successful'
    msg['From'] = sender
    msg['To'] = recipient
    
    html = f"""
    <html>
    <body>
        <h2>✅ Email Configuration Test</h2>
        <p>This is a test email from your ZenBot evaluation system.</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>If you're reading this, your email alerts are configured correctly! 🎉</p>
        
        <h3>Configuration Details:</h3>
        <ul>
            <li>Sender: {sender}</li>
            <li>Recipient: {recipient}</li>
            <li>SMTP Server: smtp.gmail.com:465 (SSL)</li>
        </ul>
        
        <p>You'll receive alerts like this when ZenBot quality checks fail.</p>
        
        <hr>
        <p><small>ZenBot Evaluation System - Email Configuration Test</small></p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # Send email
    try:
        print("   Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            print("   Logging in...")
            server.login(sender, password)
            print("   Sending email...")
            server.send_message(msg)
        print(f"✅ SUCCESS! Test email sent to {recipient}")
        print(f"   Check your inbox (and spam folder just in case)")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ AUTHENTICATION FAILED: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're using an App Password, not your regular Gmail password")
        print("2. Get one here: https://myaccount.google.com/apppasswords")
        print("3. Make sure 2FA is enabled on your Gmail account")
        print("4. Remove any spaces from the app password")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check your network/firewall allows port 465")
        print("2. Verify EMAIL_SENDER is correct")
        print("3. Try regenerating the app password")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("ZenBot Email Configuration Test")
    print("=" * 80)
    print()
    
    success = test_email()
    
    print()
    print("=" * 80)
    if success:
        print("✅ Email configuration is working!")
        print()
        print("Next steps:")
        print("1. Add these 3 secrets to GitHub:")
        print("   https://github.com/Brohammad/workspacegmail/settings/secrets/actions")
        print("   - EMAIL_SENDER (your Gmail address)")
        print("   - EMAIL_PASSWORD (your app password)")
        print("   - EMAIL_RECIPIENT (where to send alerts)")
        print()
        print("2. Commit and push the changes:")
        print("   git add scripts/check_results.py .github/workflows/evaluate.yml")
        print("   git commit -m 'Add email alerts for quality check failures'")
        print("   git push")
    else:
        print("❌ Email configuration needs fixing. See troubleshooting tips above.")
    print("=" * 80)
