from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import chooser


urlpatterns = [
    url(r'^$', chooser.payindex,
        name='wagtailjobs_payindex'),
]
