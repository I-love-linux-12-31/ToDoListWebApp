# ToDo list web application
Course work on the subject "Client-Server Application Development"

**Author: Kuznetsov Yaroslav**

## Used technologies:
* Python3
* Flask
  * Flask-login
* SQLAlchemy

Available databases:
* sqlite 
* MariaDB
* PostgreSQL

## Project structure

### Modules
* backend
  * api - API module
  * ORM - ORM models
  * tasks - some functions for operating with tasks 
  * utils - Some utils for server management (Admin user creation, etc.)
  * webapp - Web-app module 

### Files structure
```
.
├── backend
│   ├── api
│   │   ├── auth.py
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── app.py
│   ├── db.py
│   ├── decorators.py
│   ├── ORM
│   │   ├── __all_models.py
│   │   ├── authtokens.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── requirements.txt
│   ├── static
│   │   └── openapi.yaml
│   ├── tasks
│   │   ├── __init__.py
│   │   └── tasks_list.py
│   ├── templates
│   ├── utils
│   │   ├── add_user.py
│   │   └── common.py
│   ├── utils_cmd.py
│   └── webapp
│       └── __init__.py
├── DEMO_AUTH.md
├── LICENSE
├── README.md
└── README_RU.md

```
## Documentation

OpenAPI docs: 
* file - ``backend/static/openapi.yaml``
* webview - ``{URL_PREFIX}/api/v1/docs``

## About app

### Web pages

#### API

* OpenAPI docs
* Api tokens management

#### Account management:

* Login
* Registration
* Profile management

#### To-do list

* Main page
* Add task page
* Share task page


### Models

#### 1. Tasks

#### 2. Users

#### 3. AuthTokens

### Access control

In project user role based access control model.

For User model:
1) User can see only own data.
2) Admins can change user's data.

For Task model:
1) Anonymous can see shared tasks (But only for reading).
2) User can modify own tasks and shared tasks(if got write access)
3) Admin can operate with all tasks.

