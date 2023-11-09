CarCarePlus Project
===================

Author: Awwal Ahmed
Git Repository: https://github.com/Inferinus/CarCarePlus

Tech Stack Used
---------------
- Python 3.8+
- Flask (A Python web framework)
- HTML/CSS/JavaScript
- SQLite for development
- Werkzeug for server-side scripting
- Jinja2 for server-side templating
- Git for version control

Installation Instructions
-------------------------
1. Ensure Python 3.8+ is installed on your machine.
2. Install pip, Python’s package installer.
3. Clone the repository from the provided Git URL or unzip the project ZIP file into your working directory.
4. Navigate to the root directory of the project via the terminal or command prompt.

Configuration Instructions
--------------------------
1. Install virtualenv via pip with the command: `pip install virtualenv`.
2. Create a virtual environment in the project's root directory: `virtualenv venv`.
3. Activate the virtual environment:
   - On Windows, use: `venv\Scripts\activate`
   - On Unix or MacOS, use: `source venv/bin/activate`
4. Install all dependencies by running: `pip install -r requirements.txt`.

Running the Code
----------------
1. Set the FLASK_APP environment variable:
   - On Windows, use: `set FLASK_APP=run.py`
   - On Unix or MacOS, use: `export FLASK_APP=run.py`
2. Start the Flask application with the command: `flask run`.
3. Access the application by navigating to `http://127.0.0.1:5000/` in your web browser.

Additional Notes
----------------
- You will need to set up environment variables for CARMD_API_KEY and CARMD_PARTNER_TOKEN to interact with the CarMD API (it is paid so be sure you have enough credits).
- Before deploying to production, ensure you have configured a production-grade server like Gunicorn and have set up a production database.

