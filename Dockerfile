FROM python:3.8

RUN pip install pipenv

WORKDIR /app

COPY . /app

RUN pipenv install --system --skip-lock

RUN pip install gunicorn[gevent]

EXPOSE 5000

VOLUME ["/data"]

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info && mkdir /data