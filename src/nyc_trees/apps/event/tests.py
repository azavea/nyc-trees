# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from functools import partial

from datetime import datetime, timedelta
from django.utils import timezone

from django.core import mail
from django.http import HttpResponseForbidden

from apps.core.test_utils import make_request, make_event

from apps.users.models import User
from apps.users.tests import UsersTestCase

from apps.event.models import Event, EventRegistration
from apps.event.views import (events_list_page,
                              event_email,
                              register_for_event,
                              event_admin_check_in_page,
                              event_user_check_in_poll,
                              check_in_user_to_event,
                              increase_rsvp_limit)


class EventTestCase(UsersTestCase):
    def setUp(self):
        super(EventTestCase, self).setUp()
        self.event = make_event(self.group)


class EventListTest(EventTestCase):
    def test_following_user(self):
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 1)
        self.assertFalse(
            ctx['immediate_events']['event_infos'][0]['user_is_registered'])

    def test_following_user_registered(self):
        EventRegistration.objects.create(user=self.user,
                                         event=self.event)
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 1)
        self.assertTrue(
            ctx['immediate_events']['event_infos'][0]['user_is_registered'])

    def test_other_user(self):
        request = make_request(user=self.other_user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 0)
        self.assertFalse(
            ctx['all_events']['event_infos'][0]['user_is_registered'])


class EventEmailTest(EventTestCase):
    def test_sending_email(self):
        reg = EventRegistration(event=self.event, user=self.user)
        reg.clean_and_save()

        request = make_request({
            'subject': 'Come to the event',
            'body': "It's happening now!"
        }, self.other_user, 'POST', group=self.group)

        context = event_email(request, self.event.slug)

        self.assertEqual(mail.outbox[0].subject, "Come to the event")
        self.assertTrue(context['message_sent'])
        self.assertEqual(self.event, context['event'])
        self.assertEqual(self.group, context['group'])

        # Clear the test inbox
        mail.outbox = []


class CheckinEventTest(EventTestCase):
    def _assert_num_checkins(self, expected_amount):
        request = make_request(user=self.user, group=self.group)
        context = event_admin_check_in_page(request, self.event.slug)
        self.assertEqual(self.event, context['event'])
        self.assertEqual(self.group, context['group'])

        checkins = sum(1 if did_attend else 0
                       for user, did_attend in context['users'])
        self.assertEqual(expected_amount, checkins)

    def test_checkin_checkout(self):
        self._assert_num_checkins(0)
        request = partial(make_request, user=self.user, group=self.group)

        # Checkin (should fail because user has not RSVPed yet)
        context = check_in_user_to_event(request(method='POST'),
                                         self.event.slug,
                                         self.user.username)
        self.assertTrue(isinstance(context, HttpResponseForbidden))

        # RSVP
        register_for_event(request(method='POST'), self.event.slug)

        # Checkin again (should succeed this time)
        check_in_user_to_event(request(method='POST'),
                               self.event.slug,
                               self.user.username)
        self._assert_num_checkins(1)

        # Un-Checkin
        check_in_user_to_event(request(method='DELETE'),
                               self.event.slug,
                               self.user.username)
        self._assert_num_checkins(0)

    def test_rsvp_limit_increase(self):
        request = make_request(user=self.user, group=self.group)

        self.event.max_attendees = 0
        self.event.save()

        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(0, self.event.max_attendees)

        context = increase_rsvp_limit(request, self.event.slug)
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(5, context['max_attendees'])
        self.assertEqual(5, self.event.max_attendees)

        context = increase_rsvp_limit(request, self.event.slug)
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(10, context['max_attendees'])
        self.assertEqual(10, self.event.max_attendees)

        context = increase_rsvp_limit(request, self.event.slug)
        self.event = Event.objects.get(id=self.event.id)
        self.assertEqual(15, context['max_attendees'])
        self.assertEqual(15, self.event.max_attendees)

    def test_starting_soon(self):
        tz = timezone.get_current_timezone()
        event = Event(begins_at=datetime(2015, 1, 13, hour=12, tzinfo=tz),
                      ends_at=datetime(2015, 1, 13, hour=13, tzinfo=tz))

        dt = datetime(2015, 1, 13, hour=10, minute=59, tzinfo=tz)
        self.assertFalse(event.starting_soon(dt))

        # From hour=10, minute=59
        #   to hour=12, minute=59
        for i in xrange(120):
            dt = dt + timedelta(minutes=1)
            self.assertTrue(event.starting_soon(dt))

        # hour=13, minute=0
        dt = dt + timedelta(minutes=1)
        self.assertFalse(event.starting_soon(dt))

    def test_field_training_complete(self):
        request = make_request(user=self.user, group=self.group, method='POST')

        user = self.user
        user.field_training_complete = False
        user.clean_and_save()

        # RSVP
        register_for_event(request, self.event.slug)

        # Check-in user to normal event
        self.event.includes_training = False
        self.event.clean_and_save()
        check_in_user_to_event(request, self.event.slug, self.user.username)
        user = User.objects.get(id=user.id)
        self.assertEqual(False, user.field_training_complete)

        # Check-in user to training event
        self.event.includes_training = True
        self.event.clean_and_save()
        check_in_user_to_event(request, self.event.slug, self.user.username)
        user = User.objects.get(id=user.id)
        self.assertEqual(True, user.field_training_complete)

    def test_user_checkin_poll(self):
        partial_request = partial(make_request, user=self.user,
                                  group=self.group, event=self.event)

        # RSVP
        register_for_event(partial_request(method='POST'), self.event.slug)

        response = event_user_check_in_poll(partial_request(), self.event.slug)
        self.assertFalse(response['checked_in'])

        # Check-in to event
        check_in_user_to_event(partial_request(method='POST'),
                               self.event.slug,
                               self.user.username)

        response = event_user_check_in_poll(partial_request(), self.event.slug)
        self.assertTrue(response['checked_in'])


class MyEventsNowTestCase(UsersTestCase):
    def _make_event(self, start_delta, end_delta):
        now = timezone.now()
        event = make_event(
            self.group,
            begins_at=now + timedelta(hours=start_delta),
            ends_at=now + timedelta(hours=end_delta))
        return event

    def _get_my_events_now(self, start_delta, end_delta, **kwargs):
        args = {
            'event': self._make_event(start_delta, end_delta),
            'user': self.user,
        }
        args.update(kwargs)

        EventRegistration.objects.create(**args)

        events = EventRegistration.my_events_now(self.user)
        return events

    def assert_included(self, start_delta, end_delta, **kwargs):
        events = self._get_my_events_now(start_delta, end_delta, **kwargs)
        self.assertEqual(len(events), 1)

    def assert_excluded(self, start_delta, end_delta, **kwargs):
        events = self._get_my_events_now(start_delta, end_delta, **kwargs)
        self.assertEqual(len(events), 0)

    def test_included_if_starting_now(self):
        self.assert_included(+0, +1)

    def test_excluded_if_ended_6_hours_ago(self):
        self.assert_excluded(-5, -6)

    def test_excluded_if_starting_in_6_hours(self):
        self.assert_excluded(+6, +7)

    def test_excluded_if_checked_in(self):
        self.assert_excluded(+0, +1, did_attend=True)

    def test_excluded_if_not_registered(self):
        self.assert_excluded(+0, +1, user=self.other_user)

    def test_has_started(self):
        event = self._make_event(-1, +1)
        self.assertTrue(event.has_started)

    def test_has_not_started(self):
        event = self._make_event(+3, +5)
        self.assertFalse(event.has_started)
