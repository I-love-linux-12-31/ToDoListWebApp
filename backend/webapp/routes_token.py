import hashlib
import random
from datetime import datetime, UTC

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import create_session
from ORM import User, AuthToken
from ORM.authtokens import TokensAccessLevels

bp_token = Blueprint('token', __name__, url_prefix='/token')


@bp_token.route('/', methods=['GET', 'POST'])
def token():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])

    tokens = session_db.query(AuthToken).filter(AuthToken.user_id == user.id).all()
    tokens_data_list = [t.serialize_from_object() for t in tokens]
    for i, t in enumerate(tokens):
        tokens_data_list[i]["access_level"] = F"{str(t.access_level).split('.')[1]} ({tokens_data_list[i]['access_level']})" # TokensAccessLevels.id_by_level(t.access_level)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            valid_until = request.form.get('valid_until')
            access_level = request.form.get('access_level')

            token_ok = True
            if (datetime.fromisoformat(valid_until) - datetime.now(UTC)).days > 120:
                flash('Maximum duration of token 120 days!', 'warning')
                token_ok = False
            if not access_level.isdigit():
                flash('Unacceptable access level. id required.', 'danger')
                token_ok = False
            else:
                access_level = int(access_level)
                if access_level > 4 or access_level < 0:
                    flash('Invalid access level', 'warning')
                    token_ok = False
                if not user.is_admin and access_level == 4:
                    flash('Access denied', 'danger')
                    token_ok = False
            if token_ok:
                token_obj = AuthToken()
                token_obj.id = hashlib.blake2s(
                    F"{user.username}-{datetime.now(UTC).isoformat()}-{random.randint(0, 128)}".encode("utf-8")
                ).hexdigest()
                token_obj.access_level = TokensAccessLevels.level_by_id(access_level)
                token_obj.user_id = user.id
                token_obj.valid_until = datetime.fromisoformat(valid_until)
                try:
                    session_db.add(token_obj)
                    session_db.commit()
                    flash(F"Token {token_obj.id} created!", 'success')
                except Exception as e:
                    print(e)
                    flash('Failed to create token', 'danger')

        return redirect(url_for('webapp.token.token'))

    return render_template('webapp/token.html', user=user, tokens=tokens_data_list)

@bp_token.route('/revoke/<string:token_id>', methods=['GET', ])
def revoke(token_id):
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])
    _token = session_db.query(AuthToken).get(token_id)
    if not _token:
        flash('Token not found (Or already deleted).', 'danger')
    else:
        if user.id != _token.user_id and not user.is_admin:
            flash('Access denied!', 'danger')
        else:
            session_db.delete(_token)
            session_db.commit()
            flash(F"Token {token_id} deleted.", 'success')
    session_db.close()
    return redirect(url_for("webapp.token.token"))
