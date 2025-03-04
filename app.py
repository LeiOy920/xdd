import logging
import os

from flask import request

from app import create_app


os.environ['FLASK_ENV'] = 'development'
app = create_app()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def log_request_info():
    logger.info('Headers: %s', request.headers)
    logger.info('Body: %s', request.get_data())

if __name__ == '__main__':
    app.run(debug=True)