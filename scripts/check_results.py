#!/usr/bin/env python3
"""Small result checker used by CI to enforce thresholds.

Exit codes:
  0 - pass
  1 - fail

Thresholds (based on real baseline performance):
 - spec_accuracy average must be >= 0.08 (baseline: 0.10, allowing slight degradation)
 - hallucination_check average must be >= 0.50 (baseline: 0.70 in evaluators, 0.55 in check_results)

NOTE: These thresholds are conservative based on the current ZenBot implementation.
As the knowledge base expands and retrieval improves, thresholds should be increased.

This script loads `test_cases.json` and `predictions.json` and computes simple scores.
"""
import json
import re
from pathlib import Path
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime


def spec_score(prediction: str, expected: str):
    """Improved spec scoring - matches evaluators.py spec_accuracy_evaluator"""
    pred_nums = set(re.findall(r"\d+", prediction))
    exp_nums = set(re.findall(r"\d+", expected))
    
    # Filter out dates, months, years
    filtered_pred_nums = {n for n in pred_nums 
                         if int(n) not in range(1, 32)
                         and int(n) not in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}
    filtered_exp_nums = {n for n in exp_nums if int(n) not in range(1, 32)}
    
    important_nums = {n for n in filtered_exp_nums if int(n) >= 100}
    
    has_standard = bool(re.search(r"is\s*1786|is1786", prediction, re.IGNORECASE))
    expects_standard = bool(re.search(r"is\s*1786|is1786", expected, re.IGNORECASE))
    
    if not important_nums:
        # Text-based answer - fuzzy match
        pred_lower = prediction.lower()
        exp_lower = expected.lower()
        key_phrases = []
        if "verify" in exp_lower or "consult" in exp_lower or "specialist" in exp_lower:
            key_phrases = ["verify", "consult", "team", "specialist", "inventory"]
        if "structural engineer" in exp_lower or "licensed" in exp_lower:
            key_phrases = ["structural", "engineer", "technical", "consult"]
        
        phrase_matches = sum(1 for phrase in key_phrases if phrase in pred_lower)
        return 1.0 if phrase_matches >= 2 else (0.5 if phrase_matches == 1 else 0.0)
    
    # Numeric answer - check match ratio
    matched_nums = important_nums & filtered_pred_nums
    match_ratio = len(matched_nums) / len(important_nums) if important_nums else 0.0
    
    if match_ratio == 1.0:
        return 1.0 if (not expects_standard or has_standard) else 0.7
    elif match_ratio >= 0.5:
        return 0.5
    else:
        return 0.0


def hallucination_score(prediction: str):
    """Improved hallucination scoring - matches evaluators.py hallucination_detector"""
    pred = prediction.lower()
    uncertainty = ["verify", "check with", "need to confirm", "don't have", "not sure", 
                   "consult", "i could not find", "please contact", "i need to", "let me connect"]
    confidence = ["as per", "according to", "based on", "specified in", "is 1786", 
                  "per is", "as stated", "documented"]
    guessing_bad = ["probably", "likely", "i think", "maybe", "i guess", "possibly"]

    has_uncertainty = any(w in pred for w in uncertainty)
    has_confidence = any(w in pred for w in confidence)
    has_bad_guessing = any(w in pred for w in guessing_bad)
    has_approximate = any(w in pred for w in ["approximately", "around", "roughly", "about", "~"])
    approximate_with_source = has_approximate and has_confidence

    if has_bad_guessing:
        return 0.0
    elif approximate_with_source or has_confidence or has_uncertainty:
        return 1.0
    elif has_approximate:
        return 0.5
    else:
        return 0.5


