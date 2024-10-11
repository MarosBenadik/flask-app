from flask import jsonify
import sys, os, logging
from prometheus_client import Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime
import pika

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE, NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION, CROSSSERVICE_NAME
from tools.tools import get_endpoints

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def send_message_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue='task_queue')

    # Publish the message
    channel.basic_publish(exchange='', routing_key='task_queue', body=message)
    connection.close()

# Sample data storage (in-memory)
data_store = []

def register_routes(app):
    @app.route('/send-task', methods=['POST'])
    def send_task():
        task_data = request.json.get('task_data')
        send_message_to_queue(task_data)
        return jsonify({"status": "Task sent to RabbitMQ", "data": task_data}), 200

    @app.route('/data', methods=['POST'])
    def add_data():
        """Endpoint to add data to the in-memory data store."""
        new_data = request.json.get('data')
        if new_data:
            data_store.append(new_data)
            return jsonify({"status": "Data added", "data": new_data}), 201
        return jsonify({"error": "No data provided"}), 400

    @app.route('/data', methods=['GET'])
    def get_data():
        """Endpoint to retrieve all data from the in-memory data store."""
        return jsonify({"data": data_store}), 200
