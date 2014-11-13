# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from sbo_selenium import SeleniumTestCase


class NycTreesSeleniumTestCase(SeleniumTestCase):
    def wait_for_textbox_then_type(self, selector, text):
        return self.wait_for_element(selector).send_keys(text)
