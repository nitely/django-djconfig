.. _cookbook:

Cookbook
========

Save an image
-------------

::

    from django import forms
    from django.core.files.storage import default_storage
    from djconfig.forms import ConfigForm


    class MyImageForm(ConfigForm):
        """
            Save an image

            Usage ::

                # on POST, files must be passed
                form = MyImageForm(data=request.POST, files=request.FILES)
                if form.is_valid():
                    form.save()
                    return redirect('/')

        """

        myapp_image = forms.ImageField(initial=None, required=False)

        def save_image(self):
            image = self.cleaned_data.get('myapp_image')
            if image:
                # `name` may change if the storage renames the file,
                # so we update it `image.name = ...`
                image.name = default_storage.save(image.name, image)

        def save(self):
            self.save_image()
            # the image name will be saved into `conf.myapp_image`
            super(MyImageForm, self).save()
