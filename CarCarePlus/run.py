import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from main import create_app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = create_app()

# Configure logging
if not app.debug:
    # Make sure the 'logs' directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/yourapp.log', maxBytes=1024 * 1024 * 100, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('YourApp startup')

if __name__ == '__main__':
    app.run(debug=False)
