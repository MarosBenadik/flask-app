import time, pika
from tools.tools import connect_to_database
from tools.logger import logger
from tools.env_vars import FLASK_COLOR, rabbitmq_host, rabbitmq_port
from tools.rabbit_creds import rabbitmq_user, rabbitmq_password

RABBITMQ_QUEUE = f"{FLASK_COLOR}-queue"

### RabbitMQ Consumer Function ###
def consume_and_store_data():
    """Connects to RabbitMQ, retrieves messages, and stores them in MySQL."""
    try:
        # Set up RabbitMQ connection
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)

        # Try to retrieve messages
        method_frame, header_frame, body = channel.basic_get(queue=RABBITMQ_QUEUE)

        # Callback function to process each message
        if method_frame:
            message = body.decode('utf-8')
            logger.info(f"Received message from RabbitMQ: {message}")
            # Insert message into MySQL
            store_data_in_mysql(message)
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logger.info("No messages in the queue.")
            
        # Close the connection
        connection.close()
    except Exception as e:
        logger.error(f"Error while polling RabbitMQ: {e}")

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
