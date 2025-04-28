# backend/webapp/__init__.py
import os
from flask import Blueprint

from .routes_auth import bp_auth
from .routes_profile import bp_profile
from .routes_token import bp_token
from .routes_todo import bp_todo

bp = Blueprint('webapp', __name__, url_prefix=F"{os.environ.get('URL_PREFIX', '')}/")

bp.register_blueprint(bp_auth)

bp.register_blueprint(bp_profile)
bp.register_blueprint(bp_token)
bp.register_blueprint(bp_todo)
