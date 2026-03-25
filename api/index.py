import os
import sys

# Add the project root to the sys.path so app.py and other modules can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as handler

# This ensures transparency for Vercel's index-based routing
app = handler
