# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from libs.ui_test_helpers import NycTreesSeleniumTestCase

from apps.core.models import User


class LoginUITest(NycTreesSeleniumTestCase):
    def setUp(self):
        super(LoginUITest, self).setUp()
        self.user = User(username='guy', email='guy@guy.co.uk')
        self.user.set_password('password')
        self.user.save()

    def test_login(self):
        self.get('/accounts/login/')

        self.wait_for_textbox_then_type('[name="username"]',
                                        self.user.username)
        self.wait_for_textbox_then_type('[name="password"]', 'password')

        self.click('form input[type="submit"]')
