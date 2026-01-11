# run.py - MAIN ENTRY POINT
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the app
from backend.app import app

if __name__ == '__main__':
    print("Starting Road Risk System...")
    print("Dashboard: http://localhost:5000")
    print("API: http://localhost:5000/api/cities")
    app.run(debug=True, port=5000, host='0.0.0.0')
  
