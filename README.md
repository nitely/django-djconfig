# DjConfig [![Build Status](https://travis-ci.org/nitely/django-djconfig.png)](https://travis-ci.org/nitely/django-djconfig) [![Coverage Status](https://coveralls.io/repos/nitely/django-djconfig/badge.png?branch=master)](https://coveralls.io/r/nitely/django-djconfig?branch=master)

## How it works

Set the config values using a regular form.
Those values are persisted in the database (one per row)
and stored in an in-memory cache for later access.

## Requirements

* Python 2.7, 3.3 or 3.4 (recommended)
* Django 1.7, 1.8

## Installing

1. Add `djconfig` to `INSTALLED_APPS`
2. Run `python manage.py migrate`
3. [Set a cache backend](https://github.com/nitely/django-djconfig#backends)
4. (Optional) Add `djconfig.middleware.DjConfigLocMemMiddleware` to `MIDDLEWARE_CLASSES` if you are using django `LocMemCache`
5. (Optional) Add `djconfig.context_processors.config` to `TEMPLATE_CONTEXT_PROCESSORS` to access the `config` within your templates

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
*Requires setting `djconfig.context_processors.config` or passing the `config` object to your RequestContext manually*

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

## Backends

An *in-memory* cache is required.

```python
# settings.py

# ...

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

To use other backend than the default, add `DJC_BACKEND = 'my_backend'` in your *settings.py* file.

Supported backends:
* `LocMemCache`
* `Memcached`
* `Redis` (requires [django-redis-cache](https://github.com/sebleier/django-redis-cache))
* Any other in-memory cache.

>**Note**: When using `LocMemCache` you must add `djconfig.middleware.DjConfigLocMemMiddleware` to your *MIDDLEWARE_CLASSES*.
>
>This will make cross-process caching possible. Not really, but it will reload the cache on every request by quering the database.

## Supported form fields

The following form fields were tested: `BooleanField`, `CharField`, `EmailField`, `FloatField`, `IntegerField`, `URLField`.

Fields that return complex objects are not supported. Basically any object that can be store in a data base is supported, except for DateField which is not supported at this time (sorry).

## Testing

Add `LOCATION` to your cache so you can call `cache.clear()` to clear all your caches but the DjConfig one.

Usage:
```python
CACHES = {
    'default': {
        # ...
    },
    'djconfig': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-djconfig',
    },
}
```

## Testing helpers

DjConfig comes with a helper similar to django's `@override_settings` you can use in tests.

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