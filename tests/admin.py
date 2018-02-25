# -*- coding: utf-8 -*-

import djconfig

from .tests import FooForm


class FooAdmin(djconfig.admin.ConfigAdmin):

    change_list_form = FooForm

djconfig.admin.register(FooAdmin)
