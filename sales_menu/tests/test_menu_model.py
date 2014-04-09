# -*- coding: utf-8 -*-

import random

import pytest

from menu.models import Menu

from factories import MenuFactory


class TestMenu(object):

    @pytest.mark.django_db
    def test_menu_children(self):
        menu = MenuFactory()

        menu1 = MenuFactory(parent=menu)
        menu2 = MenuFactory(parent=menu)

        children = menu.children()

        assert menu1 and menu2 in children

    @pytest.mark.django_db
    def test_selected_menu_path(self):
        menu_root1 = MenuFactory()
        menu_root2 = MenuFactory()

        menu1 = MenuFactory(parent=menu_root1)
        menu2 = MenuFactory(parent=menu_root2)

        assert menu1 and menu_root1 in Menu.selected_path(menu1.url)
        assert menu2 and menu_root2 in Menu.selected_path(menu2.url)
        assert menu_root1 and not (menu1 and menu2) in Menu.selected_path(menu_root1.url)
        assert menu_root2 and not (menu1 and menu2) in Menu.selected_path(menu_root2.url)

    @pytest.mark.django_db
    def test_get_real_weight(self):
        menu = MenuFactory(weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))

        menu1 = MenuFactory(parent=menu, weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))
        menu2 = MenuFactory(parent=menu, weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))
        menu3 = MenuFactory(parent=menu1, weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))

        menu_weight = (menu.weight << (Menu.BITS_PER_LEVEL * Menu.MAX_LEVEL))
        menu1_weight = menu_weight | (menu1.weight << (Menu.BITS_PER_LEVEL * (Menu.MAX_LEVEL - 1)))
        menu2_weight = menu_weight | (menu2.weight << (Menu.BITS_PER_LEVEL * (Menu.MAX_LEVEL - 1)))
        menu3_weight = menu_weight | menu1_weight | (menu3.weight << (Menu.BITS_PER_LEVEL * (Menu.MAX_LEVEL - 2)))

        assert menu3.get_real_weight() == menu3_weight
        assert menu2.get_real_weight() == menu2_weight
        assert menu1.get_real_weight() == menu1_weight
        assert menu.get_real_weight() == menu_weight

    @pytest.mark.django_db
    def test_save_calculated_real_weight(self):
        menu = MenuFactory(weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))

        menu1 = MenuFactory(parent=menu, weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))
        menu2 = MenuFactory(parent=menu, weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))

        m2 = Menu.objects.get(pk=menu2.pk)

        assert m2.real_weight > 0

        old_real_weight = m2.real_weight

        new_weight = m2.weight

        while new_weight == m2.weight:
            new_weight = random.randint(1, 2 ** Menu.BITS_PER_LEVEL)

        m2.weight = new_weight
        m2.save()

        assert m2.real_weight != old_real_weight

    @pytest.mark.django_db
    def test_real_weight_changed_when_change_level(self):
        menu = MenuFactory(weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))

        menu1 = MenuFactory(parent=menu, weight=random.randint(1, 2 ** Menu.BITS_PER_LEVEL))

        old_real_weight = menu1.real_weight

        menu1.parent = None
        menu1.save()

        assert menu1.real_weight != old_real_weight

    @pytest.mark.django_db
    def test_real_weight_of_child_change_when_change_parent_real_weight(self):
        menu = MenuFactory(weight=1)

        menu1 = MenuFactory(parent=menu, weight=1)

        old_real_weight = menu1.real_weight

        menu.weight = 2
        menu.save()

        m = Menu.objects.get(url=menu1.url)

        assert m.real_weight > old_real_weight
