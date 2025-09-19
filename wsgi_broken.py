#!/usr/bin/env python3
"""
WSGI entry point for Hoster.by deployment
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('PYTHONPATH', str(project_root))

# Import the main application
from bot.main import main
import asyncio

def application(environ, start_response):
    """
    WSGI application entry point for Hoster.by
    """
    try:
        # Run the async main function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        
        # Return success response
        status = '200 OK'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [b'Bakery Bot is running']
        
    except Exception as e:
        # Return error response
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [f'Error: {str(e)}'.encode('utf-8')]

# For direct execution
if __name__ == '__main__':
    asyncio.run(main())
