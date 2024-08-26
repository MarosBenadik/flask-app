from flask import Flask, render_template, jsonify, url_for, send_from_directory
import logging
import sys
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
import socket
from datetime import datetime
import os

# Access environment variables
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
FLASK_COLOR = os.environ.get('FLASK_COLOR', 'NONE')
NODE_NAME = os.environ.get('NODE_NAME', 'NONE')

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_TIME = Summary('app_processing_seconds', 'Time spent processing request')
REQUEST_COUNTER = Counter('app_requests_total', 'Total app requests', ['http_method', 'url_path', 'status_code'])
APP_INFO = Info('app_info', 'App info')
REQUEST_GAUGE  = Gauge('app_requests_gauge', 'Description of gauge')

# Define the prefix
PREFIX = f'/{FLASK_COLOR}'

# Initialize Flask app with static URL path and folder
app = Flask(__name__, static_url_path=f'{PREFIX}/static', static_folder='static')
APP_INFO.info({'version': '1.0.0', 'runtime_host': NODE_NAME, 'app_color' : FLASK_COLOR, 'app_env' : FLASK_ENV})


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def hello():
    logger.info("Main route accessed")
    REQUEST_COUNTER.labels(http_method='GET', url_path='/', status_code='200').inc()

    endpoints = []

    for rule in app.url_map.iter_rules():
        # Skip the `static` endpoint and any other endpoints with parameters
        if rule.endpoint == 'static' or rule.arguments:
            continue

        try:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        except TypeError:
            url = url_for(rule.endpoint)  # Handle endpoints with missing parameters

        endpoints.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': PREFIX + url
        })

    return render_template('index.html', endpoints=endpoints, flask_env=FLASK_ENV, flask_color=FLASK_COLOR, node_name=NODE_NAME)

@app.route('/health')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def health():
    logger.info("Health route accessed")
    return jsonify(status="UP")

@app.route('/info')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def info():
    logger.info("Info route accessed")
    REQUEST_COUNTER.labels(http_method='GET', url_path='/info', status_code='200').inc()
    pod_name = socket.gethostname()
    ip_address = socket.gethostbyname(pod_name)
    current_time = datetime.now().strftime('%H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')

    endpoints = []

    for rule in app.url_map.iter_rules():
        # Skip the `static` endpoint and any other endpoints with parameters
        if rule.endpoint == 'static' or rule.arguments:
            continue

        try:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        except TypeError:
            url = url_for(rule.endpoint)  # Handle endpoints with missing parameters

        endpoints.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': PREFIX + url
        })

    data = {
        'time': current_time,
        'date': current_date,
        'pod_name': pod_name,
        'ip_address': ip_address
    }
    return render_template('info.html', data=data, endpoints=endpoints)

@app.route('/metrics')
def metrics():
    return generate_latest(), 200

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

@app.route('/help')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def help():
    logger.info("Help route accessed")
    endpoints = []
    REQUEST_COUNTER.labels(http_method='GET', url_path='/help', status_code='200').inc()

    for rule in app.url_map.iter_rules():
        # Skip the `static` endpoint and any other endpoints with parameters
        if rule.endpoint == 'static' or rule.arguments:
            continue

        try:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        except TypeError:
            url = url_for(rule.endpoint)  # Handle endpoints with missing parameters

        endpoints.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': PREFIX + url
        })

    help_info = {
        '/': 'Main route',
        '/health': 'Health check route',
        '/info': 'Info route',
        '/metrics': 'Prometheus metrics',
        '/info/data': 'Get info data',
        '/help': 'Help route that lists all available endpoints and their descriptions',
        '/endpoints': 'List all available endpoints dynamically',
        '/static/<path:path>': 'Serve static files'
    }
    return render_template('help.html', help_info=help_info, endpoints=endpoints)

@app.route('/endpoints')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def list_endpoints():
    logger.info("Endpoints route accessed")
    REQUEST_COUNTER.labels(http_method='GET', url_path='/endpoints', status_code='200').inc()
    endpoints = []
    
    for rule in app.url_map.iter_rules():
        # Skip the `static` endpoint and any other endpoints with parameters
        if rule.endpoint == 'static' or rule.arguments:
            continue
        
        try:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        except TypeError:
            url = url_for(rule.endpoint)  # Handle endpoints with missing parameters
        
        endpoints.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'url': PREFIX + url
        })
        
    return render_template('endpoints.html', endpoints=endpoints)

@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"Page not found: {e}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    logger.info("APP has Started")
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)
