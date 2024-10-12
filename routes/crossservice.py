from flask import Flask, render_template, jsonify, url_for, send_from_directory, g
import sys, os, socket, logging, requests
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION, CROSSSERVICE_NAME 
from tools.tools import get_endpoints
from tools.logger import logger

def register_routes(app):

    @app.route('/info/data')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def get_info():
        logger.info("Info data endpoint accessed")
        REQUEST_COUNTER.labels(http_method='POST', url_path='/info/data', status_code='200').inc()
        pod_name = socket.gethostname()
        ip_address = socket.gethostbyname(pod_name)
        current_time = datetime.now().strftime('%H:%M:%S')
        current_date = datetime.now().strftime('%Y-%m-%d')

        data = {
            'time': current_time,
            'date': current_date,
            'pod_name': pod_name,
            'ip_address': ip_address
        }
        return jsonify(data)

    @app.route('/crossservice')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def crossservice():
        logger.info("CrossService route accessed")
        REQUEST_COUNTER.labels(http_method='GET', url_path='/crossservice', status_code='200').inc()

        endpoints = get_endpoints(app)

        logger.info(f"endpoints: {endpoints}")
        # Call the /data endpoint on Flask App 2
        response = requests.get(f'http://{CROSSSERVICE_NAME}.default.svc.cluster.local:5000/info/data')

            # Parse the response as JSON
        try:
            response_data = response.json()
            logger.info(f"Response data (JSON): {response_data}")
        except ValueError as e:
            # Handle error if response is not valid JSON
            logger.error(f"Failed to parse JSON response: {e}")
            response_data = "Invalid JSON response"

        logger.info(f"response: {response_data}")
        return render_template('crossservice.html', response=response_data, endpoints=endpoints, crossservice=CROSSSERVICE_NAME)

