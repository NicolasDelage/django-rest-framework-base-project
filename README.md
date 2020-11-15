# heroad-django-api

#### build docker image
`docker build .`

#### build image using docker compose configuration
`docker-compose build`

#### create django project
`docker-compose run app sh -c "django-admin.py startproject app ."`

###launch django test
`docker-compose run app sh -c "python manage.py test"`

###create core app
`docker-compose run app sh -c "python manage.py startapp core"`

###make a migration
`docker-compose run app sh -c "python manage.py makemigrations core"`
