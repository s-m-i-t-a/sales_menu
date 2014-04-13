# -*- coding: utf-8 -*-

from django import template

from sales_menu.models import Menu


register = template.Library()

# get_menu
# get_submenu
# get_sitemap - return menu for use in footer


class MenuNode(template.Node):
    def render(self, context):
        if 'request' not in context:
            return ''

        request = context['request']

        context['menu'] = Menu.root.all()
        selected_path = Menu.selected_path(request.path)
        context['selected_menu_path'] = selected_path

        if len(selected_path) > 0:
            context['submenu'] = context['selected_menu_path'][0].children()

        return ''


@register.tag
def menu(parser, token):
    return MenuNode()
