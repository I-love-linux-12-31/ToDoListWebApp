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
* PostgreSQL (used as default in containerized version)

## How to run

### Superfast

1. Download docker-compose configuration
2. Download example .env file
3. Launch docker-compose (If first launch, wait 15-30 seconds and restart backend container or all)
 
```bash
wget https://raw.githubusercontent.com/I-love-linux-12-31/ToDoListWebApp/refs/heads/main/docs/docker-compose-fast-deploy.yaml -O docker-compose.yaml
wget https://raw.githubusercontent.com/I-love-linux-12-31/ToDoListWebApp/refs/heads/main/example.env -O .env
docker-compose up
```

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
│   ├── Dockerfile
│   ├── forms
│   │   ├── __init__.py
│   │   └── token_create.py
│   ├── ORM
│   │   ├── __all_models.py
│   │   ├── authtokens.py
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── run_server.sh
│   ├── static
│   │   ├── main.css
│   │   └── openapi.yaml
│   ├── tasks
│   │   ├── __init__.py
│   │   └── tasks_list.py
│   ├── templates
│   │   ├── base.html
│   │   └── webapp
│   │       ├── add_task.html
│   │       ├── login.html
│   │       ├── profile.html
│   │       ├── register.html
│   │       ├── share_task.html
│   │       ├── todo.html
│   │       └── token.html
│   ├── utils
│   │   ├── add_user.py
│   │   └── common.py
│   ├── utils_cmd.py
│   ├── uWSGI.ini
│   └── webapp
│       ├── __init__.py
│       ├── routes_auth.py
│       ├── routes_profile.py
│       ├── routes_todo.py
│       └── routes_token.py
├── DEMO_AUTH.md
├── docker-compose.yml
├── docs
│   ├── docker-compose-fast-deploy.yaml
│   ├── openapi.yaml -> ../backend/static/openapi.yaml
│   └── README_RU.md
├── example.env
├── LICENSE
├── nginx
│   ├── 00-to-do-list.conf
│   └── Dockerfile
└── README.md


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

