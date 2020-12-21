# django-rest-framework-base-project

This is a base django rest framework comes with docker everything we need to have fun!

##Features
By default, this project structure includes:

Python:

- python:3.7-alpine

DB Postgres:

- postgres:10-alpine

Requirements:

- Django>=3.1.3,<3.1.4
- djangorestframework>=3.12.2,<3.12.3
- psycopg2>=2.7.5,<2.8.0
- flake8>=3.6.0,<3.7.0
- Pillow>=5.3.0,<5.4.0
- django-filter>=2.4.0
- django-cors-headers>=3.6.0

Core app:

- Defining and testing default user model
- Waiting for db command

User app:

- Defining and testing user and token views/serializers 

##Example of some docker commands:
Build docker image
- `docker build .`

Build image using docker compose configuration
- `docker-compose build`

Run docker container
- `docker-compose up`
- `docker-compose down`

Execute python commands
- `docker-compose run app sh -c "<command>"`
