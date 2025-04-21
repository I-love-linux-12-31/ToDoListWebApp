import hashlib
import random
from datetime import datetime, timedelta, UTC
from flask import Blueprint, jsonify, request, Response
from werkzeug.security import generate_password_hash, check_password_hash

from db import create_session
from decorators import token_auth

from ORM.users import User
from ORM.authtokens import AuthToken, TokensAccessLevels

bp = Blueprint('auth', __name__)

@bp.route('/token/create', methods=['POST'])
@token_auth(allow_anonymous=True)
def create_token(session=None, **kwargs):
    request_data = request.get_json()
    username = request_data.get('username', None)
    password = request_data.get('password', None)
    token_access_level = request_data.get('token_access_level', None)
    access_level = TokensAccessLevels.level_by_id(token_access_level)
    duration = min(request_data.get('duration', 30), 120)

    session = session or create_session()
    user = session.query(User).filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return Response('Access denied!', 403)

    if access_level == TokensAccessLevels.EVERYTHING_ADMIN and not user.is_admin:
        return Response('Access denied!', 403)
    token = AuthToken()
    token.id = hashlib.blake2s(
        F"{username}-{datetime.now(UTC).isoformat()}-{random.randint(0, 128)}".encode("utf-8")
    ).hexdigest()

    token.user_id = user.id
    token.access_level = access_level
    token.valid_until = datetime.now(UTC) + timedelta(hours=1, days=duration)
    token_serialized = token.serialize_from_object()
    session.add(token)
    session.commit()
    session.close()

    res = jsonify(token_serialized)
    res.status_code = 201
    return res
    # password_hash = generate_password_hash

@bp.route('token/revoke', methods=['DELETE'])
@token_auth(allow_anonymous=False)
def revoke_token(session=None, token_status:TokensAccessLevels=None, **kwargs):
    if token_status is None or token_status < TokensAccessLevels.EVERYTHING_USER:
        return Response('Access denied!', 403)
    request_data = request.get_json()
    username = request_data.get('username', None)
    token = request_data.get('token', None)
    if token is None:
        return Response("Bad request!, token in request body is missing", 400)
    token = token.split()[1]
    if session is None:
        session = create_session()

    user_obj = session.query(User).filter_by(username=username).first()
    if user_obj is None:
        return Response('Access denied!', 403)
    token_obj: AuthToken = session.query(AuthToken).filter_by(id=token, user_id=user_obj.id).first()
    session.delete(token_obj)
    session.commit()
    session.close()
    return Response("", 204)

