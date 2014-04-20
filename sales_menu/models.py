# -*- coding: utf-8 -*-

from collections import deque

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class MenuManager(models.Manager):
    def get_queryset(self):
        return super(MenuManager, self).get_queryset().order_by('real_weight')


class RootMenuManager(MenuManager):
    def get_queryset(self):
        return super(RootMenuManager, self).get_queryset().filter(parent=None)


class Menu(models.Model):
    BITS_PER_LEVEL = 6  # 2 ** 6 = 64 (who want more? idiot!?)
    LEVELS = 4  # levels count (level 0, level 1, ..., level LEVELS - 1)
    MAX_LEVEL = LEVELS - 1

    text = models.CharField(verbose_name=_(u'Text'), max_length=255)
    parent = models.ForeignKey('self', verbose_name=_(u'Parent'), default=None, blank=True, null=True)
    url = models.CharField(verbose_name=_(u"Link"), max_length=255)
    weight = models.PositiveIntegerField(verbose_name=_(u"Order"), default=1)
    real_weight = models.PositiveIntegerField(default=0, editable=False)

    objects = MenuManager()
    root = RootMenuManager()

    def __unicode__(self):
        return self.text

    def children(self):
        return Menu.objects.filter(parent=self)

    def clean(self):
        super(Menu, self).clean()

        self.validate_unique_weight_in_same_level()

    def get_real_weight(self):
        '''
        The real weight is calculated as the sum of the weights of parents shifted by BITS_PER_LEVEL bits.
        '''
        level_passed = 0
        weights = []

        item = self
        while item is not None:
            weights.append(item.weight)
            level_passed = level_passed + 1
            item = item.parent

        result = 0
        for x in weights:
            result = result | (x << (Menu.BITS_PER_LEVEL * (Menu.LEVELS - level_passed)))
            level_passed = level_passed - 1

        return result

    def save(self, *args, **kwargs):
        self.real_weight = self.get_real_weight()

        # TODO: call full_clean or not?

        return super(Menu, self).save(*args, **kwargs)

    def validate_unique_weight_in_same_level(self):
        '''
        Check unique combination parent and weight.
        '''
        if Menu.objects.filter(parent=self.parent).filter(weight=self.weight).exists():
            raise ValidationError('The combination of parent and weight must be unique.')

    @classmethod
    def selected_path(cls, url):
        path = []
        try:
            menu_item = cls.objects.get(url=url)

            while menu_item.parent is not None:
                path.insert(0, menu_item)
                menu_item = menu_item.parent

            # add last item
            path.insert(0, menu_item)

        except cls.DoesNotExist:
            pass
        except cls.MultipleObjectsReturned:
            pass

        return path

    class Meta:
        verbose_name = _(u"Menu")
        verbose_name_plural = _(u"Menu")


@receiver(post_save, sender=Menu, dispatch_uid='menu-propagate-weight')
def propagate_weight_change(sender, instance, **kwargs):
    '''
    When is real_weight changed, then children must recalculate own real_weight.
    '''
    queue = deque(instance.children())
    while len(queue) > 0:
        item = queue.popleft()
        item.save()

        children = item.children()
        if len(children) > 0:
            queue.extend(children)
