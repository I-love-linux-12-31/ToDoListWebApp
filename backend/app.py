import os
import hashlib
import logging
from flask_swagger_ui import get_swaggerui_blueprint
from flask_wtf.csrf import CSRFProtect, CSRFError

if os.environ.get("DOTENV", False):
    from dotenv import load_dotenv
    load_dotenv()


from flask import Flask, get_flashed_messages, redirect, url_for, render_template
from db import global_init, create_session

from decorators import token_auth

from api import bp as api_bp
from webapp import bp as webapp_bp

URL_PREFIX = os.environ.get("URL_PREFIX", "")

app = Flask(__name__, static_url_path=F"{URL_PREFIX}/static")
app.secret_key = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(24)).hexdigest())

# Configure secure cookies for production
if os.environ.get("FLASK_ENV") != "development":
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=7200,  # 120 minutes in seconds
    )

# Initialize CSRF protection
csrf = CSRFProtect(app)
# Exempt the API routes from CSRF protection
csrf.exempt(api_bp)

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


@app.route(F"{URL_PREFIX}/")
def index():
    return redirect(url_for("webapp.todo.todo_list"))


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
    logging.warning(f"CSRF error: {e.description}")
    return render_template("errors/csrf_error.html"), 400


global_init()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    session = create_session()
    app.run()
