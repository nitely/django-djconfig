# DjConfig [![Build Status](https://travis-ci.org/nitely/django-djconfig.png)](https://travis-ci.org/nitely/django-djconfig) [![Coverage Status](https://coveralls.io/repos/nitely/django-djconfig/badge.png?branch=master)](https://coveralls.io/r/nitely/django-djconfig?branch=master)

DjConfig is a Django app to store other apps configurations.

## How it works

DjConfig let you provide all the configuration variables you need by using a regular form.

Those variables are persisted in the database (one per row) and stored in the selected cache backend for later access.

## Requirements

DjConfig requires the following software to be installed:

* Python 2.7, 3.3 or 3.4 (recommended)
* Django 1.5, 1.6, 1.7

## Configuration

1. Add `djconfig` to your *INSTALLED_APPS*
2. Run `python manage.py syncdb`
3. [Set a cache backend](https://github.com/nitely/django-djconfig#backends)
4. (Optional) Add `djconfig.middleware.DjConfigLocMemMiddleware` to your *MIDDLEWARE_CLASSES* if you are using django `LocMemCache` and running multiple processes
5. (Optional) Add `djconfig.context_processors.config` to your *TEMPLATE_CONTEXT_PROCESSORS* for accessing `config` within your templates

## Usage

Setting your config variables:

```python
# forms.py

from djconfig.forms import ConfigForm


class AppConfigForm(ConfigForm):

    my_first_key = forms.BooleanField(initial=True, required=False)
    my_second_key = forms.IntegerField(initial=20)
```

Registering your form:
>**Note**: On django<=1.6 there is no good place to put startup code,
I've tried urls.py and manager.py and both of them seems to work fine.
>
> On django>=1.7 use the `AppConfig.ready()`.

```python
# urls.py

import djconfig

djconfig.register(AppConfigForm)

# ...
```

Accessing your config variables:

```python
from djconfig import config


if config.my_first_key:
    # ...
```

Accessing your config variables within your templates:
*Requires setting `djconfig.context_processors.config` or passing the `config` object to your RequestContext manually*

```python
# template.html

# ...

{% if config.my_first_key %}
    # ...
{% endif %}
```

Dynamically setting your config variables:

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

DjConfig requires a Django cache backend to be installed.

```python
# settings.py

# ...

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

To use other backend than the default, add `DJC_BACKEND = 'other'` in your *settings.py* file.

Supported backends:
* `LocMemCache`
* `Memcached`
* `Redis` (requires [django-redis-cache](https://github.com/sebleier/django-redis-cache))
* Any other memory-based cache.

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

Breaking changes:

**v0.2.x**
* Configuration is lazy loaded, now. This means the database will get queried the first time an option is accessed *(ie: `confi.my_first_key`)*
* Only `config` and `register` are available for importing from the root module *djconfig*.

## Contributing

Feel free to check out the source code and submit pull requests.

You may also report any bug or propose new features in the [issues tracker](https://github.com/nitely/django-djconfig/issues)

## Copyright / License

Copyright 2014 [Esteban Castro Borsani](https://github.com/nitely).

Licensed under the [MIT License](https://github.com/nitely/django-djconfig/blob/master/LICENSE).

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
