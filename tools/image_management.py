import os
from minio import Minio
from flask import current_app, g
from tools.vault import get_vault_secret
from tools.logger import logger

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'default')
MINIO_VAULT_PATH = os.getenv('MINIO_VAULT_PATH', 'default')

secret = get_vault_secret(MINIO_VAULT_PATH)

access_key = secret['data']['data']['access_key']
secret_key = secret['data']['data']['secret_key']

def get_minio_client():
    if 'minio' not in g:
        # Initialize MinIO client with your app configuration
        g.minio = Minio(
            MINIO_ENDPOINT,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
    return g.minio