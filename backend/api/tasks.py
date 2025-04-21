from datetime import datetime, timedelta, UTC
from flask import Blueprint, jsonify, request, Response

from decorators import token_auth
from db import create_session
from ORM.users import User
from ORM.tasks import Task, TaskShareLevel, TaskStatus
from ORM.authtokens import TokensAccessLevels

from tasks import get_user_tasks

bp = Blueprint('tasks', __name__)


@bp.route('/tasks', methods=['GET'])
@token_auth(allow_anonymous=False)
def list_tasks(session=None, token_status=None, user_id=None, **kwargs):
    if session is None:
        session = create_session()
    # todo: move params from URL to request body!
    tasks = get_user_tasks(user_id, session=session, **kwargs)

    session.close()
    return jsonify(tasks)


@bp.route('/tasks/<int:id>', methods=['GET'])
@token_auth(allow_anonymous=True)
def get_task(id, session=None, token_status=None, user_id=None, **kwargs):
    """Get a specific task"""
    if session is None:
        session = create_session()

    task = session.query(Task).filter_by(id=id).first()
    if not task:
        return Response("Task not found", 404)

    # Check permission
    if token_status is None:
        # Anonymous user - can only see shared tasks
        if task.access_politics not in [
            TaskShareLevel.R_ALL,
            TaskShareLevel.R_ONLY_1_LEVELS,
            TaskShareLevel.R_ONLY_2_LEVELS,
            TaskShareLevel.RW_ALL,
            TaskShareLevel.RW_ONLY_1_LEVELS,
            TaskShareLevel.RW_ONLY_2_LEVELS
        ]:
            return Response("Access denied", 403)
    elif token_status != TokensAccessLevels.EVERYTHING_ADMIN and task.owner_id != user_id:
        # Non-admin user trying to access another user's private task
        if task.access_politics == TaskShareLevel.PRIVATE:
            return Response("Access denied", 403)

    task_data = {
        "id": task.id,
        "owner_id": task.owner_id,
        "parent": task.parent,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "access_politics": task.access_politics.name,
        "creation_date": task.creation_date.isoformat(),
        "deadline": task.deadline.isoformat() if task.deadline else None
    }

    return jsonify(task_data)


@bp.route('/tasks', methods=['POST'])
@token_auth(allow_anonymous=False)
def create_task(session=None, token_status=None, user_id=None, **kwargs):
    """Create a new task"""
    if token_status is None or token_status < TokensAccessLevels.READ_CREATE:
        return Response("Access denied - insufficient permissions", 403)

    if session is None:
        session = create_session()

    data = request.get_json()
    if not data or 'title' not in data:
        return Response("Missing required fields", 400)

    task = Task()
    task.owner_id = user_id
    task.title = data.get('title')
    task.description = data.get('description')

    if 'status' in data and data['status'] in [status.value for status in TaskStatus]:
        task.status = TaskStatus(data.get('status'))
    else:
        task.status = TaskStatus.NONE

    if 'access_politics' in data and data['access_politics'] in [level.name for level in TaskShareLevel]:
        task.access_politics = TaskShareLevel[data.get('access_politics')]
    else:
        task.access_politics = TaskShareLevel.PRIVATE

    if 'parent' in data:
        task.parent = data.get('parent')

    if 'deadline' in data:
        try:
            task.deadline = datetime.fromisoformat(data.get('deadline'))
        except ValueError:
            return Response("Invalid date format for deadline", 400)

    session.add(task)
    session.commit()

    task_data = {
        "id": task.id,
        "owner_id": task.owner_id,
        "parent": task.parent,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "access_politics": task.access_politics.name,
        "creation_date": task.creation_date.isoformat(),
        "deadline": task.deadline.isoformat() if task.deadline else None
    }

    return jsonify(task_data), 201


@bp.route('/tasks/<int:id>', methods=['PUT'])
@token_auth(allow_anonymous=False)
def update_task(id, session=None, token_status=None, user_id=None, **kwargs):
    """Update a task"""
    if token_status is None:
        return Response("Authentication required", 401)

    if session is None:
        session = create_session()

    task = session.query(Task).filter_by(id=id).first()
    if not task:
        return Response("Task not found", 404)

    # Check permission
    if token_status != TokensAccessLevels.EVERYTHING_ADMIN and task.owner_id != user_id:
        # Check if the task is shared with write access
        if task.access_politics not in [
            TaskShareLevel.RW_ALL,
            TaskShareLevel.RW_ONLY_1_LEVELS,
            TaskShareLevel.RW_ONLY_2_LEVELS
        ]:
            return Response("Access denied", 403)

    data = request.get_json()
    if not data:
        return Response("No data provided", 400)

    # Update fields
    if 'title' in data:
        task.title = data.get('title')

    if 'description' in data:
        task.description = data.get('description')

    if 'status' in data and data['status'] in [status.value for status in TaskStatus]:
        task.status = TaskStatus(data.get('status'))

    # Only owner or admin can change access politics
    if 'access_politics' in data and (token_status == TokensAccessLevels.EVERYTHING_ADMIN or task.owner_id == user_id):
        if data['access_politics'] in [level.name for level in TaskShareLevel]:
            task.access_politics = TaskShareLevel[data.get('access_politics')]

    if 'parent' in data:
        task.parent = data.get('parent')

    if 'deadline' in data:
        try:
            task.deadline = datetime.fromisoformat(data.get('deadline'))
        except ValueError:
            return Response("Invalid date format for deadline", 400)

    session.commit()

    task_data = {
        "id": task.id,
        "owner_id": task.owner_id,
        "parent": task.parent,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "access_politics": task.access_politics.name,
        "creation_date": task.creation_date.isoformat(),
        "deadline": task.deadline.isoformat() if task.deadline else None
    }

    return jsonify(task_data)


@bp.route('/tasks/<int:id>', methods=['DELETE'])
@token_auth(allow_anonymous=False)
def delete_task(id, session=None, token_status=None, user_id=None, **kwargs):
    """Delete a task"""
    if token_status is None:
        return Response("Authentication required", 401)

    if session is None:
        session = create_session()

    task = session.query(Task).filter_by(id=id).first()
    if not task:
        return Response("Task not found", 404)

    # Check permission
    if token_status != TokensAccessLevels.EVERYTHING_ADMIN and task.owner_id != user_id:
        return Response("Access denied", 403)

    session.delete(task)
    session.commit()

    return Response("", 204)
