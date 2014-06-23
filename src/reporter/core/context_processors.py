# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.utils.safestring import mark_safe
from reporter.core import models
from reporter.core.utils import fetch_credits


CACHE_TIMEOUT = 60 * 60 * 24

# get credits + split contributers
CONTRIBUTORS, FUNDS = fetch_credits()


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
    # cache all request 24h
    menu = cache.get('menu')
    if not menu:
        roots = models.MenuItem.objects.filter(level=0)  # @UndefinedVariable
        menu = []
        for n in roots:
            menu.append(_recursive_node(n))
        cache.set('menu', menu, CACHE_TIMEOUT)
    return {
        'menu': menu,
        'contributors': CONTRIBUTORS,
        'funds': FUNDS,
    }
