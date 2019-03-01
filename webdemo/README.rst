===========
Django-flie
===========

Django-based demo website for flie: the formal language inference engine.

============
Requirements
============

* `Django <https://www.djangoproject.com/>`__ (2.1.7+)
* `RQ <https://github.com/nvie/rq>`__ (0.13.0+), which builds upon `Redis <https://redis.io/>`__ (3.0.0+)
* `django-rq <https://github.com/rq/django-rq>`__ (1.3.0+)

============
Installation
============

* Create ``django-flie`` package:

  .. code-block:: console

    python setup.py sdist

* Install ``django-rq``:

  .. code-block:: console

    pip install django-flie-0.1.tar.gz

* Add ``django_rq`` and ``django_flie`` to ``INSTALLED_APPS`` in your site's ``settings.py``:

  .. code-block:: python

    INSTALLED_APPS = [
        # other apps
        'django_rq',
        'django_flie',
    ]

* Configure (i.e., add) a queue with name ``default`` in your site's ``settings.py``:

  .. code-block:: python

    RQ_QUEUES = {
        'default': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 0,
            'DEFAULT_TIMEOUT': 360,
        },
    }
    
* Configure (i.e., add) ``django-flie``'s custom exception handler in your site's ``settings.py``:

  .. code-block:: python

    RQ_EXCEPTION_HANDLERS = [
        'django_flie.rq_exception_handler.job_exception_handler'
    ]

* Include ``django_flie.urls`` in your site's ``urls.py``:

  .. code-block:: python

    # Django >= 2.0
    urlpatterns += [
        path('flie/', include('django_flie.urls'))
    ]
    
  You might need to import ``path`` from ``django.urls``.

    
=====
Usage
=====

1. Set up database for ``django-flie``:

  .. code-block:: console

    python ./manage.py migrate
    
2. Create one (or more) ``django-rq`` workers:

  .. code-block:: console

    python ./manage.py rqworker default

3. Run Django's webserver:

  .. code-block:: console
  
    python ./manage.py runserver
  
  and visit http://127.0.0.1:8000/flie/.
  
  Remember to never use Django's development server in a production environment.