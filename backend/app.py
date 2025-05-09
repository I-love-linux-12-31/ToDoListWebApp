import sys
import os
import hashlib
import logging
from flask_swagger_ui import get_swaggerui_blueprint
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_cors import CORS

if os.environ.get("DOTENV", False):
    from dotenv import load_dotenv
    load_dotenv()


from flask import Flask, get_flashed_messages, redirect, url_for, render_template, request, session, jsonify
from db import global_init, create_session

from decorators import token_auth

from api import bp as api_bp
from webapp import bp as webapp_bp

URL_PREFIX = os.environ.get("URL_PREFIX", "")

app = Flask(__name__, static_url_path=F"{URL_PREFIX}/static")
app.secret_key = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(24)).hexdigest())

# Enable CORS for all routes
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization", "X-CSRFToken", "X-CSRF-Token"])

# Set CSRF headers
app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-CSRF-Token']
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_HOST_CHECK'] = False  # Disable host check for CSRF validation

# Configure session cookies to work across different IPs
app.config['SESSION_COOKIE_SECURE'] = False  # Allow cookies on non-HTTPS connections
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = None  # Allow cross-site cookies
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookies for any domain
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 120 minutes in seconds
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow CSRF protection on non-HTTPS connections
app.config['WTF_CSRF_TIME_LIMIT'] = 7200  # Set CSRF token timeout to 2 hours

# CSRF configuration
csrf = CSRFProtect(app)  # Initialize with app directly

# Exempt API blueprint from CSRF protection
csrf.exempt(api_bp)

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(webapp_bp)

SWAGGER_URL = F"{URL_PREFIX}/api/v1/docs"
API_URL = F"{URL_PREFIX}/static/openapi.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "ToDo list service API"},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
csrf.exempt(swaggerui_blueprint)

# Create API view endpoints array for manual exemption - make sure this comes AFTER api_bp registration
api_views = []
for rule in app.url_map.iter_rules():
    if rule.rule.startswith(f"{URL_PREFIX}/api/"):
        api_views.append(app.view_functions[rule.endpoint])

# Now initialize CSRF with app and exempt API endpoints
csrf.init_app(app)
# Exempt individual API view functions
for view in api_views:
    csrf.exempt(view)

@app.route(F"{URL_PREFIX}/")
def index():
    return redirect(url_for("webapp.todo.todo_list"))

@app.route(F"{URL_PREFIX}/debug/session", methods=["GET"])
def debug_session():
    """Debug route to check session handling"""
    
    # Set a test value in session
    session['test_value'] = 'Session is working'
    
    # Return current session data
    return jsonify({
        'session_data': dict(session),
        'cookies': dict(request.cookies),
        'csrf_token': csrf._get_csrf_token(),
        'headers': dict(request.headers)
    })

@app.route(F"{URL_PREFIX}/debug/csrf", methods=["GET"])
def debug_csrf():
    """Debug route to reset CSRF protection"""
    from flask import jsonify
    
    # Generate and set a new CSRF token
    csrf_token = csrf._get_csrf_token()
    
    # Return current token
    return jsonify({
        'new_csrf_token': csrf_token,
        'session_csrf_token': session.get('csrf_token', None),
        'session_data': dict(session),
        'cookies': dict(request.cookies)
    })

# Error handlers
@app.errorhandler(401)
def unauthorized(error):
    return render_template("errors/401.html"), 401

@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403

@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(error):
    logging.error(f"500 error: {error}", exc_info=True)
    return render_template("errors/500.html"), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    # Log detailed information for debugging
    logging.warning(f"CSRF error: {e.description}")
    logging.warning(f"Request origin: {request.headers.get('Origin')}")
    logging.warning(f"Request host: {request.host}")
    logging.warning(f"Request headers: {dict(request.headers)}")
    logging.warning(f"Request cookies: {request.cookies}")
    
    # In development mode, allow bypassing CSRF
    if os.environ.get("FLASK_ENV") == "development":
        # Generate a new CSRF token
        csrf_token = csrf._get_csrf_token()
        # Set it in the session
        session['csrf_token'] = csrf_token
        
        # If this was a login attempt, try to process it 
        if request.path == f"{URL_PREFIX}/auth/login" and request.method == "POST":
            from webapp.routes_auth import process_login
            return process_login(request)
            
    return render_template("errors/csrf_error.html"), 400


global_init()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    session = create_session()
    app.run("172.16.0.1")
