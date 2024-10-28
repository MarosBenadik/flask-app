import os

MINIO_PATH = os.getenv('MINIO_PATH', 'default')

def get_image_url(bucket: str, image_id: str):
    """Generate the URL for a specific image."""
    return f"http://{MINIO_PATH}/{bucket}/{image_id}" 