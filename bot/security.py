"""
Bot Security Module
Provides security functions and monitoring for the Telegram bot
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BotSecurityMonitor:
    """Monitors bot security and prevents unauthorized access."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_base = f"https://api.telegram.org/bot{bot_token}"
        self.suspicious_patterns = [
            "casino", "bet", "gambling", "slot", "poker",
            "jetacas", "work.gd", "malicious", "spam"
        ]
        self.last_webhook_check = None
        self.webhook_check_interval = timedelta(hours=1)
    
    async def check_webhook_security(self) -> Dict:
        """Check webhook security status."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/getWebhookInfo") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            webhook_info = data["result"]
                            return self._analyze_webhook_security(webhook_info)
            
            return {"secure": False, "error": "Failed to check webhook"}
            
        except Exception as e:
            logger.error(f"Error checking webhook security: {e}")
            return {"secure": False, "error": str(e)}
    
    def _analyze_webhook_security(self, webhook_info: Dict) -> Dict:
        """Analyze webhook security."""
        url = webhook_info.get("url", "")
        
        # Check if webhook is set
        if not url:
            return {"secure": True, "status": "No webhook set", "recommendation": "Safe"}
        
        # Check for suspicious patterns
        suspicious = any(pattern in url.lower() for pattern in self.suspicious_patterns)
        
        # Check if it's your own domain
        your_domains = [
            "bakery-mini-app-server-440955f475ad.herokuapp.com",
            "drazhin.by",
            "localhost",
            "127.0.0.1"
        ]
        
        is_your_domain = any(domain in url for domain in your_domains)
        
        if suspicious:
            return {
                "secure": False,
                "status": "Suspicious webhook detected",
                "url": url,
                "recommendation": "DELETE IMMEDIATELY",
                "risk": "HIGH"
            }
        elif not is_your_domain:
            return {
                "secure": False,
                "status": "Unknown webhook domain",
                "url": url,
                "recommendation": "Verify ownership or delete",
                "risk": "MEDIUM"
            }
        else:
            return {
                "secure": True,
                "status": "Webhook appears safe",
                "url": url,
                "recommendation": "Monitor regularly"
            }
    
    async def delete_webhook(self) -> Dict:
        """Delete current webhook."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/deleteWebhook") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            logger.info("Webhook deleted successfully")
                            return {"success": True, "message": "Webhook deleted"}
                        else:
                            return {"success": False, "error": data.get("description", "Unknown error")}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_secure_webhook(self, url: str) -> Dict:
        """Set webhook only to trusted URLs."""
        # Validate URL
        if not self._is_trusted_url(url):
            return {
                "success": False,
                "error": "URL not trusted. Only set webhooks to your own domains."
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/setWebhook", data={"url": url}) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            logger.info(f"Secure webhook set to: {url}")
                            return {"success": True, "message": f"Webhook set to {url}"}
                        else:
                            return {"success": False, "error": data.get("description", "Unknown error")}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_trusted_url(self, url: str) -> bool:
        """Check if URL is trusted."""
        trusted_domains = [
            "bakery-mini-app-server-440955f475ad.herokuapp.com",
            "drazhin.by",
            "localhost",
            "127.0.0.1"
        ]
        
        return any(domain in url for domain in trusted_domains)
    
    async def monitor_bot_activity(self) -> Dict:
        """Monitor bot for suspicious activity."""
        try:
            async with aiohttp.ClientSession() as session:
                # Get bot updates
                async with session.get(f"{self.api_base}/getUpdates") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            updates = data.get("result", [])
                            return self._analyze_updates(updates)
            
            return {"secure": False, "error": "Failed to get updates"}
            
        except Exception as e:
            logger.error(f"Error monitoring bot activity: {e}")
            return {"secure": False, "error": str(e)}
    
    def _analyze_updates(self, updates: List) -> Dict:
        """Analyze bot updates for suspicious activity."""
        suspicious_count = 0
        total_updates = len(updates)
        
        for update in updates:
            message = update.get("message", {})
            text = message.get("text", "").lower()
            
            # Check for suspicious content
            if any(pattern in text for pattern in self.suspicious_patterns):
                suspicious_count += 1
        
        if suspicious_count > 0:
            return {
                "secure": False,
                "status": f"Found {suspicious_count} suspicious updates",
                "total_updates": total_updates,
                "suspicious_count": suspicious_count,
                "recommendation": "Investigate immediately"
            }
        else:
            return {
                "secure": True,
                "status": "No suspicious activity detected",
                "total_updates": total_updates,
                "suspicious_count": 0
            }

# Security utility functions
async def security_check(bot_token: str) -> Dict:
    """Perform comprehensive security check."""
    monitor = BotSecurityMonitor(bot_token)
    
    results = {
        "webhook_security": await monitor.check_webhook_security(),
        "bot_activity": await monitor.monitor_bot_activity(),
        "timestamp": datetime.now().isoformat()
    }
    
    # Overall security assessment
    overall_secure = (
        results["webhook_security"].get("secure", False) and
        results["bot_activity"].get("secure", False)
    )
    
    results["overall_secure"] = overall_secure
    
    return results

async def emergency_webhook_cleanup(bot_token: str) -> Dict:
    """Emergency cleanup of compromised webhooks."""
    monitor = BotSecurityMonitor(bot_token)
    
    # Check current webhook
    webhook_status = await monitor.check_webhook_security()
    
    if not webhook_status.get("secure", True):
        # Delete compromised webhook
        delete_result = await monitor.delete_webhook()
        return {
            "action": "emergency_cleanup",
            "webhook_status": webhook_status,
            "delete_result": delete_result,
            "recommendation": "Regenerate bot token immediately"
        }
    else:
        return {
            "action": "no_action_needed",
            "webhook_status": webhook_status,
            "recommendation": "Monitor regularly"
        }
