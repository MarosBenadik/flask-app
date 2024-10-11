from prometheus_client import Summary, Counter, Info, Gauge
import os

NODE_NAME = os.getenv('NODE_NAME', 'unknown_node')
FLASK_COLOR = os.getenv('FLASK_COLOR', 'blue')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_VERSION = os.environ.get('FLASK_VERSION', 'NONE')
CROSSSERVICE_NAME = os.environ.get('CROSSSERVICE_NAME', 'flask-blue-flaskapp-chart')  

# Prometheus metrics
REQUEST_TIME = Summary('app_processing_seconds', 'Time spent processing request')
REQUEST_COUNTER = Counter('app_requests_total', 'Total app requests', ['http_method', 'url_path', 'status_code'])
APP_INFO = Info('app_info', 'App info')
REQUEST_GAUGE = Gauge('app_requests_gauge', 'Description of gauge')

APP_INFO.info({'version': '1.0.0', 'runtime_host': NODE_NAME, 'app_color' : FLASK_COLOR, 'app_env' : FLASK_ENV})