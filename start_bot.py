#!/usr/bin/env python3
"""
Startup script for Hoster.by deployment
Simple wrapper to start the bot application
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from env.production if available
env_file = project_root / 'env.production'
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

async def main():
    """Main startup function"""
    try:
        print("🚀 Starting Bakery Bot for Hoster.by...")
        
        # Import and run the main application
        from bot.main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

