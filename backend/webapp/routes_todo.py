from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from ORM.tasks import TaskShareLevel
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


@bp_todo.route("/", methods=["GET", "POST"])
def todo_list():
    if "user_id" not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])

    if request.method == "POST":
        form = request.form
        if all([key in form for key in ["title", "description", "status", "task_id"]]):
            is_data_valid = False
            try:
                task_id = int(form["task_id"])
                description = form["description"]
                status = form["status"].upper()
                title = form["title"]
                is_data_valid = True
            except Exception as e:
                print(e)
                flash('Please enter a valid data.', 'warning')
            if is_data_valid:
                task = session_db.query(Task).get(task_id)
                task: Task
                if task.owner_id == user.id or task.writable():
                    task.title = title
                    task.description = description
                    task.status = status
                    try:
                        session_db.add(task)
                        session_db.commit()
                    except Exception as e:
                        print(e)
                        flash('Failed to update task. Something went wrong.', 'danger')

                else:
                    flash('Access denied.', 'warning')

    tasks = get_user_tasks(user.id, session_db, short_response=False, write_permission_required=False)

    tree = build_task_tree(tasks)

    return render_template('webapp/todo.html', tasks=tree, user=user, current_date=datetime.now(UTC))


@bp_todo.route("/add/<int:parent_id>", methods=["GET", "POST"])
def add_task(parent_id):
    if "user_id" not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])
    parent_task = session_db.query(Task).get(parent_id)

    if not parent_task:
        flash('Parent task not found.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    if not parent_task.writable and parent_task.owner_id != user.id and not user.is_admin:
        flash('You do not have permission to add subtasks here.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        deadline = request.form.get('deadline')

        new_task = Task()
        new_task.title = title
        new_task.description = description
        new_task.creation_date = datetime.now()
        new_task.parent = parent_task.id
        new_task.owner_id = user.id
        new_task.status = "PENDING"
        # new_task.writable = True  # New tasks created by user are writable

        if deadline:
            try:
                new_task.deadline = datetime.fromisoformat(deadline)
            except ValueError:
                flash('Invalid deadline format. Ignored.', 'warning')

        session_db.add(new_task)
        session_db.commit()

        flash('Subtask created successfully!', 'success')
        return redirect(url_for('webapp.todo.todo_list'))

    return render_template('webapp/add_task.html', parent_task=parent_task)



@bp_todo.route("/add/", methods=["GET", "POST"])
def add_root_task():
    if "user_id" not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        deadline = request.form.get('deadline')

        new_task = Task()
        new_task.title = title
        new_task.description = description
        new_task.creation_date = datetime.now()
        new_task.parent = None
        new_task.owner_id = user.id
        new_task.status = "PENDING"

        if deadline:
            try:
                new_task.deadline = datetime.fromisoformat(deadline)
            except ValueError:
                flash('Invalid deadline format. Ignored.', 'warning')

        session_db.add(new_task)
        session_db.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('webapp.todo.todo_list'))

    return render_template('webapp/add_task.html', parent_task=None)


@bp_todo.route("/delete/<int:task_id>", methods=["GET", "POST"])
def delete_task(task_id):
    if "user_id" not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])
    task = session_db.query(Task).get(task_id)

    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    if task.owner_id != user.id and not user.is_admin:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    session_db.delete(task)
    session_db.commit()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('webapp.todo.todo_list'))


@bp_todo.route("/share/<int:task_id>", methods=["GET", "POST"])
def share_task(task_id):
    if "user_id" not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('webapp.auth.login'))

    session_db = create_session()
    user = session_db.query(User).get(session['user_id'])
    task = session_db.query(Task).get(task_id)

    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    if task.owner_id != user.id and not user.is_admin:
        flash('You do not have permission to share this task.', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    if request.method == "POST":

        share_level = request.form.get('access_level')
        bad_level = True
        if share_level.isdigit() or share_level.startswith("-") and share_level[1:].isdigit():
            bad_level = False
        if bad_level:
            flash('Unacceptable access level. id required.', 'danger')
            return redirect(url_for('webapp.todo.todo_list'))
        share_level = TaskShareLevel.int2level(int(share_level))
        if TaskShareLevel.level2int(share_level) == 0:
            flash('Invalid level. Sharing stopped.', 'warning')
            return redirect(url_for('webapp.todo.todo_list'))
        # TODO: implement recursive access changed (for children)
        task.access_politics = share_level
        try:
            session_db.add(task)
            session_db.commit()
            flash(f'Task shared.', 'success')
        except Exception as e:
            print(e)
            flash('Failed to share this task!', 'danger')
        return redirect(url_for('webapp.todo.todo_list'))

    return render_template('webapp/share_task.html', task=task)
