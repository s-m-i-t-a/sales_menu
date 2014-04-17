# -*- coding: utf-8 -*-

import random

import pytest

from .factories import MenuFactory

from sales_menu.models import Menu


class TestMenuManager(object):
    @pytest.mark.django_db
    def test_return_only_root_items(self):
        menu_root = []
        submenu = []

        # generate root menu
        for i in range(random.randint(2, 10)):
            menu = MenuFactory()
            menu_root.append(menu)

            # generate submenu
            for j in range(random.randint(0, 10)):
                submenu.append(MenuFactory(parent=menu))

        roots = Menu.root.all()

        for item in submenu:
            assert item not in roots

        for item in menu_root:
            assert item in roots

    @pytest.mark.django_db
    def test_root_menu_is_ordred_by_weight(self):
        menu_root = []
        submenu = []

        # generate root menu
        for i in range(random.randint(2, 10)):
            menu = MenuFactory(weight=random.randint(1, 10))
            menu_root.append(menu)

            # generate submenu
            for j in range(random.randint(0, 10)):
                submenu.append(MenuFactory(parent=menu, weight=random.randint(1, 10)))

        roots = Menu.root.all()

        last = 0
        for item in roots:
            assert item.weight >= last
            last = item.weight

    @pytest.mark.django_db
    def test_returned_objects_are_sorted_by_real_weight(self):
        menu_root = []
        submenu = []

        # generate root menu
        for i in range(random.randint(2, 10)):
            menu = MenuFactory(weight=random.randint(1, 10))
            menu_root.append(menu)

            # generate submenu
            for j in range(random.randint(0, 10)):
                submenu.append(MenuFactory(parent=menu, weight=random.randint(1, 10)))

        menus = Menu.objects.all()

        last = 0
        for item in menus:
            assert item.real_weight >= last
            last = item.real_weight
