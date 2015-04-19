# DjConfig [![Build Status](https://travis-ci.org/nitely/django-djconfig.png)](https://travis-ci.org/nitely/django-djconfig) [![Coverage Status](https://coveralls.io/repos/nitely/django-djconfig/badge.png?branch=master)](https://coveralls.io/r/nitely/django-djconfig?branch=master)

## How it works

Set the config values using a regular form.
Those values are persisted in the database (one per row)
and stored in an in-memory cache for later access.

## Requirements

* Python 2.7, 3.3 or 3.4 (recommended)
* Django 1.7, 1.8

## Installing

1. `pip install django-djconfig`
2. Add `djconfig` to `INSTALLED_APPS`
3. Add `djconfig.middleware.DjConfigMiddleware` to `MIDDLEWARE_CLASSES`
4. Add `djconfig.context_processors.config` to `TEMPLATE_CONTEXT_PROCESSORS`
5. Run `python manage.py migrate`

## Usage

Creating the config form:

```python
# forms.py

from djconfig.forms import ConfigForm


class AppConfigForm(ConfigForm):

    my_first_key = forms.BooleanField(initial=True, required=False)
    my_second_key = forms.IntegerField(initial=20)
```

Registering the config form:

Read the [django applications doc](https://docs.djangoproject.com/en/1.8/ref/applications/)

```python
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
```

Accessing the config:

```python
from djconfig import config


if config.my_first_key:
    # ...
```

Accessing the config within templates:

```python
# template.html

# ...

{% if config.my_first_key %}
    # ...
{% endif %}
```

Editing the config values:

```python
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
```

## Supported form fields

The following form fields were tested: `BooleanField`, `CharField`,
`EmailField`, `FloatField`, `IntegerField`, `URLField`.

Fields that return complex objects are not supported.
Basically any object that can be store in a data base is supported,
except for DateField which is not supported at this time (sorry).


## Testing helpers

There is a helper similar to django's `@override_settings` that can be used in tests.

Usage:
```python
from djconfig.utils import override_djconfig

@override_djconfig(my_first_key="foo", my_second_key="bar")
def test_something(self):
    # ...
```

## Limitations

* Although you can register several forms, field names must be unique across forms.

## Changelog

[changelog](https://github.com/nitely/django-djconfig/blob/master/HISTORY.md)

## License

MIT