#wagtailjobs


A plugin for Wagtail that provides job functionality
[Documentation on ReadTheDocs](https://wagtailjobs.readthedocs.org/en/latest/)
##Installing


Install using pip
```
pip install wagtailjobs
```
It works with Wagtail 1.0b2 and upwards.

##Using

Create job models for your application that inherit from the relevant `wagtailjobs` models:

``` python

    from django.db import models

    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailcore.fields import RichTextField
    from wagtail.wagtailcore.models import Page

    from wagtailjobs.models import jobIndexMixin, Abstractjob
    from wagtailjobs.decorators import jobindex


    # The decorator registers this model as a job index
    @jobindex
    class jobIndex(jobIndexMixin, Page):
        # Add extra fields here, as in a normal Wagtail Page class, if required
        job_model = 'job'


    class job(Abstractjob):
        # job is a normal Django model, *not* a Wagtail Page.
        # Add any fields required for your page.
        # It already has ``date`` field, and a link to its parent ``jobIndex`` Page
        full_name = models.CharField(max_length=255)
        organization = models.CharField(max_length=255)
        phone_number = models.CharField(max_length=255)
        

        panels = [
            FieldPanel('full_name', classname='full'),
            FieldPanel('organization'),
            FieldPanel('phone_number')
        ] + Abstractjob.panels

        def __unicode__(self):
            return self.full_name
```