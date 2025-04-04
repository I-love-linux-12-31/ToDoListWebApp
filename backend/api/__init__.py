from flask import Blueprint

from .auth import bp as auth_bp
from .tasks import bp as tasks_bp

bp = Blueprint('api', __name__, url_prefix='/api/v1')
bp.register_blueprint(auth_bp)
bp.register_blueprint(tasks_bp)