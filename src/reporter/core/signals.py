# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete

from reporter.core import models


def invalidate_menu_cache(sender, instance, **kwargs):  # @UnusedVariable
    # context cache
    cache.delete('menu')
    # template cache
    cache.delete(make_template_fragment_key('rendered_menu'))

post_save.connect(invalidate_menu_cache, sender=models.MenuItem)
post_delete.connect(invalidate_menu_cache, sender=models.MenuItem)
