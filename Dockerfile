#FROM python:3.8-slim-buster
##FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
#WORKDIR /app
#
#COPY . /app
#
#ENV STATIC_URL /static
#ENV STATIC_PATH /var/www/app/static
#
##RUN apt-get -y update
#RUN pip3 install -r requirements.txt
#RUN pip install uwsgi==2.0.17
#
##EXPOSE 5000
#
##CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
#CMD [ "python3", "app.py"]
##CMD ["uwsgi --ini uwsgi.ini"]
FROM python:3.8-slim-buster

RUN pip install pipenv

COPY . /flask-deploy

WORKDIR /flask-deploy

RUN pipenv install --system --skip-lock

RUN pip install gunicorn[gevent]

EXPOSE 5000

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info