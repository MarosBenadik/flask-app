import os

MINIO_PATH = os.getenv('MINIO_PATH', 'default')

def get_image_url(bucket, image_id):
    """Generate the URL for a specific image."""
    return f"http://{MINIO_PATH}:9000/{bucket}/{image_id}" 