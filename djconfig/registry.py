# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings as django_settings

from .settings import BACKEND

_registered_forms = set()


def register(form_class):
    """
    Register config forms

    :param form_class: The form to be registered.
    :type form_class: ConfigForm.
    """
    from . import forms  # avoids circular dependency

    global _registered_forms

    assert issubclass(form_class, forms.ConfigForm), \
        "The form does not inherit from ConfigForm"

    _registered_forms.add(form_class)
    _check_backend()


def _check_backend():
    if django_settings.CACHES[BACKEND]['BACKEND'].endswith(".LocMemCache") and \
            "djconfig.middleware.DjConfigLocMemMiddleware" not in django_settings.MIDDLEWARE_CLASSES:
        raise ValueError("LocMemCache requires DjConfigLocMemMiddleware "
                         "but it was not found in MIDDLEWARE_CLASSES")
