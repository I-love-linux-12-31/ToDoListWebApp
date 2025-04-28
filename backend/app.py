import os
import hashlib
from flask_swagger_ui import get_swaggerui_blueprint

if os.environ.get("DOTENV", False):
    from dotenv import load_dotenv
    load_dotenv()


from flask import Flask, get_flashed_messages
from db import global_init, create_session

from decorators import token_auth

from api import bp as api_bp
from webapp import bp as webapp_bp

URL_PREFIX = os.environ.get('URL_PREFIX', '')

app = Flask(__name__, static_url_path=F"{URL_PREFIX}/static")
app.secret_key = hashlib.sha256(os.urandom(24)).hexdigest()

app.register_blueprint(api_bp)

app.register_blueprint(webapp_bp)


SWAGGER_URL = F"{URL_PREFIX}/api/v1/docs"
API_URL = F"{URL_PREFIX}/static/openapi.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "ToDo list service API",}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


global_init()

if __name__ == '__main__':
    session = create_session()
    app.run()
