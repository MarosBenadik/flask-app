import os
from minio import Minio
from flask import current_app, g
from tools.vault import get_vault_secret

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'default')
MINIO_VAULT_PATH = os.getenv('MINIO_VAULT_PATH', 'default')
access_key = get_vault_secret(MINIO_VAULT_PATH)['data']['data']['access_key']
secret_key = get_vault_secret(MINIO_VAULT_PATH)['data']['data']['secret_key']

minio_endpoint = f"http://{MINIO_ENDPOINT}"

def get_minio_client():
    if 'minio' not in g:
        # Initialize MinIO client with your app configuration
        g.minio = Minio(
            minio_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
    return g.minio