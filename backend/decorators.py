from ORM.authtokens import TokensAccessLevels, AuthToken
from flask import request, Response

from db import create_session

def token_auth(allow_anonymous=False):
    def decorator(func, *args, **kwargs):
        def check_token_auth(*args2, **kwargs2):
            if "token_status" in kwargs or "token_status" in kwargs2:
                return Response("Bad request!", 400)
            token_status = None
            token: str = request.headers.get("Authorization")
            if not allow_anonymous and not token:
                return Response("Unauthorized", 401)
            if token is None:
                print("[DBG] Auth passed (anonymous)")
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
                if token:
                    print("[DBG] Auth passed:", token)
                    token_status = token.access_level
                else:
                    return Response("Unauthorized: bad token!", 401)

            return func(*args2, token_status=token_status, session=session,**kwargs2)
        return check_token_auth
    return decorator
