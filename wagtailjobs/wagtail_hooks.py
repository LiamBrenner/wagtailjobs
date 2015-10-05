from __future__ import unicode_literals, absolute_import

from django.conf.urls import include, url
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from . import pays_urls, jobs_urls
from .permissions import user_can_edit_jobs


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^jobs/', include(jobs_urls)),
        url(r'^pays/', include(pays_urls)),
    ]


@hooks.register('construct_main_menu')
def construct_main_menu(request, menu_items):
    if user_can_edit_jobs(request.user):
        menu_items.append(
            MenuItem(_('Jobs'), urlresolvers.reverse('wagtailjobs_choose'),
                     classnames='icon icon-user', order=250)
        )
        menu_items.append(
            MenuItem(_('Pays'), urlresolvers.reverse('wagtailjobs_payindex'),
                     classnames='icon icon-group', order=250)
        )
