0.3.0
==================

* Drops support for django 1.5 and 1.6 (for no special reason)
* Support for django 1.8
* Adds migrations
* Raise AttributeError if the config key/attr is not found
* Fix race condition that caused returning non existent values (None) if the config was not fully loaded
* Huge code refactor