FROM python:3.7-alpine
MAINTAINER Nicolas Delage

ENV PYTHONUNBUFFERED 1

#copy local requirements.txt into the docker container
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#create app folder
RUN mkdir /app
#define app folder as the work directory
WORKDIR /app
#copy local app folder into the docker container
COPY ./app /app

#create user "user"
RUN adduser -D user
#define "user" as the actual user
USER user