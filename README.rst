===============
django-minitrue
===============

django-minitrue is a search & replace app for content that is stored in Django
models. You can register models and their fields and search&replace content in
the Django Admin.

Setup
=====

1. Add ``'minitrue'`` to ``INSTALLED_APPS``
2. Register some models. Create a file ``searchreplace.py`` in an app folder
   and register a model like this::

    from minitrue.base import replacer
    replacer.register(MyModel, fields=['title', 'description'])


Included Replacers
==================

django-minitrue comes with a number of replacers for 3rd party Django packages.
Add them to ``INSTALLED_APPS`` to activate them.

 * `django CMS`_: ``'minitrue.contrib.django_cms'``
 * `django-filer`_: ``'minitrue.contrib.django_filer',``
 * `django-simplegallery`_: ``'minitrue.contrib.django_simplegallery',``


.. _django CMS: http://www.django-cms.org
.. _django-filer: http://readthedocs.org/docs/django-filer/
.. _django-simplegallery: https://github.com/divio/django-simplegallery

