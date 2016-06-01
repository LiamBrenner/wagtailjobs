from __future__ import absolute_import, unicode_literals, print_function

import os
import StringIO

from six import string_types, text_type

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.utils.text import slugify
from uuidfield import UUIDField
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.wagtailsearch import index
from wagtail.wagtailsearch.backends import get_search_backend
from xhtml2pdf import pisa

from .views import frontend

JOBINDEX_MODEL_CLASSES = []
_JOBINDEX_CONTENT_TYPES = []


def get_jobindex_content_types():
    global _JOBINDEX_CONTENT_TYPES
    if len(_JOBINDEX_CONTENT_TYPES) != len(JOBINDEX_MODEL_CLASSES):
        _JOBINDEX_CONTENT_TYPES = [
            ContentType.objects.get_for_model(cls)
            for cls in JOBINDEX_MODEL_CLASSES]
    return _JOBINDEX_CONTENT_TYPES


class JobIndexMixin(RoutablePageMixin):
    job_model = None
    subpage_types = []

    @route(r'^(?P<uuid>[0-9a-f-]+)/$', name='job')
    def v_job(s, r, **k):
        return frontend.job_detail(r, s, **k)

    @route(r'^(?P<uuid>[0-9a-f-]+)/pdf/$', name='job_pdf')
    def v_job_pdf(s, r, **k):
        return frontend.job_pdf(r, s, **k)

    @classmethod
    def get_job_model(cls):
        if isinstance(cls.job_model, models.Model):
            return cls.job_model
        elif isinstance(cls.job_model, string_types):
            return resolve_model_string(cls.job_model, cls._meta.app_label)
        else:
            raise ValueError('Can not resolve {0}.job_model in to a model: {1!r}'.format(
                cls.__name__, cls.job_model))


class AbstractJobQuerySet(QuerySet):
    def search(self, query_string, fields=None, backend='default'):
        """
        This runs a search query on all the pages in the QuerySet
        """
        search_backend = get_search_backend(backend)
        return search_backend.search(query_string, self)


class AbstractJob(models.Model):
    jobindex = models.ForeignKey(Page)
    uuid = UUIDField(auto=True, null=True, default=None)
    issue_date = models.DateTimeField('Issue date', default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Without dollar sign($)')

    # User creating the job
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    panels = [
        FieldPanel('amount'),
    ]

    objects = AbstractJobQuerySet.as_manager()

    class Meta:
        abstract = True

    def get_nice_url(self):
        return slugify(text_type(self))

    def get_template(self, request):
        try:
            return self.template
        except AttributeError:
            return '{0}/{1}.html'.format(self._meta.app_label, self._meta.model_name)

    def url(self):
        jobindex = self.jobindex.specific
        url = jobindex.url + jobindex.reverse_subpage('job', kwargs={
            'uuid': str(self.uuid)})
        return url

    def serve(self, request):
        return render(request, self.get_template(request), {
            'self': self.jobindex.specific,
            'job': self,
        })

    def serve_pdf(self, request):
        # Convert HTML URIs to absolute system paths
        def link_callback(uri, rel):
            # use short variable names
            sUrl = settings.STATIC_URL
            sRoot = settings.STATIC_ROOT
            mUrl = settings.MEDIA_URL
            mRoot = settings.MEDIA_ROOT

            # convert URIs to absolute system paths
            if uri.startswith(mUrl):
                path = os.path.join(mRoot, uri.replace(mUrl, ""))
            elif uri.startswith(sUrl):
                path = os.path.join(sRoot, uri.replace(sUrl, ""))

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % \
                            (sUrl, mUrl))
            return path

        # Render html content through html template with context
        template = get_template(settings.PDF_TEMPLATE)
        html = template.render(Context({'job': self}))
        print(type(self))

        # Write PDF to file
        file = StringIO.StringIO()
        pisaStatus = pisa.CreatePDF(
            html,
            dest=file,
            link_callback=link_callback)

        # Return PDF document through a Django HTTP response
        file.seek(0)
        return HttpResponse(file, content_type='application/pdf')

# Need to import this down here to prevent circular imports :(
