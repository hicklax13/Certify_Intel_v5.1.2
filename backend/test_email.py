"""
Certify Intel - Email Configuration Test
Tests the email alert system configuration.
"""
import os
import sys

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. Environment variables must be set manually.")

from alerts import AlertSystem, AlertConfig


def test_email_config():
    """Test email configuration."""
    print("=" * 60)
    print("Certify Intel - Email Configuration Test")
    print("=" * 60)
    
    config = AlertConfig()
    
    print("\n📧 Email Configuration Status:")
    print("-" * 40)
    print(f"  SMTP Host: {config.smtp_host}")
    print(f"  SMTP Port: {config.smtp_port}")
    print(f"  SMTP User: {config.smtp_user or '❌ NOT SET'}")
    print(f"  SMTP Password: {'✅ Set' if config.smtp_password else '❌ NOT SET'}")
    print(f"  From Email: {config.from_email}")
    print(f"  To Emails: {config.to_emails or '❌ NOT SET'}")
    
    # Check if configured
    if not config.smtp_user:
        print("\n⚠️  Email is NOT configured!")
        print("\nTo enable email alerts:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your SMTP credentials")
        print("  3. For Gmail, generate an App Password at:")
        print("     https://myaccount.google.com/apppasswords")
        return False
    
    if not config.to_emails:
        print("\n⚠️  No recipients configured!")
        print("  Set ALERT_TO_EMAILS in your .env file")
        return False
    
    print("\n✅ Email configuration looks good!")
    return True


def send_test_email():
    """Send a test email."""
    print("\n📤 Sending test email...")
    
    alert_system = AlertSystem()
    
    test_html = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="background: #2F5496; color: white; padding: 20px; border-radius: 8px;">
            <h1>🧪 Test Email from Certify Intel</h1>
        </div>
        <div style="padding: 20px;">
            <p>Congratulations! Your email alert system is working correctly.</p>
            <p><strong>System Status:</strong></p>
            <ul>
                <li>✅ SMTP Connection: Successful</li>
                <li>✅ Authentication: Successful</li>
                <li>✅ Email Delivery: Successful</li>
            </ul>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is a test email from the Certify Intel competitive intelligence platform.
            </p>
        </div>
    </body>
    </html>
    """
    
    success = alert_system.send_alert(
        subject="🧪 Certify Intel Test Email",
        body_html=test_html,
        body_text="This is a test email from Certify Intel. Your email configuration is working!"
    )
    
    if success:
        print("✅ Test email sent successfully!")
        print(f"   Check inbox for: {', '.join(alert_system.config.to_emails)}")
    else:
        print("❌ Failed to send test email.")
        print("   Check your SMTP credentials and try again.")
    
    return success


def test_weekly_summary():
    """Send a test weekly summary."""
    print("\n📊 Sending test weekly summary...")
    
    alert_system = AlertSystem()
    success = alert_system.send_weekly_summary()
    
    if success:
        print("✅ Weekly summary sent successfully!")
    else:
        print("ℹ️  Weekly summary skipped (no data or email not configured)")
    
    return success


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Certify Intel email configuration")
    parser.add_argument("--send", action="store_true", help="Send a test email")
    parser.add_argument("--weekly", action="store_true", help="Send weekly summary")
    args = parser.parse_args()
    
    # Always check configuration
    config_ok = test_email_config()
    
    if args.send and config_ok:
        send_test_email()
    elif args.weekly and config_ok:
        test_weekly_summary()
    elif not args.send and not args.weekly:
        print("\n💡 To send a test email, run:")
        print("   python test_email.py --send")
        print("\n💡 To send a weekly summary, run:")
        print("   python test_email.py --weekly")
