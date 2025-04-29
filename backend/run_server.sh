#!/bin/bash

cp -r ./static/* /static/;

uwsgi --plugin http --http 0.0.0.0:5000 --plugin python3 --wsgi-file app.py --callable app --master
