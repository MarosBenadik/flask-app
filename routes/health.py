from flask import jsonify
import sys, os, logging
from prometheus_client import Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE, NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def register_routes(app):

    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200

    @app.route('/health')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def health():
        logger.info("Health route accessed")
        return jsonify(status="UP")
