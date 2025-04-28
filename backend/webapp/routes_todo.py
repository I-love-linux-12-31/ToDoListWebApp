from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import create_session
from datetime import datetime, UTC

from tasks import get_user_tasks
from ORM import User, Task

bp_todo = Blueprint('todo', __name__, url_prefix='/todo')


def build_task_tree(tasks):
    """Build a tree structure from flat task list."""
    task_dict = {task["id"]: task for task in tasks}
    tree = []

    for task in tasks:
        print(task)
        if task.get("parent", None) is not None and task_dict.get(task["parent"], None) is not None:
            parent = task_dict.get(task["parent"])
            parent: dict
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(task)
        else:
            tree.append(task)

    return tree


@bp_todo.route("/", methods=["GET"])
def todo_list():
    if "user_id" not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])

    tasks = get_user_tasks(user.id, session_db, short_response=False, write_permission_required=False)

    tree = build_task_tree(tasks)

    return render_template('webapp/todo.html', tasks=tree, user=user, current_date=datetime.now(UTC))
