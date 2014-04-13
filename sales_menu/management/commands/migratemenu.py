# -*- coding: utf-8 -*-


from django.core.management.base import BaseCommand, CommandError
from django.contrib.flatpages.models import FlatPage
from django.db import connection
from django.utils.translation import ugettext as _

from sales_menu.models import Menu


OLD_MENU_SQL = '''SELECT * FROM old_menu_menu ORDER BY url'''


class Command(BaseCommand):
    help = _(u'Migrate old menu data to new menu.')

    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def get_old_menu(self):
        cursor = connection.cursor()
        cursor.execute(OLD_MENU_SQL)

        old_menu = self.dictfetchall(cursor)

        return old_menu

    def get_menu_name(self, url):
        '''
        Search for url in flatpages and return title.
        '''
        try:
            fp = FlatPage.objects.get(url=url)
            name = fp.title
        except FlatPage.DoesNotExist:
            name = url.strip("/").replace("/", " ")

        return name

    def migrate(self, old_menu):
        for old in old_menu:
            parent = None
            path = old['url'].strip('/').split('/')
            if len(path) > 1:
                parent_url = '/%s/' % ('/'.join(path[:-1]), )
                parent = Menu.objects.get(url=parent_url)

            menu = Menu(
                text=self.get_menu_name(old['url']),
                parent=parent,
                weight=old['weight'],
                url=old['url']
            )
            menu.save()

    def handle(self, *args, **options):
        self.migrate(self.get_old_menu())
