from flask import Flask, render_template, jsonify, url_for, send_from_directory, g
import sys, os, socket, logging, requests
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime
import pymysql

# Access environment variables
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
FLASK_COLOR = os.environ.get('FLASK_COLOR', 'NONE')
NODE_NAME = os.environ.get('NODE_NAME', 'NONE')
FLASK_VERSION = os.environ.get('FLASK_VERSION', 'NONE')
CROSSSERVICE_NAME = os.getenv('CROSSSERVICE_NAME', 'flask-blue-flaskapp-chart')  

# Configuration for the MySQL connection (from environment variables)
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'flaskappdb')

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_TIME = Summary('app_processing_seconds', 'Time spent processing request')
REQUEST_COUNTER = Counter('app_requests_total', 'Total app requests', ['http_method', 'url_path', 'status_code'])
APP_INFO = Info('app_info', 'App info')
REQUEST_GAUGE  = Gauge('app_requests_gauge', 'Description of gauge')

APP_INFO.info({'version': '1.0.0', 'runtime_host': NODE_NAME, 'app_color' : FLASK_COLOR, 'app_env' : FLASK_ENV})

# Define the prefix
PREFIX = f'/{FLASK_COLOR}'

# Initialize Flask app with static URL path and folder
app = Flask(__name__, static_url_path=f'{PREFIX}/static', static_folder='static')

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

with app.app_context():
    """Connects to the database when the Flask app starts."""
    g.db = connect_to_database()
    logger.info("Database connected")

@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database connection when the request ends."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("Database disconnected")

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

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

    return render_template('index.html', endpoints=endpoints, flask_env=FLASK_ENV, flask_color=FLASK_COLOR, node_name=NODE_NAME, flask_version=FLASK_VERSION, db_status=db_status)

@app.route('/crossservice')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def crossservice():
    logger.info("CrossService route accessed")
    REQUEST_COUNTER.labels(http_method='GET', url_path='/crossservice', status_code='200').inc()

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
    
    # Call the /data endpoint on Flask App 2
    response = requests.get(f'http://{CROSSSERVICE_NAME}.default.svc.cluster.local:5000/info/data')

    return render_template('crossservice.html', response=response, endpoints=endpoints, crossservice=CROSSSERVICE_NAME)

@app.route('/data')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def data():
    """Endpoint to display database summary and data."""
    if 'db' not in g:
        g.db = connect_to_database()
    cursor = g.db.cursor()

    # Fetch total counts for each table
    cursor.execute("SELECT COUNT(*) AS total_users FROM users;")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) AS total_posts FROM posts;")
    total_posts = cursor.fetchone()['total_posts']

    cursor.execute("SELECT COUNT(*) AS total_comments FROM comments;")
    total_comments = cursor.fetchone()['total_comments']

    # Fetch all data from each table
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM posts;")
    posts = cursor.fetchall()

    cursor.execute("SELECT * FROM comments;")
    comments = cursor.fetchall()

    cursor.close()

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

    # Render the template with the data
    return render_template(
        'data.html',
        endpoints=endpoints,
        total_users=total_users,
        total_posts=total_posts,
        total_comments=total_comments,
        users=users,
        posts=posts,
        comments=comments,
        flask_version="1.0.0",  # Example value; change as necessary
        flask_color="blue",      # Example value; change as necessary
        flask_env=os.getenv('FLASK_ENV', 'development'),
        node_name=os.getenv('NODE_NAME', 'unknown')
    )


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

@app.route('/health')
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def health():
    logger.info("Health route accessed")
    return jsonify(status="UP")


@app.errorhandler(404)
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def page_not_found(e):
    logger.error(f"Page not found: {e}")
    REQUEST_COUNTER.labels(http_method='GET', url_path='/404', status_code='404').inc()
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
    return render_template('404.html', endpoints=endpoints), 404

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

@app.errorhandler(500)
@REQUEST_TIME.time()
@REQUEST_GAUGE.track_inprogress()
def internal_server_error(e):
    logger.error(f"Server error: {e}")
    REQUEST_COUNTER.labels(http_method='GET', url_path='/500', status_code='500').inc()
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
    return render_template('500.html', endpoints=endpoints), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    logger.info("APP has Started")
    start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)
