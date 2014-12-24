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

        self.wait_for_text('Contributions')

    def assert_text_in_body(self, text):
        body = self.sel.find_element_by_css_selector('body').text
        self.assertTrue(text in body,
                        'Expected to find %s in %s' % (text, body))

    def assert_text_not_in_body(self, text):
        body = self.sel.find_element_by_css_selector('body').text
        self.assertTrue(text not in body,
                        'Did not expect to find %s in %s' % (text, body))
