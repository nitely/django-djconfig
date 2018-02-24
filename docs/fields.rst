.. _fields:

Fields
======

Supported form fields
---------------------

The following form fields were tested:

* ``BooleanField``
* ``CharField``
* ``EmailField``
* ``FloatField``
* ``IntegerField``
* ``URLField``
* ``ChoiceField``
* ``ModelChoiceField``
* ``FileField``
* ``ImageField``

DateField is not supported at this time (sorry).

Limitations
-----------

ChoiceField
***********

The config will always return a *string*
representation of the saved value. It's up to you to coerce
it to the right type (int, float or boolean), which can be
done within the ``clean_my_field`` method.

Example::

    # forms.py

    from djconfig.forms import ConfigForm


    class AppConfigForm(ConfigForm):

        myapp_choice = forms.ChoiceField(initial=None, choices=[(1, 'label_a'), (2, 'label_b')])

    def clean_myapp_choice(self):
        # By doing this, config.myapp_choice
        # will return a int instead of a string
        return int(self.cleaned_data['myapp_choice'])


ModelChoiceField
****************

The config will always return the model
instance which is frozen in time to when the config was loaded.
If you just need the *pk*, consider returning it within the ``clean_my_field``
method.

The config will return the initial value (usually ``None``),
if the previously saved choice is ever deleted from the data base.

``to_field_name`` parameter is *not* currently supported.

Example::

    # forms.py

    from djconfig.forms import ConfigForm


    class AppConfigForm(ConfigForm):

        myapp_model_choice = forms.ModelChoiceField(initial=None, queryset=MyModel.objects.all())

    def clean_myapp_model_choice(self):
        # By doing this, config.myapp_model_choice
        # will return the model instance pk
        # instead of the model instance object
        return self.cleaned_data['myapp_model_choice'].pk

