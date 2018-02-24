.. _cookbook:

Cookbook
========

Image field
-----------

::

    from django.core.files.storage import default_storage
    from djconfig.forms import ConfigForm


    class ImageForm(ConfigForm):
        """Save an image"""
        image = forms.ImageField(initial=None, required=False)

        def save_image(self):
            image = self.cleaned_data.get('image')
            if image:
                # `name` may change if the storage renames the file,
                # so we update it `image.name = ...`
                image.name = default_storage.save(image.name, image)

        def save(self):
            self.save_image()
            # the image name will be saved into `conf.image`
            super(ImageForm, self).save()
