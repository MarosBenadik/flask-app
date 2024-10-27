from flask import jsonify
import sys, os, logging
from prometheus_client import Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION
from tools.logger import logger
from tools.tools import get_endpoints
from tools.vault import get_vault_secret

def register_routes(app):

    @app.route('/secret')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def secret():
        logger.info("Secret route accessed")
        REQUEST_COUNTER.labels(http_method='POST', url_path='/secret', status_code='200').inc()
        endpoints = get_endpoints(app)

        secret = get_vault_secret('secret/flask/testsecret')

        return render_template('secret.html', endpoints=endpoints, secret=secret )