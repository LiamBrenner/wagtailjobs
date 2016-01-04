from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from . import urls
from .permissions import user_can_edit_jobs


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^jobs/', include(urls)),
    ]


@hooks.register('construct_main_menu')
def construct_main_menu(request, menu_items):
    if request.user.is_active and request.user.has_perm('wagtailadmin.access_admin'):
        menu_items.append(
            MenuItem(_('Jobs'), urlresolvers.reverse('wagtailjobs_choose'),
                     classnames='icon icon-user', order=250)
        )
