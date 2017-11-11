# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.core.cache import cache
from django.utils.safestring import mark_safe

from . import models, utils


CACHE_TIMEOUT = 60 * 60 * 24


def _recursive_node(node):
    children = [_recursive_node(c) for c in node.get_children()]
    return {'icon': node.icon,
            'name': mark_safe(node.name.replace(' ', '&nbsp;')),
            'url': node.url,
            'is_leaf_node': node.is_leaf_node(),
            'children': children}


def static(request):  # @UnusedVariable
    """
    A context processor returning basic parameters used on all pages.
    """
    # cache menu structure for 24h
    menu = cache.get('menu')
    if not menu:
        roots = models.MenuItem.objects.filter(level=0)  # @UndefinedVariable
        menu = []
        for n in roots:
            menu.append(_recursive_node(n))
        cache.set('menu', menu, CACHE_TIMEOUT)
    # cache funds and contributors content for 24h
    funds = cache.get('funds')
    contributors = cache.get('contributors')
    backup_funds = cache.get('backup_funds') or funds
    backup_contributors = cache.get('backup_contributors') or contributors
    if not funds or not contributors:
        print('no cache')
        try:
            contributors, funds = utils.fetch_credits()
        except Exception:
            # timeout - just use our backup
            cache.set('funds', backup_funds, CACHE_TIMEOUT)
            cache.set('contributors', backup_contributors, CACHE_TIMEOUT)
        else:
            print('new cache')
            cache.set('funds', funds, CACHE_TIMEOUT)
            cache.set('contributors', contributors, CACHE_TIMEOUT)
            # overwrite/set our new backup - no cache timeout
            cache.set('backup_funds', funds, None)
            cache.set('backup_contributors', contributors, None)
    return {
        'menu': menu,
        'contributors': contributors,
        'funds': funds,
    }
