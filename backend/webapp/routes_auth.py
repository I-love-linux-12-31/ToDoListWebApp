from flask import Blueprint, render_template, request, redirect, url_for, session, flash, get_flashed_messages
# from flask_login import login_user, logout_user, login_required, current_user
from db import create_session
from ORM import User
from werkzeug.security import generate_password_hash, check_password_hash

bp_auth = Blueprint('auth', __name__, url_prefix='/auth')


@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session_db = create_session()
        username = request.form['username']
        password = request.form['password']

        if session_db.query(User).filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('webapp.auth.register'))

        user = User(username=username, password_hash=generate_password_hash(password))
        session_db.add(user)
        session_db.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('webapp.auth.login'))

    return render_template('webapp/register.html')


@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session_db = create_session()
        username = request.form['username']
        password = request.form['password']
        user = session_db.query(User).filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('webapp.auth.login'))

        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        flash('Logged in successfully', 'success')
        return redirect(url_for('webapp.todo.todo_list'))

    return render_template('webapp/login.html')


@bp_auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('webapp.auth.login'))
