FROM python:3.10-bullseye

#change working directory
WORKDIR /usr/src/django

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

# copy requirements
COPY requirements.txt /usr/src/django/requirements.txt

RUN apt-get update && apt-get install -y build-essential
RUN pip install --upgrade pip

# install required packages
RUN pip install -r requirements.txt

RUN mkdir /var/log/odoo \
    && touch /var/log/odoo/gunicorn-error.log \
    && touch /var/log/odoo/gunicorn-access.log

# copy project
COPY . /usr/src/django/

## Launch the wait tool to wait for postgres to be up (check-compose)
CMD /wait

# run entrypoint.sh
ENTRYPOINT ["sh","/usr/src/django/entrypoint.sh"]

# for security reasons the user that will run
# our software will be user and not root
# RUN adduser --disabled-login --gecos "" user
# USER user