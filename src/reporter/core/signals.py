from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver
from mptt.signals import node_moved

from . import models


@receiver(post_save, sender=models.MenuItem)
@receiver(post_delete, sender=models.MenuItem)
@receiver(node_moved, sender=models.MenuItem)
def invalidate_menu_cache(sender, instance, **kwargs):  # @UnusedVariable
    # context cache
    cache.delete("menu")
    # template cache
    cache.delete(make_template_fragment_key("rendered_menu"))
