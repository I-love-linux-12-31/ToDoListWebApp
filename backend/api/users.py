from flask import Blueprint, jsonify, request, Response
from werkzeug.security import generate_password_hash, check_password_hash

from decorators import token_auth
from db import create_session
from ORM.users import User
from ORM.authtokens import TokensAccessLevels

bp = Blueprint('users', __name__)


@bp.route('/users', methods=['GET'])
@token_auth(allow_anonymous=False)
def get_users(token_status=None, user_id=None, session=None, **kwargs):
    """Get user(s) - regular users can only see their own data, admins can see all users"""
    if session is None:
        session = create_session()
    
    # Check if admin is requesting all users
    if token_status == TokensAccessLevels.EVERYTHING_ADMIN:
        users = session.query(User).all()
        users_data = [{"id": user.id, "username": user.username, "email": user.email, 
                      "created_at": user.created_at.isoformat(), "is_admin": user.is_admin} 
                     for user in users]
        return jsonify(users_data)
    
    # Regular user can only see their own data
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return Response("User not found", 404)
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_admin": user.is_admin
    })


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth(allow_anonymous=False)
def get_user(id, token_status=None, user_id=None, session=None, **kwargs):
    """Get a specific user - users can only see themselves, admins can see any user"""
    if session is None:
        session = create_session()
    
    # Regular users can only see their own data
    if token_status != TokensAccessLevels.EVERYTHING_ADMIN and id != user_id:
        return Response("Access denied", 403)
    
    user = session.query(User).filter_by(id=id).first()
    if not user:
        return Response("User not found", 404)
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_admin": user.is_admin
    })


@bp.route('/users', methods=['POST'])
@token_auth(allow_anonymous=False)
def create_user(token_status=None, user_id=None, session=None, **kwargs):
    """Create a new user - only admins can create users through API"""
    if token_status != TokensAccessLevels.EVERYTHING_ADMIN:
        return Response("Access denied", 403)
    
    if session is None:
        session = create_session()
    
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return Response("Missing required fields", 400)
    
    # Check if username or email already exists
    if session.query(User).filter_by(username=data['username']).first():
        return Response("Username already exists", 400)
    if session.query(User).filter_by(email=data['email']).first():
        return Response("Email already exists", 400)
    
    # Create new user
    user = User()
    user.username = data['username']
    user.email = data['email']
    user.password_hash = generate_password_hash(data['password'])
    user.is_admin = data.get('is_admin', False)
    
    session.add(user)
    session.commit()
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_admin": user.is_admin
    }), 201


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth(allow_anonymous=False)
def update_user(id, token_status=None, user_id=None, session=None, **kwargs):
    """Update user - users can update only their own data, admins can update any user"""
    if token_status != TokensAccessLevels.EVERYTHING_ADMIN and id != user_id:
        return Response("Access denied", 403)
    
    if session is None:
        session = create_session()
    
    user = session.query(User).filter_by(id=id).first()
    if not user:
        return Response("User not found", 404)
    
    data = request.get_json()
    if not data:
        return Response("No data provided", 400)
    
    # Update fields
    if 'username' in data:
        existing = session.query(User).filter_by(username=data['username']).first()
        if existing and existing.id != id:
            return Response("Username already exists", 400)
        user.username = data['username']
    
    if 'email' in data:
        existing = session.query(User).filter_by(email=data['email']).first()
        if existing and existing.id != id:
            return Response("Email already exists", 400)
        user.email = data['email']
    
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'])
    
    # Only admins can change admin status
    if 'is_admin' in data and token_status == TokensAccessLevels.EVERYTHING_ADMIN:
        user.is_admin = data['is_admin']
    
    session.commit()
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_admin": user.is_admin
    })


@bp.route('/users/<int:id>', methods=['DELETE'])
@token_auth(allow_anonymous=False)
def delete_user(id, token_status=None, user_id=None, session=None, **kwargs):
    """Delete user - only admins can delete users"""
    if token_status != TokensAccessLevels.EVERYTHING_ADMIN:
        return Response("Access denied", 403)
    
    if session is None:
        session = create_session()
    
    user = session.query(User).filter_by(id=id).first()
    if not user:
        return Response("User not found", 404)
    
    session.delete(user)
    session.commit()
    
    return Response("", 204) 