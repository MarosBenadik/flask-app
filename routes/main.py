from flask import Flask, render_template, jsonify, url_for, send_from_directory, g
import sys, os, socket, logging, requests
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime
import pymysql
from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE, NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION
from tools.db_creds import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from tools.tools import get_endpoints, connect_to_database

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def register_routes(app):

    @app.route('/')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def hello():
        logger.info("Main route accessed")
        REQUEST_COUNTER.labels(http_method='GET', url_path='/', status_code='200').inc()
        """Example route to check database connection."""
        if 'db' not in g:
            g.db = connect_to_database()
            
        cursor = g.db.cursor()
        db_status = cursor.execute("SELECT 'Hello, MySQL!' AS message")
        cursor.close()
        db_status = False

        endpoints = get_endpoints(app)

        return render_template('index.html', endpoints=endpoints, flask_env=FLASK_ENV, flask_color=FLASK_COLOR, node_name=NODE_NAME, flask_version=FLASK_VERSION, db_status=db_status)


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

        endpoints = get_endpoints(app)

        data = {
            'time': current_time,
            'date': current_date,
            'pod_name': pod_name,
            'ip_address': ip_address
        }
        return render_template('info.html', data=data, endpoints=endpoints)

    @app.route('/endpoints')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def list_endpoints():
        logger.info("Endpoints route accessed")
        REQUEST_COUNTER.labels(http_method='GET', url_path='/endpoints', status_code='200').inc()
        
        endpoints = get_endpoints(app)

        return render_template('endpoints.html', endpoints=endpoints)

    @app.route('/help')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def help():
        logger.info("Help route accessed")
        endpoints = get_endpoints(app)
        REQUEST_COUNTER.labels(http_method='GET', url_path='/help', status_code='200').inc()

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