# Demo Website for flie: the formal language inference engine

## Prerequisites
- redis >= 3.0.0
- python-rq >= 0.13.0
- django >= 2.1.7
- django-rq >= 1.3.0

## Setup
Follow the following steps. If neccessary, consult the documentation of the corresponding software packages for further instructions.

### 1. Create a new Django project
Create a new Django project by run the command

    django-admin startproject mysite

The following commands are relative to the root directory `./mysite/`, which is created in this process.

### 2. Copy the flie app
Copy the `flie` directory into `./mysite/`.

### 3. Prepare the Django Project
Preparing the `mysite` project requires to modify two files:

- `./mysite/mysite/settings.py`

  Register `django_rq` and `flie` as installed apps by adding the following two lines in the `INSTALLED_APPS` section:

        INSTALLED_APPS = [
          'django_rq',
          'flie.apps.FlieConfig',
          ...
        ]

  Next, register a Redis queue with name `default` by adding the following code (e.g., at the end of `settings.py`):
  
        RQ_QUEUES = {
          'default': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 0,
            'DEFAULT_TIMEOUT': 360,
          },
        }

  Finally, add `flie`'s custom exception handler by adding the following code (e.g., at the end of `settings.py`):

        RQ_EXCEPTION_HANDLERS = [
          'flie.rq_exception_handler.job_exception_handler'
        ]
- `./mysite/mysite/urls.py`

  Add `from django.urls import include` at the top of `urls.py`.
  Then, register the `flie` URLs by adding the following line to the `urlpatterns` section:
  
        urlpatterns = [
          path('flie/', include('flie.urls')),
          ...
        ]

### 4. Set up the database
Run

    python ./manage.py migrate

to let Django create the database.

### 5. Create a Django-RQ worker
Create one (or more) Django-RQ workers with the following command:

    python ./manage.py rqworker default

The argument `default` refers to the (only) Redis queue we have set up in the project.

### 6. Run Django's webserver

    python manage.py runserver

This webserver is for testing purposes only. Do not use Django's webserver in a production environment.
If everything was set up successfully, you should be able to access the website at

    http://localhost:8000/flie/
