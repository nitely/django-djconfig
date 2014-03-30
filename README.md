# DjConfig

DjConfig is a Django app to store other apps configurations.

## How it works

DjConfig let you provide all the configuration variables you need by using a regular form.
Those variables are persisted in the database (one per row) and stored in the selected cache backend for later access.


## Requirements

DjConfig requires the following software to be installed:

* Python 2.7
* Django +1.5 (tested locally on 1.6)

## Configuration

Add `djconfig` to your *INSTALLED_APPS*

Add `djconfig.middleware.DjConfigMiddleware` to your *MIDDLEWARE_CLASSES* if you are planning to use LocMemCache as the cache backend

Run:

    python manage.py syncdb

## Usage

Setting your config variables:

> from djconfig.forms import ConfigForm
>
>
>
>
> class AppConfigForm(ConfigForm):
>
>
>    debug = forms.BooleanField(initial=True, required=False)
>
>    max_comments = forms.IntegerField(initial=20)

Registering your form:

> _models.py_
>
>
> import djconfig
>
> ...
>
> djconfig.register(AppConfigForm)

Accessing your config variables:

> from djconfig import config
>
>
> ...
> if config.debug:
>     ...

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