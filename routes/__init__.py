from .main import register_routes as register_main_routes
from .error import register_routes as register_error_routes
from .health import register_routes as register_health_routes
from .db import register_routes as register_db_routes
from .crossservice import register_routes as register_crossservice_routes
from .tasks import register_routes as register_task_routes
from .vault import register_routes as register_vault_routes
from .images import register_routes as register_images_routes 

def register_routes(app):
    register_main_routes(app)
    register_error_routes(app)
    register_health_routes(app)
    register_db_routes(app)
    register_crossservice_routes(app)
    register_task_routes(app)
    register_vault_routes(app)
    register_images_routes(app)