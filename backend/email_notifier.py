#!/usr/bin/env python3
"""
Email Notifier - Sends email notifications via SendGrid
Queues notifications to be sent by GitHub Actions workflow
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Hardcoded paths for GitHub Actions compatibility
BASE_PATH = "/home/runner/work/The-basics/The-basics"
NOTIFICATIONS_DIR = os.path.join(BASE_PATH, "notifications")
OUTGOING_FILE = os.path.join(NOTIFICATIONS_DIR, "outgoing.json")

# Hardcoded recipient (intentional security feature)
DEFAULT_RECIPIENT = "oconnorw225@gmail.com"


class EmailNotifier:
    """Email notification system using SendGrid"""
    
    def __init__(self):
        self.recipient = DEFAULT_RECIPIENT
        self.ensure_notifications_dir()
    
    def ensure_notifications_dir(self):
        """Ensure notifications directory exists"""
        os.makedirs(NOTIFICATIONS_DIR, exist_ok=True)
    
    def queue_notification(self, subject: str, body: str, priority: str = "normal") -> bool:
        """Queue an email notification to be sent"""
        try:
            notification = {
                "to": self.recipient,
                "subject": subject,
                "body": body,
                "priority": priority,
                "queued_at": datetime.now().isoformat(),
                "sent": False
            }
            
            # Load existing queue
            queue = self.load_queue()
            
            # Add new notification
            queue.append(notification)
            
            # Save queue
            self.save_queue(queue)
            
            print(f"✅ Notification queued: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Error queuing notification: {e}")
            return False
    
    def load_queue(self) -> List[Dict]:
        """Load notification queue from file"""
        if os.path.exists(OUTGOING_FILE):
            try:
                with open(OUTGOING_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_queue(self, queue: List[Dict]):
        """Save notification queue to file"""
        with open(OUTGOING_FILE, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def send_system_status(self, status_data: Dict) -> bool:
        """Send system status notification"""
        subject = f"🚀 System Status: {status_data.get('status', 'Unknown')}"
        
        body = f"""
System Status Report
====================

Status: {status_data.get('status', 'Unknown')}
Timestamp: {datetime.now().isoformat()}

Services:
{self._format_services(status_data.get('services', {}))}

Metrics:
{self._format_metrics(status_data.get('metrics', {}))}

---
This is an automated notification from your trading system.
"""
        
        return self.queue_notification(subject, body, priority="high")
    
    def send_alert(self, alert_type: str, message: str, details: Optional[Dict] = None) -> bool:
        """Send an alert notification"""
        subject = f"🚨 ALERT: {alert_type}"
        
        body = f"""
ALERT: {alert_type}
==================

{message}

Timestamp: {datetime.now().isoformat()}
"""
        
        if details:
            body += f"\n\nDetails:\n{json.dumps(details, indent=2)}"
        
        body += "\n\n---\nThis is an automated alert from your trading system."
        
        return self.queue_notification(subject, body, priority="urgent")
    
    def send_activation_complete(self, services: List[Dict], config: Dict) -> bool:
        """Send system activation complete notification"""
        subject = "🚀 SYSTEM FULLY AUTONOMOUS AND OPERATING"
        
        body = f"""
SYSTEM ACTIVATION COMPLETE
==========================

Your trading system is now fully operational and running autonomously!

✅ ALL SYSTEMS OPERATIONAL

Services Started:
{self._format_service_list(services)}

Configuration:
{self._format_config(config)}

Access Points:
- Dashboard: http://localhost:5173
- API Server: http://localhost:3000
- Bot API: http://localhost:9000
- Dashboard API: http://localhost:8000

The system is now:
✅ Monitoring markets 24/7
✅ Executing trades automatically
✅ Managing risk with safety protocols
✅ Self-recovering from issues
✅ Sending periodic status updates

Timestamp: {datetime.now().isoformat()}

---
This is an automated notification from your trading system.
"""
        
        return self.queue_notification(subject, body, priority="high")
    
    def _format_services(self, services: Dict) -> str:
        """Format services for display"""
        lines = []
        for name, status in services.items():
            status_icon = "✅" if status == "running" else "❌"
            lines.append(f"  {status_icon} {name}: {status}")
        return "\n".join(lines) if lines else "  No services reported"
    
    def _format_service_list(self, services: List[Dict]) -> str:
        """Format service list for display"""
        lines = []
        for service in services:
            name = service.get('name', 'Unknown')
            pid = service.get('pid', 'N/A')
            port = service.get('port', 'N/A')
            lines.append(f"  ✅ {name} (PID: {pid}, Port: {port})")
        return "\n".join(lines) if lines else "  No services"
    
    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for display"""
        lines = []
        for key, value in metrics.items():
            lines.append(f"  • {key}: {value}")
        return "\n".join(lines) if lines else "  No metrics reported"
    
    def _format_config(self, config: Dict) -> str:
        """Format configuration for display"""
        lines = []
        for key, value in config.items():
            # Mask sensitive values
            if any(secret in key.lower() for secret in ['secret', 'key', 'password', 'token']):
                value = "***" + str(value)[-4:] if value else "****"
            lines.append(f"  • {key}: {value}")
        return "\n".join(lines) if lines else "  No configuration"


if __name__ == "__main__":
    # Test email notifier
    notifier = EmailNotifier()
    print(f"Email Notifier initialized")
    print(f"Recipient: {notifier.recipient}")
    
    # Test queuing a notification
    notifier.queue_notification(
        "Test Notification",
        "This is a test notification from the email notifier system.",
        "low"
    )
    print("Test notification queued")
