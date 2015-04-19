# -*- coding: utf-8 -*-

from __future__ import unicode_literals


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