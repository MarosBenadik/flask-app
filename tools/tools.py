from flask import Flask, render_template, jsonify, url_for, send_from_directory, g
import sys, os, socket, logging, requests
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime
import pymysql

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE, NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION, CROSSSERVICE_NAME
from tools.db_creds import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PREFIX = f'/{FLASK_COLOR}'

def get_endpoints(app):
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
    return endpoints

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )