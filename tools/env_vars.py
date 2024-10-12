import os

rabbitmq_host = os.getenv('RABBIT_MQ_HOST', 'default')
rabbitmq_port = int(os.getenv('RABBIT_MQ_PORT', 5672))

NODE_NAME = os.getenv('NODE_NAME', 'unknown_node')
FLASK_COLOR = os.getenv('FLASK_COLOR', 'blue')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_VERSION = os.environ.get('FLASK_VERSION', 'NONE')
CROSSSERVICE_NAME = os.environ.get('CROSSSERVICE_NAME', 'flask-blue-flaskapp-chart')

RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'NONE')