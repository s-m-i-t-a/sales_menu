# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _

from sales_menu.models import Menu


class MenuAdmin(admin.ModelAdmin):

    list_display = ('indented_name', )

    def indented_name(self, obj):
        item = obj
        indent = u''
        while item.parent is not None:
            item = item.parent
            indent = u'%s-' % indent

        return u'%s %s' % (indent, obj.text)

    indented_name.short_description = _(u'Text')


admin.site.register(Menu, MenuAdmin)
