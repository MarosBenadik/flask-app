from flask import render_template, request, jsonify
import sys, os
from prometheus_client import Summary, Counter, Gauge
from datetime import datetime
import pika, pymysql
from tools.logger import logger

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION, CROSSSERVICE_NAME, RABBITMQ_QUEUE, rabbitmq_host, rabbitmq_port
from tools.db_creds import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from tools.tools import get_endpoints, connect_to_database
from tools.rabbit_creds import rabbitmq_user, rabbitmq_password
from tools.image_render import get_image_url


def send_message_to_queue(message):
    logger.info("Sending ,essage to RabbitMQ")
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    # Publish the message
    channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message)
    connection.close()

def register_routes(app):

    # Route to render the form to send data
    @app.route('/task/send-data-form', methods=['GET'])
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def send_data_form():
        
        logo = get_image_url('flask-app', 'mb.jpg')
        endpoints = get_endpoints(app)

        return render_template('send_data.html', endpoints=endpoints, logo=logo, color=FLASK_COLOR)

    # Route to handle the POST request from the form
    @app.route('/task/send-data', methods=['POST'])
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def send_data():
        data = request.form.get('data')

        logo = get_image_url('flask-app', 'mb.jpg')
        endpoints = get_endpoints(app)

        if not data:
            return render_template('404.html', endpoints=endpoints, logo=logo, data={"error": "No data provided"}), 400

        send_message_to_queue(data)
        return render_template('send_data_ok.html', endpoints=endpoints, logo=logo, status={"status": "Message sent"}, data=data ), 200

