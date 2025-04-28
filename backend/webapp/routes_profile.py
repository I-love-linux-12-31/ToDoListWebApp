from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import create_session
from ORM import User
from werkzeug.security import generate_password_hash

bp_profile = Blueprint('profile', __name__, url_prefix='/profile')


def get_current_user():
    session_db = create_session()
    return session_db.query(User).get(session.get('user_id'))


@bp_profile.route('/', methods=['GET', 'POST'])
@bp_profile.route('/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id=None):
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()

    # Determine target user
    if user_id:
        if not session.get('is_admin'):
            flash('Only admin can edit other profiles.', 'danger')
            return redirect(url_for('webapp.profile.profile'))
        user = session_db.query(User).get(user_id)
    else:
        user = session_db.query(User).get(session['user_id'])

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form.get('password')

        user.username = username
        user.email = email

        if password:
            user.password_hash = generate_password_hash(password)

        session_db.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('webapp.profile.profile', user_id=user.id if session.get('is_admin') else None))

    return render_template('webapp/profile.html', user=user, is_admin=session.get('is_admin'))
