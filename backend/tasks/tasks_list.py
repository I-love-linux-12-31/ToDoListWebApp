from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import or_
from ORM.tasks import Task, TaskShareLevel, TaskStatus
from ORM.users import User

def get_user_tasks(
    user_id: int,
    session: Session,
    write_permission_required: bool = False,
    filter_user: int = None,
    filter_status: str = None,
    filter_search: str = None,
    short_response: bool = True,

) -> int or [{str: Any, }, ]:
    """
Function to search user's tasks
    :param user_id: ID of request sender
    :param session: DB session
    :param write_permission_required: filter access by user's write permission
    :param filter_user: Search other user's tasks (Admin user only)
    :param filter_status: Filter by status
    :param filter_search: Search of string in title and description
    :param short_response: Is all fields of Task class required.
    :return: Int error code or serialized response(list of dicts).
    """
    user = session.query(User).filter_by(id=user_id).first()
    if not filter_user:
        filter_user = user
    else:
        if not user.is_admin:
            return 403
        filter_user =  session.query(User).filter_by(id=filter_user).first()


    query = session.query(Task).filter(Task.owner_id == filter_user)

    if filter_status:
        query = query.filter(Task.status == TaskStatus[filter_status])

    if filter_search:
        query = query.filter(
            or_(
                Task.title.ilike(f'%{filter_search}%'),
                Task.description.ilike(f'%{filter_search}%')
            )
        )

    if write_permission_required:
        query = query.filter(Task.access_politics.in_([
            TaskShareLevel.RW_ALL,
            TaskShareLevel.RW_ONLY_1_LEVELS,
            TaskShareLevel.RW_ONLY_2_LEVELS
        ]))
    else:
        query = query.filter(Task.access_politics.in_([
            TaskShareLevel.R_ALL,
            TaskShareLevel.R_ONLY_1_LEVELS,
            TaskShareLevel.R_ONLY_2_LEVELS,
            # TaskShareLevel.PARENT_SELECT
        ]))

    if short_response:
        query = query.with_entities(Task.id, Task.title, Task.status)
    else:
        query = query.with_entities(Task.id, Task.title, Task.description, Task.status, Task.creation_date, Task.deadline)

    if filter_user is not None:
        query = query.filter(Task.owner_id == filter_user)

    tasks = query.all()

    result = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "status": task.status.name
        }
        if not short_response:
            task_dict.update({
                "description": task.description,
                "creation_date": task.creation_date,
                "deadline": task.deadline
            })
        result.append(task_dict)

    return result
