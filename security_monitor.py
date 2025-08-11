#!/usr/bin/env python3
"""
Bot Security Monitor Script
Run this script to check your bot's security status
"""

import os
import asyncio
import json
from bot.security import security_check, emergency_webhook_cleanup

async def main():
    """Main security monitoring function."""
    print("🛡️  Bot Security Monitor")
    print("=" * 50)
    
    # Get bot token from environment
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("❌ BOT_TOKEN environment variable not set!")
        print("Please set it before running this script.")
        return
    
    print(f"🔍 Checking security for bot: {bot_token[:20]}...")
    print()
    
    # Perform security check
    print("📊 Running security check...")
    security_results = await security_check(bot_token)
    
    # Display results
    print("\n📋 Security Report:")
    print("-" * 30)
    
    # Webhook security
    webhook = security_results["webhook_security"]
    print(f"🔗 Webhook Security: {'✅ SAFE' if webhook.get('secure') else '❌ UNSAFE'}")
    print(f"   Status: {webhook.get('status', 'Unknown')}")
    if webhook.get('url'):
        print(f"   URL: {webhook.get('url')}")
    print(f"   Recommendation: {webhook.get('recommendation', 'None')}")
    
    # Bot activity
    activity = security_results["bot_activity"]
    print(f"\n🤖 Bot Activity: {'✅ SAFE' if activity.get('secure') else '❌ SUSPICIOUS'}")
    print(f"   Status: {activity.get('status', 'Unknown')}")
    print(f"   Total Updates: {activity.get('total_updates', 0)}")
    print(f"   Suspicious: {activity.get('suspicious_count', 0)}")
    
    # Overall assessment
    print(f"\n🎯 Overall Security: {'✅ SECURE' if security_results.get('overall_secure') else '❌ COMPROMISED'}")
    
    # Emergency cleanup if needed
    if not security_results.get("overall_secure"):
        print("\n🚨 EMERGENCY CLEANUP NEEDED!")
        print("Running emergency webhook cleanup...")
        
        cleanup_result = await emergency_webhook_cleanup(bot_token)
        print(f"   Action: {cleanup_result.get('action')}")
        print(f"   Result: {cleanup_result.get('recommendation')}")
        
        if cleanup_result.get('action') == 'emergency_cleanup':
            print("\n⚠️  CRITICAL: Your bot was compromised!")
            print("   - Malicious webhook has been deleted")
            print("   - REGENERATE YOUR BOT TOKEN IMMEDIATELY")
            print("   - Contact @BotFather on Telegram")
    
    print(f"\n⏰ Check completed at: {security_results.get('timestamp')}")
    
    # Save detailed report
    with open("security_report.json", "w") as f:
        json.dump(security_results, f, indent=2, default=str)
    print("\n📄 Detailed report saved to: security_report.json")

if __name__ == "__main__":
    asyncio.run(main())
