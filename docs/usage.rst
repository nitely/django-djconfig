.. _usage:

Usage
=====

Creating the config form
------------------------

.. Tip:: Form's field names must be unique across forms,
          so you should prefix them with the name of your app.

::

    # forms.py

    from djconfig.forms import ConfigForm


    class AppConfigForm(ConfigForm):

        myapp_first_key = forms.BooleanField(initial=True, required=False)
        myapp_second_key = forms.IntegerField(initial=20)

Registering the config form
---------------------------

.. Tip:: Read the django_applications_docs_

.. _django_applications_docs: https://docs.djangoproject.com/en/1.8/ref/applications/

::

    # apps.py

    from django.apps import AppConfig


    class MyAppConfig(AppConfig):

        name = 'myapp'
        verbose_name = "Myapp"

        def ready(self):
            self.register_config()
            # ...

        def register_config(self):
            import djconfig
            from .forms import MyConfigForm

            djconfig.register(MyConfigForm)

Accessing the config
--------------------

::

    from djconfig import config


    if config.myapp_first_key:
        # ...

Accessing the config within templates:

::

    # template.html

    # ...

    {% if config.myapp_first_key %}
        # ...
    {% endif %}

Editing the config values
-------------------------

::

    # views.py

    @login_required
    def config_view(request):
        if not request.user.is_superuser:
            raise Http404

        if request.method == 'POST':
            form = AppConfigForm(data=request.POST)

            if form.is_valid():
                form.save()
                return redirect('/')
        else:
            form = AppConfigForm()

        return render(request, 'app/configuration.html', {'form': form, })

Testing helpers
---------------

There is a helper similar to django's ``@override_settings`` that can be used in tests.

::

    # tests.py

    from djconfig.utils import override_djconfig

    @override_djconfig(myapp_first_key="foo", myapp_second_key="bar")
    def test_something(self):
        # ...

Calling ``djconfig.reload_maybe()`` is required when
unit testing. For example, it may be called within
the test's ``setUp`` method to run it before each test.
The middleware will call this, so it's not needed
on integration tests that make use of django's test ``Client``.

::

    # tests.py

    import djconfig

    def setUp(self):
        djconfig.reload_maybe()

Admin
-----

Register a config form into django admin.

The following example shows how to register a single form that
contains all settings:

::

    # admin.py

    import djconfig
    from .forms import AppConfigForm


    class AppConfigAdmin(djconfig.admin.ConfigAdmin):
        change_list_form = AppConfigForm


    class AppConfig(djconfig.admin.Config):
        app_label = 'djconfig'
        verbose_name_plural = 'app config'
        slug = 'appconfig'

    djconfig.admin.register(AppConfig, AppConfigAdmin)

The following example shows how to register a form in multiple apps:

::

    # myapp/admin.py

    import djconfig
    from .forms import MyAppConfigForm


    class MyAppConfigAdmin(djconfig.admin.ConfigAdmin):
        change_list_form = MyAppConfigForm


    class MyAppConfig(djconfig.admin.Config):
        app_label = 'myapp'
        verbose_name_plural = 'myapp config'
        slug = 'myappconfig'

    djconfig.admin.register(MyAppConfig, MyAppConfigAdmin)


    # myotherapp/admin.py

    import djconfig
    from .forms import MyOtherAppConfigForm


    class MyOtherAppConfigAdmin(djconfig.admin.ConfigAdmin):
        change_list_form = MyOtherAppConfigForm


    class MyOtherAppConfig(djconfig.admin.Config):
        app_label = 'myotherapp'
        verbose_name_plural = 'myotherapp config'
        slug = 'myotherappconfig'

    djconfig.admin.register(MyOtherAppConfig, MyOtherAppConfigForm)

