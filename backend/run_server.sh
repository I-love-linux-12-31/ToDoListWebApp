#!/bin/bash

mkdir -p /static/todo-app/static/ || true
# cp -r ./static/* /static/;
cp -r ./static/* /todo-app/static/ || true
if [ -f "/usr/bin/python3.14t" ]; then
  uwsgi --plugin http --http 0.0.0.0:5000 --plugin python3 --wsgi-file app.py --callable app --master --ini uWSGI.ini
else
  # used default python3
  uwsgi --plugin http --http 0.0.0.0:5000 --plugin python3 --wsgi-file app.py --callable app --master
fi
