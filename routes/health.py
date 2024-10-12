from flask import jsonify
import sys, os, logging
from prometheus_client import Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION
from tools.logger import logger

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
