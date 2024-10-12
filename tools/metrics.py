from prometheus_client import Summary, Counter, Info, Gauge
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV
import os

# Prometheus metrics
REQUEST_TIME = Summary('app_processing_seconds', 'Time spent processing request')
REQUEST_COUNTER = Counter('app_requests_total', 'Total app requests', ['http_method', 'url_path', 'status_code'])
APP_INFO = Info('app_info', 'App info')
REQUEST_GAUGE = Gauge('app_requests_gauge', 'Description of gauge')

APP_INFO.info({'version': '1.0.0', 'runtime_host': NODE_NAME, 'app_color' : FLASK_COLOR, 'app_env' : FLASK_ENV})