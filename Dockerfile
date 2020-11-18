FROM python:3.7-alpine
MAINTAINER Nicolas Delage

ENV PYTHONUNBUFFERED 1

#copy local requirements.txt into the docker container
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

#create app folder
RUN mkdir /app
#define app folder as the work directory
WORKDIR /app
#copy local app folder into the docker container
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
#create user "user"
RUN adduser -D user
#change the owner of vol directory and childs directories
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
#define "user" as the actual user
USER user