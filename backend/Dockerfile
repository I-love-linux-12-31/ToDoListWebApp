FROM fedora:latest
LABEL authors="Yaroslav Kuznetsov"

WORKDIR /app

RUN dnf install python3-pip python3.14 python3.14-freethreading python3.14-libs python3-flask python3-flask-login postgresql python3-psycopg2 python3-dotenv python3-pyyaml python3-werkzeug python3-sqlalchemy "python3-sqlalchemy+postgresql" -y
RUN dnf install uwsgi-plugin-python3 uwsgi-router-http uwsgi -y
COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

# RUN pip3 install uwsgi


COPY . .

CMD ["bash", "run_server.sh"]
