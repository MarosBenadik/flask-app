import time, pika
from tools.tools import connect_to_database
from tools.logger import logger
from tools.env_vars import FLASK_COLOR, rabbitmq_host, rabbitmq_port

RABBITMQ_QUEUE = f"{FLASK_COLOR}-queue"

### RabbitMQ Consumer Function ###
def consume_and_store_data():
    """Connects to RabbitMQ, retrieves messages, and stores them in MySQL."""
    try:
        # Set up RabbitMQ connection
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)

        # Callback function to process each message
        def callback(ch, method, properties, body):
            message = body.decode('utf-8')
            logger.info(f"Received message from RabbitMQ: {message}")
            # Insert message into MySQL
            store_data_in_mysql(message)
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Start consuming messages
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
        logger.info("Started consuming RabbitMQ messages")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Error while consuming messages: {e}")

def store_data_in_mysql(message):
    """Store the consumed message in the MySQL database."""
    try:
        connection = connect_to_database()
        with connection.cursor() as cursor:
            sql_query = "INSERT INTO messages (content) VALUES (%s)"
            cursor.execute(sql_query, (message,))
        connection.commit()
        logger.info("Message stored in MySQL")
    except Exception as e:
        logger.error(f"Error while storing message in MySQL: {e}")
    finally:
        connection.close()

### Start Background Thread ###
def start_rabbitmq_consumer():
    """Runs RabbitMQ consumer in the background every 15 seconds."""
    while True:
        logger.info("Starting RabbitMQ consumer...")
        consume_and_store_data()
        logger.info("Sleeping for 15 seconds before the next check")
        time.sleep(15)
