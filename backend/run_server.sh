#!/bin/bash

cp -r ./static/* /static/;

uwsgi --http 0.0.0.0:5000 --wsgi-file app.py --callable app --master