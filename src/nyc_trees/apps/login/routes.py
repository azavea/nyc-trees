# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.utils import decorate as do
from django_tinsel.decorators import route, render_template

from apps.login import views as v
from apps.login.backends import NycRegistrationView


#####################################
# ACCOUNTS ROUTES
#####################################

logout = do(v.logout)
password_reset = do(v.password_reset)

activation_complete = do(
    login_required,
    render_template('registration/activation_complete.html'),
    route(GET=v.activation_complete,
          POST=v.save_optional_info))

register = NycRegistrationView.as_view()

password_reset_impossible = route(
    GET=render_template('login/password_reset_impossible.html')())

#####################################
# LOGIN ROUTES
#####################################

forgot_username = do(
    render_template('login/forgot_username.html'),
    route(GET=v.forgot_username_page, POST=v.forgot_username))

forgot_username_sent = do(
    render_template('login/forgot_username_complete.html'),
    v.forgot_username_sent)

# We use a slightly different template when coming from a failed password reset
password_reset_resend_activation = do(
    render_template('login/password_reset_activation_email.html'),
    route(GET=v.send_activation_email_page, POST=v.send_activation_email))

send_activation_email = do(
    render_template('login/send_activation_email.html'),
    route(GET=v.send_activation_email_page, POST=v.send_activation_email))

activation_email_sent = do(
    render_template('login/activation_email_sent.html'),
    v.activation_email_sent)

activated = do(
    render_template('login/activated.html'),
    v.activated)
