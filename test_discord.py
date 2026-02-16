#!/usr/bin/env python3
"""Quick test to verify Discord webhook configuration works"""
import urllib.request
import json
import os
from datetime import datetime

def test_discord():
    """Send a test message to Discord webhook"""
    
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ ERROR: DISCORD_WEBHOOK_URL not set")
        print("   Set it with: export DISCORD_WEBHOOK_URL='your-webhook-url'")
        print("\n📝 How to get a Discord webhook URL:")
        print("   1. Open your Discord server")
        print("   2. Go to Server Settings → Integrations → Webhooks")
        print("   3. Click 'New Webhook'")
        print("   4. Name it 'ZenBot Monitor'")
        print("   5. Select the channel for alerts")
        print("   6. Click 'Copy Webhook URL'")
        print("   7. Export it: export DISCORD_WEBHOOK_URL='<paste-url-here>'")
        return False
    
    print(f"💬 Testing Discord webhook configuration...")
    print(f"   Webhook URL: {webhook_url[:50]}...")
    
    # Create test embed
    embed = {
        "title": "✅ ZenBot Discord Test - Configuration Successful",
        "description": "This is a test message from your ZenBot evaluation system.",
        "color": 0x00FF00,  # Green
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {
                "name": "📊 Test Metrics",
                "value": "Spec Accuracy: 90% ✅\nPricing: 100% ✅\nHallucination: 80% ✅",
                "inline": False
            },
            {
                "name": "🎯 Status",
                "value": "If you're reading this, your Discord webhook is configured correctly! 🎉",
                "inline": False
            },
            {
                "name": "📝 What's Next",
                "value": "• Add `DISCORD_WEBHOOK_URL` to GitHub secrets\n• Push code changes\n• Alerts will be sent here when quality checks fail",
                "inline": False
            }
        ],
        "footer": {
            "text": "ZenBot Evaluation System • Configuration Test"
        },
        "thumbnail": {
            "url": "https://cdn-icons-png.flaticon.com/512/6134/6134346.png"
        }
    }
    
    payload = {
        "username": "ZenBot Monitor",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/6134/6134346.png",
        "embeds": [embed]
    }
    
    try:
        print("   Sending test message...")
        
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'ZenBot-Monitor/1.0'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                print(f"✅ SUCCESS! Test message sent to Discord")
                print(f"   Check your Discord channel for the message")
                return True
            else:
                print(f"⚠️ Unexpected status: {response.status}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR: {e.code} - {e.reason}")
        if e.code == 404:
            print("\nTroubleshooting:")
            print("1. Check that the webhook URL is correct")
            print("2. Make sure the webhook wasn't deleted from Discord")
            print("3. Try creating a new webhook")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check your network/firewall")
        print("2. Verify the webhook URL is complete")
        print("3. Try the URL in your browser (should show webhook details)")
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("ZenBot Discord Webhook Configuration Test")
    print("=" * 80)
    print()
    
    success = test_discord()
    
    print()
    print("=" * 80)
    if success:
        print("✅ Discord webhook is working!")
        print()
        print("Next steps:")
        print("1. Add this secret to GitHub:")
        print("   https://github.com/Brohammad/workspacegmail/settings/secrets/actions")
        print("   Name: DISCORD_WEBHOOK_URL")
        print("   Value: <your-webhook-url>")
        print()
        print("2. Commit and push the changes:")
        print("   git add scripts/check_results.py .github/workflows/evaluate.yml test_discord.py")
        print("   git commit -m 'Add Discord webhook notifications'")
        print("   git push")
        print()
        print("3. When quality checks fail, you'll get alerts in Discord AND email! 📧💬")
    else:
        print("❌ Discord webhook needs configuration. See instructions above.")
    print("=" * 80)
