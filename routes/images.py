from flask import render_template
import sys, os, logging
from prometheus_client import Summary, Counter, generate_latest, Info, Gauge
from datetime import datetime

from tools.metrics import REQUEST_TIME, REQUEST_COUNTER, APP_INFO, REQUEST_GAUGE
from tools.env_vars import NODE_NAME, FLASK_COLOR, FLASK_ENV, FLASK_VERSION
from tools.logger import logger
from tools.tools import get_endpoints
from tools.image_render import get_image_url
from tools.image_management import get_minio_client

MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'default')

def register_routes(app):

    @app.route('/images')
    @REQUEST_TIME.time()
    @REQUEST_GAUGE.track_inprogress()
    def list_files():
        logger.info("Images route accessed")

        minio_client = get_minio_client()

        REQUEST_COUNTER.labels(http_method='GET', url_path='/images', status_code='200').inc()

        logo = get_image_url('flask-app', 'mb.jpg')
        endpoints = get_endpoints(app)
        
        list_of_images = []

        try:
            objects = minio_client.list_objects(MINIO_BUCKET)
            for obj in objects:
                list_of_images.append(obj.__dict__)
        except Exception as err:
            err = { str(err), 500 }
        logger.info(f"Images List: {list_of_images}")
        return render_template('images.html', endpoints=endpoints, logo=logo, objects=list_of_images )

        