def send_email_alert(spec_avg, hall_avg, failed_checks):
    """Send email alert when quality checks fail"""
    
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    recipient = os.environ.get("EMAIL_RECIPIENT")
    
    # Skip if email not configured
    if not all([sender, password, recipient]):
        print("⚠️ Email credentials not configured, skipping alert")
        return False
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'⚠️ ZenBot Quality Alert - {len(failed_checks)} Check(s) Failed'
    msg['From'] = sender
    msg['To'] = recipient
    
    # HTML email body
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f44336; color: white; }}
            .fail {{ color: #f44336; font-weight: bold; }}
            .pass {{ color: #4CAF50; font-weight: bold; }}
            h2 {{ color: #333; }}
            .timestamp {{ color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <h2>🤖 ZenBot Quality Check Failed</h2>
        <p class="timestamp">Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        
        <p>The automated quality evaluation detected the following issues:</p>
        
        <table>
            <tr>
                <th>Metric</th>
                <th>Score</th>
                <th>Threshold</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Spec Accuracy</td>
                <td>{spec_avg:.1%}</td>
                <td>≥ 8%</td>
                <td class="{'fail' if spec_avg < 0.08 else 'pass'}">
                    {"❌ FAILED" if spec_avg < 0.08 else "✅ PASSED"}
                </td>
            </tr>
            <tr>
                <td>Hallucination Check</td>
                <td>{hall_avg:.1%}</td>
                <td>≥ 50%</td>
                <td class="{'fail' if hall_avg < 0.50 else 'pass'}">
                    {"❌ FAILED" if hall_avg < 0.50 else "✅ PASSED"}
                </td>
            </tr>
        </table>
        
        <h3>Failed Checks:</h3>
        <ul>
            {"".join(f"<li>{check}</li>" for check in failed_checks)}
        </ul>
        
        <h3>Recommended Actions:</h3>
        <ol>
            <li>Review failed test cases in <a href="https://github.com/Brohammad/workspacegmail/actions">GitHub Actions log</a></li>
            <li>Check recent changes to ZenBot knowledge base</li>
            <li>Run local evaluation: <code>python evaluators.py</code></li>
            <li>Consider expanding knowledge base with more documents (see Priority 1 improvements)</li>
        </ol>
        
        <hr>
        <p><small>This is an automated alert from ZenBot Evaluation System</small></p>
        <p><small>Repository: <a href="https://github.com/Brohammad/workspacegmail">Brohammad/workspacegmail</a></small></p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # Send email via Gmail SMTP
    try:
        print(f"📧 Sending email alert to {recipient}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ Alert email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_discord_alert(spec_avg, hall_avg, failed_checks):
    """Send alert to Discord webhook"""
    
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ Discord webhook not configured, skipping Discord alert")
        return False
    
    # Determine embed color based on severity
    # Red for failures, Orange for warnings
    color = 0xFF0000 if spec_avg < 0.08 or hall_avg < 0.50 else 0xFFA500
    
    # Build Discord embed
    embed = {
        "title": "⚠️ ZenBot Quality Check Failed",
        "description": f"The automated quality evaluation detected **{len(failed_checks)}** issue(s)",
        "color": color,
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {
                "name": "📊 Spec Accuracy",
                "value": f"{spec_avg:.1%} {'❌' if spec_avg < 0.08 else '✅'} (threshold: ≥8%)",
                "inline": True
            },
            {
                "name": "🔍 Hallucination Check",
                "value": f"{hall_avg:.1%} {'❌' if hall_avg < 0.50 else '✅'} (threshold: ≥50%)",
                "inline": True
            },
            {
                "name": "\u200b",  # Empty field for layout
                "value": "\u200b",
                "inline": True
            },
            {
                "name": "❌ Failed Checks",
                "value": "\n".join([f"• {check}" for check in failed_checks]) if failed_checks else "None",
                "inline": False
            },
            {
                "name": "🔗 Actions",
                "value": "[View GitHub Actions Run](https://github.com/Brohammad/workspacegmail/actions) • [View Repository](https://github.com/Brohammad/workspacegmail)",
                "inline": False
            }
        ],
        "footer": {
            "text": "ZenBot Evaluation System • Automated Alert"
        }
    }
    
    payload = {
        "username": "ZenBot Monitor",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/6134/6134346.png",  # Robot icon
        "embeds": [embed]
    }
    
    try:
        import urllib.request
        import json as json_lib
        
        print(f"💬 Sending Discord alert...")
        
        req = urllib.request.Request(
            webhook_url,
            data=json_lib.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'ZenBot-Monitor/1.0'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                print(f"✅ Discord alert sent successfully")
                return True
            else:
                print(f"⚠️ Discord webhook returned status {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to send Discord alert: {e}")
        return False


def main():
    tests_path = Path('test_cases.json')
    preds_path = Path('predictions.json')
    if not tests_path.exists() or not preds_path.exists():
        print('Missing test_cases.json or predictions.json')
        sys.exit(1)

    tests = json.loads(tests_path.read_text())
    preds = json.loads(preds_path.read_text())

    spec_scores = []
    hall_scores = []
    for t in tests:
        tid = str(t.get('id'))
        expected = t.get('expected_answer','')
        pred = preds.get(tid, '')
        spec_scores.append(spec_score(pred, expected))
        hall_scores.append(hallucination_score(pred))

    spec_avg = sum(spec_scores) / len(spec_scores)
    hall_avg = sum(hall_scores) / len(hall_scores)

    print(f"Spec accuracy avg: {spec_avg:.3f}")
    print(f"Hallucination score avg: {hall_avg:.3f}")

    # Collect failed checks
    failed_checks = []
    threshold_failed = False
    
    # Thresholds - realistic based on current baseline
    # Baseline: spec=0.10, hallucination=0.55
    # Allow 20% degradation buffer for safety
    if spec_avg < 0.08:
        failed_checks.append(f'Spec accuracy too low: {spec_avg:.1%} < 8%')
        threshold_failed = True
        print(f'SPEC ACCURACY THRESHOLD FAILED: {spec_avg:.3f} < 0.08')
    
    if hall_avg < 0.50:
        failed_checks.append(f'Hallucination score too low: {hall_avg:.1%} < 50%')
        threshold_failed = True
        print(f'HALLUCINATION THRESHOLD FAILED: {hall_avg:.3f} < 0.50')
    
    # Send alerts if any checks failed
    if threshold_failed:
        # Send both email and Discord alerts (parallel - don't fail if one fails)
        email_sent = send_email_alert(spec_avg, hall_avg, failed_checks)
        discord_sent = send_discord_alert(spec_avg, hall_avg, failed_checks)
        
        if email_sent or discord_sent:
            print(f"📢 Alerts sent: Email={'✅' if email_sent else '❌'}, Discord={'✅' if discord_sent else '❌'}")
        else:
            print("⚠️ No alerts were sent (credentials not configured)")
        
        sys.exit(1)

    print('✅ All checks passed!')
    print(f'  Spec accuracy: {spec_avg:.3f} >= 0.08')
    print(f'  Hallucination: {hall_avg:.3f} >= 0.50')
    sys.exit(0)


if __name__ == '__main__':
    main()
