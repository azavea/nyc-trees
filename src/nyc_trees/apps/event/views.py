# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import render_template


def event_dashboard(request, group_slug):
    # TODO: implement
    pass


def add_event(request, group_slug):
    # TODO: implement
    pass


@render_template('event/add_event.html')
def add_event_page(request, group_slug):
    # TODO: implement
    return {}


@render_template('event/event_detail.html')
def event_detail(request, group_slug, event_slug):
    # TODO: implement
    return {}


@render_template('event/event_list.html')
def events_list_page(request):
    # TODO: implement
    return {}


def events_list_page_partial(request):
    # TODO: implement
    pass


def events_list_feed(request):
    # TODO: implement
    pass


def delete_event(request, group_slug, event_slug):
    # TODO: implement
    pass


@render_template('event/edit_event.html')
def edit_event_page(request, group_slug, event_slug):
    # TODO: implement
    return {}


def edit_event(request, group_slug, event_slug):
    # TODO: implement
    pass


def event_popup_partial(request, group_slug, event_slug):
    # TODO: implement
    pass


def register_for_event(request, group_slug, event_slug):
    # TODO: implement
    pass


def cancel_event_registration(request, group_slug, event_slug):
    # TODO: implement
    pass


def start_event_map_print_job(request, group_slug, event_slug):
    # TODO: implement
    pass


@render_template('event/admin_checkin.html')
def event_check_in_page(request, group_slug, event_slug):
    # TODO: implement
    return {}


def check_in_user_to_event(request, group_slug, event_slug, username):
    # TODO: implement
    pass


def un_check_in_user_to_event(request, group_slug, event_slug, username):
    # TODO: implement
    pass


def email_event_registered_users(request, group_slug, event_slug):
    # TODO: implement
    pass
