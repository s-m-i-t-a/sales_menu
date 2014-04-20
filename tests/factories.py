# -*- coding: utf-8 -*-

import factory

from sales_menu.models import Menu


class MenuFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Menu

    text = factory.Sequence(lambda n: u'Menu %d' % n)
    parent = None
    url = factory.Sequence(lambda n: u'/menu-%d' % n)
    weight = factory.Sequence(lambda n: n)
