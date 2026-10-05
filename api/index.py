# Vercel serverless entry point for the LMS Flask application
# This file is the bridge between Vercel's Python runtime and our Flask app.

import sys
import os

# Add parent directory to path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a variable named 'app' (WSGI callable)
# Our Flask app object is already named 'app' - imported above
