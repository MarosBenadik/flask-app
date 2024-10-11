from flask import Flask, send_from_directory, g
import sys, logging
from prometheus_client import start_http_server
from routes import register_routes
from tools.metrics import FLASK_COLOR

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define the prefix
PREFIX = f'/{FLASK_COLOR}'

# Initialize Flask app with static URL path and folder
app = Flask(__name__, static_url_path=f'{PREFIX}/static', static_folder='static')

with app.app_context():
    print("Hello Flask app")
    """Connects to the database when the Flask app starts."""
    g.db = connect_to_database()
    logger.info("Database connected")

@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database connection when the request ends."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("Database disconnected")

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

register_routes(app)

if __name__ == '__main__':
    # Start Prometheus metrics server
    logger.info("APP has Started")
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000, debug=True)
