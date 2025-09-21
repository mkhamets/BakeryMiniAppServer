#!/usr/bin/env python3
"""
Main entry point for the Bakery Bot application in Replit
"""
import sys
import os

# Add the project root to Python path to fix imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the main function
from bot.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())