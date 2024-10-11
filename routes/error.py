from flask import Flask, render_template, jsonify, url_for, send_from_directory, g
import sys, os, socket, logging, requests
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE, NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION
from tools.tools import get_endpoints

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def register_routes(app):

    @app.errorhandler(404)
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def page_not_found(e):
        logger.error(f"Page not found: {e}")
        REQUEST_COUNTER.labels(http_method='GET', url_path='/404', status_code='404').inc()
        
        endpoints = get_endpoints(app)

        return render_template('404.html', endpoints=endpoints), 404


    @app.errorhandler(500)
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def internal_server_error(e):
        logger.error(f"Server error: {e}")
        REQUEST_COUNTER.labels(http_method='GET', url_path='/500', status_code='500').inc()
        
        endpoints = get_endpoints(app)

        return render_template('500.html', endpoints=endpoints), 500