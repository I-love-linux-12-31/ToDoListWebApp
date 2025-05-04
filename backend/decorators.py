import logging
from datetime import datetime

from ORM.authtokens import TokensAccessLevels, AuthToken
from flask import request, Response
import functools

from db import create_session

logger = logging.getLogger(__name__)

def token_auth(allow_anonymous=False):
    def decorator(func, *args, **kwargs):
        @functools.wraps(func)
        def check_token_auth(*args2, **kwargs2):
            if "token_status" in kwargs or "token_status" in kwargs2:
                return Response("Bad request!", 400)
            token_status = None
            user_id = None
            token: str = request.headers.get("Authorization")
            if not allow_anonymous and not token:
                return Response("Unauthorized", 401)
            if token is None:
                # print("[DBG] Auth passed (anonymous)")
                logger.debug("Auth passed: %s", token)
                return func(*args2, token_status=None, **kwargs2)
            split = token.split(" ")
            if len(split) != 2:
                return Response("Unauthorized: Bad token format!", 401)
            token_type, token = split
            if token_type == "Bearer":
                return Response("Unauthorized: JWT auth not supported!", 401)

            session = create_session()

            if token_type == "Token":
                # print(token)
                token: AuthToken = session.query(AuthToken).get(token)
                if token and token.valid_until >= datetime.now():
                    logger.info("Auth passed: %s", token)
                    token_status = token.access_level
                    user_id = token.user_id
                else:
                    return Response("Unauthorized: bad token!", 401)
            else:
                return Response("Unauthorized: bad token type!", 401)
            return func(*args2, token_status=token_status, user_id=user_id, session=session,**kwargs2)
        return check_token_auth
    return decorator
