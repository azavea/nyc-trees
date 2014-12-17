# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from sbo_selenium import SeleniumTestCase

from django.core.urlresolvers import reverse


class NycTreesSeleniumTestCase(SeleniumTestCase):
    def wait_for_textbox_then_type(self, selector, text):
        return self.wait_for_element(selector).send_keys(text)

    def login(self, username, password='password'):
        self.get(reverse('auth_login'))

        self.wait_for_textbox_then_type('[name="username"]', username)
        self.wait_for_textbox_then_type('[name="password"]', password)

        self.click('form input[type="submit"]')

        self.wait_for_text('This is your user profile')
