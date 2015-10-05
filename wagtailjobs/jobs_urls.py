from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import chooser, editor


urlpatterns = [
    url(r'^$', chooser.choose,
        name='wagtailjobs_choose'),
    url(r'^(?P<pk>\d+)/$', chooser.index,
        name='wagtailjobs_index'),
    url(r'^(?P<pk>\d+)/search/$', chooser.search,
        name='wagtailjobs_search'),
    url(r'^(?P<pk>\d+)/create/$', editor.create,
        name='wagtailjobs_create'),
    url(r'^(?P<pk>\d+)/edit/(?P<job_pk>.*)/$', editor.edit,
        name='wagtailjobs_edit'),
    url(r'^(?P<pk>\d+)/delete/(?P<job_pk>.*)/$', editor.delete,
        name='wagtailjobs_delete'),
    url(r'^(?P<pk>\d+)/copy/(?P<job_pk>.*)/$', editor.copy,
        name='wagtailjobs_copy'),
    # pays
    url(r'^$', chooser.payindex,
        name='wagtailjobs_payindex'),
]
