# -*- coding: utf-8 -*-

import random

import pytest

from django.template import Context, Template
from django.test.client import RequestFactory

from sales_menu.templatetags.menu_tags import MenuNode
from sales_menu.models import Menu

from .factories import MenuFactory


class TestMenuNode(object):
    def test_context_without_request(self):
        context = Context()

        node = MenuNode()
        node.render(context)

        assert 'menu' not in context
        assert 'selected_menu_path' not in context

    @pytest.mark.django_db
    def test_context_contain_root_menu(self):
        context = Context()

        root_menu = []
        for i in range(random.randint(2, 10)):
            root_menu.append(MenuFactory())

        context['request'] = RequestFactory().get(root_menu[0].url)

        node = MenuNode()
        node.render(context)

        for menu_item in root_menu:
            assert menu_item in context['menu']

    @pytest.mark.django_db
    def test_context_contain_selected_path(self):
        context = Context()

        menu_root = []
        submenu = []

        # generate root menu
        for i in range(random.randint(2, 10)):
            menu = MenuFactory()
            menu_root.append(menu)

            # generate submenu
            for j in range(random.randint(0, 10)):
                submenu.append(MenuFactory(parent=menu))

        selected = random.choice(menu_root + submenu)
        context['request'] = RequestFactory().get(selected.url)

        node = MenuNode()
        node.render(context)

        item = selected
        while item is not None:
            assert item in context['selected_menu_path']
            item = item.parent

    @pytest.mark.django_db
    def test_context_contain_submenu(self):
        context = Context()

        menu_root = []
        submenu = []

        # generate root menu
        for i in range(random.randint(2, 10)):
            menu = MenuFactory()
            menu_root.append(menu)

            # generate submenu
            for j in range(random.randint(0, 10)):
                submenu.append(MenuFactory(parent=menu))

        selected = random.choice(menu_root + submenu)
        context['request'] = RequestFactory().get(selected.url)

        node = MenuNode()
        node.render(context)

        root = selected
        while root.parent is not None:
            root = root.parent

        for item in root.children():
            assert item in context['submenu']


class TestMenuTags(object):
    def render_page(self, request=None):
        """Return rendred test template."""

        if request is None:
            request = RequestFactory().get(Menu.root.all()[0].url)

        template = Template('''
            {% load menu_tags %}
            {% menu %}

            {% for item in menu %}
                <p>{{ item.text }}</p>
            {% endfor %}
        ''')

        context = Context({'request': request})
        rendered = template.render(context)

        return rendered

    @pytest.mark.django_db
    def test_menu_tag(self):
        menu_root = []
        submenu = []

        # generate root menu
        for i in range(random.randint(2, 10)):
            menu = MenuFactory()
            menu_root.append(menu)

            # generate submenu
            for j in range(random.randint(0, 10)):
                submenu.append(MenuFactory(parent=menu))

        rendred = self.render_page()

        assert all(map(lambda m: rendred.find(m.text) > -1, menu_root))
