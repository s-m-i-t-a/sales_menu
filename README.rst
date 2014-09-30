=============================
sales_menu
=============================

.. image:: https://badge.fury.io/py/sales_menu.png
    :target: https://badge.fury.io/py/sales_menu

.. image:: https://travis-ci.org/s-m-i-t-a/sales_menu.png?branch=master
    :target: https://travis-ci.org/s-m-i-t-a/sales_menu

.. image:: https://coveralls.io/repos/s-m-i-t-a/sales_menu/badge.png?branch=master
    :target: https://coveralls.io/r/s-m-i-t-a/sales_menu?branch=master

.. image:: https://requires.io/github/s-m-i-t-a/sales_menu/requirements.svg?branch=master
    :target: https://requires.io/github/s-m-i-t-a/sales_menu/requirements/?branch=master
    :alt: Requirements Status

The simple menu for Django.

..
    Documentation
    -------------

..
    The full documentation is at https://sales_menu.readthedocs.org.

Quickstart
----------

Install sales_menu::

    pip install sales_menu

Add ``sales_menu`` to your ``INSTALLED_APPS`` list in your settings.

``sales_menu`` requires that the ``request`` object be available in
the context when you call the ``{% menu %}`` template tag. This
means that you need to ensure that your ``TEMPLATE_CONTEXT_PROCESSORS``
setting includes ``django.core.context_processors.request``, which it
doesn't by default.

And use in template::

    {% menu_tags %}
    {% menu %}

    {% for item in menu %}

        <p>{{ item.text }}
        {% if menu_item in selected_menu_path %}
        &mdash; selected
        {% endif %}
        </p>

        {% for child in item.children %}
            <p>— {{ child.text }}</p>
        {% endfor %}
    {% endfor %}

Features
--------

* TODO
