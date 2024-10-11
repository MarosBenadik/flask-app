import os

# Configuration for the MySQL connection (from environment variables)
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'flaskappdb')