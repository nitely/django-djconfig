0.7.0
==================

* Add: support for `ModelMultipleChoiceField`

0.6.0
==================

* Add: support for `ImageField` and `FileField` PR #27
* Adds Django 1.11 support (no changes were required)
* Adds Django 2.0 support (no changes were required)
* Adds Python 3.6 support (no changes were required)

0.5.3
==================

* Fix: compat for new style middleware (PR #25)

0.5.2
==================

* Adds compat for new style (Django 1.10) middleware (PR #24)

0.5.1
==================

* Adds Django 1.10 support

0.5.0
==================

* Drops Django 1.7 support
* Adds Django 1.9 support
* Adds Python 3.5 support
* Remove config lazy loading
* Adds `conf.reload_maybe()` to load the config
* Adds `app.py` config
* Docs

0.4.0
==================

* No longer use django cache
* Renamed `DjConfigLocMemMiddleware` to `DjConfigMiddleware`
* `DjConfigMiddleware` is required

0.3.2
==================

* Fix to never expire keys

0.3.1
==================

* Include missing migrations in setup.py

0.3.0
==================

* Drops support for django 1.5 and 1.6 (for no special reason)
* Support for django 1.8
* Adds migrations
* Raise AttributeError if the config key/attr is not found
* Fix race condition that caused returning non existent values (None) if the config was not fully loaded
* Huge code refactor

0.2.0
==================

* Configuration is lazy loaded, now. This means the database will get queried the first time an option is accessed *(ie: `confi.my_first_key`)*
* Only `config` and `register` are available for importing from the root module *djconfig*.
