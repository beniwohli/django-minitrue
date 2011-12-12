===============
django-minitrue
===============

django-minitrue is a search & replace app for content that is stored in Django
models. You can register models and their fields and search&replace content in
the Django Admin.

Setup
=====

1. Add ``minitrue`` to ``INSTALLED_APPS``
2. Register some models. Create a file ``searchreplace.py`` in an app folder
   and register a model like this::

    from minitrue.base import replacer
    replacer.register(MyModel, fields=['title', 'description'])

