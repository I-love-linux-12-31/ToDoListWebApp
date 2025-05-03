#!/bin/bash

mkdir -p /static/todo-app/static/ || true
# cp -r ./static/* /static/;
cp -r ./static/* /todo-app/static/ || true


uwsgi --plugin http --http 0.0.0.0:5000 --plugin python3 --wsgi-file app.py --callable app --master --ini uWSGI.ini
