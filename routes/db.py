from flask import Flask, render_template, jsonify, url_for, send_from_directory, g
import sys, os, socket, logging, requests
from prometheus_client import start_http_server, Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime
import pymysql

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION, CROSSSERVICE_NAME
from tools.db_creds import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from tools.tools import get_endpoints, connect_to_database
from tools.logger import logger

def register_routes(app):

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

        cursor.execute("SELECT COUNT(*) AS total_messages FROM messages;")
        total_messages = cursor.fetchone()['total_messages']

        # Fetch all data from each table
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()

        cursor.execute("SELECT * FROM posts;")
        posts = cursor.fetchall()

        cursor.execute("SELECT * FROM comments;")
        comments = cursor.fetchall()

        cursor.execute("SELECT * FROM messages;")
        messages = cursor.fetchall()

        cursor.close()

        endpoints = get_endpoints(app)

        # Render the template with the data
        return render_template(
            'data.html',
            endpoints=endpoints,
            total_users=total_users,
            total_posts=total_posts,
            total_comments=total_comments,
            total_messages=total_messages,
            users=users,
            posts=posts,
            comments=comments,
            messages=messages,
            flask_version="1.0.0",  # Example value; change as necessary
            flask_color="blue",      # Example value; change as necessary
            flask_env=os.getenv('FLASK_ENV', 'development'),
            node_name=os.getenv('NODE_NAME', 'unknown')
        )

    @app.route('/messages', methods=['GET'])
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def show_messages():
        """Endpoint to show all messages from the database."""
        try:
            if 'db' not in g:
                g.db = connect_to_database()
            cursor = g.db.cursor()
            cursor.execute("SELECT * FROM messages") 
            messages = cursor.fetchall()
            
            cursor.close()

            endpoints = get_endpoints(app)

            return render_template('messages.html', endpoints=endpoints, messages=messages)
            
        except Exception as e:
            logger.error(f"Error deleting messages: {e}")
            return render_template('500.html', endpoints=endpoints)

    @app.route('/messages/delete', methods=['POST'])
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def delete_all_messages():
        """Endpoint to delete all messages from the database."""
        try:
            if 'db' not in g:
                g.db = connect_to_database()
            cursor = g.db.cursor()
            
            # Delete all messages from the messages table
            cursor.execute("DELETE FROM messages")  # Adjust the table name if necessary
            connection.commit()
            
            cursor.close()
            connection.close()

            endpoints = get_endpoints(app)

            logger.info("All messages have been deleted.")
            return render_template('messagess_deleted_ok.html', endpoints=endpoints, status={"status": "Message deleted"} ), 200
        except Exception as e:
            logger.error(f"Error deleting messages: {e}")
            return render_template('500.html', endpoints=endpoints), 500