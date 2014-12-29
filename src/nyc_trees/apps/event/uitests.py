# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import datetime

from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.utils.timezone import (make_aware, localtime, get_current_timezone,
                                   now)

from libs.ui_test_helpers import NycTreesSeleniumTestCase

from apps.core.models import User, Group

from apps.event.models import Event, EventRegistration


def add_event(group, begins_at, ends_at):
    kwargs = {
        'group': group,
        'title': 'Test event',
        'slug': 'test-event-slug',
        'begins_at': begins_at,
        'ends_at': ends_at,
        'location': Point(0, 0),
        'max_attendees': 0,
        'contact_email': 'test@aol.com',
        'address': '340 N 12th St.'
    }
    event = Event(**kwargs)
    event.clean_and_save()
    return event


class EventTestCase(NycTreesSeleniumTestCase):
    def setUp(self):
        super(EventTestCase, self).setUp()

        self.user = User(username='leela',
                         email='leela@planetexpress.nyc',
                         first_name='Turanga',
                         last_name='Leela')
        self.user.set_password('password')
        self.user.clean_and_save()

        self.group = Group.objects.create(
            name='Planet Express',
            slug='planet-express',
            description='A simple delivery company',
            contact_name='Professor Farnseworth',
            contact_email='prof@planetexpress.nyc',
            contact_url='https://planetexpress.nyc',
            admin=self.user
        )


class AddEventUITest(EventTestCase):
    def test_add_event(self):
        self.login(self.user.username)

        self.get(reverse('add_event', kwargs={'group_slug': self.group.slug}))

        self.wait_for_textbox_then_type('[name="title"]', 'Xmas')
        self.wait_for_textbox_then_type('[name="date"]', '12/25/2014')
        self.wait_for_textbox_then_type('[name="begins_at_time"]', '11:00 PM')
        self.wait_for_textbox_then_type('[name="ends_at_time"]', '11:59 PM')
        self.wait_for_textbox_then_type('[name="address"]', 'Central Park')
        self.wait_for_textbox_then_type('[name="max_attendees"]', '35')

        self.click('#use-my-contact-info')

        self.click('form input[type="submit"]')

        self.wait_for_text('Events')

        events = Event.objects.all()

        self.assertEqual(1, len(events))
        xmas = make_aware(datetime(2014, 12, 25, 23, 59),
                          get_current_timezone())
        self.assertEqual(xmas, localtime(events[0].ends_at))
        self.assertEqual('%s %s' % (self.user.first_name, self.user.last_name),
                         events[0].contact_name)
        self.assertEqual(self.user.email, events[0].contact_email)


class EditEventUITest(EventTestCase):
    def test_edit_event_datetime_fields(self):
        """
        Test that saving the edit form without modifications doesn't alter
        datetime fields.
        """
        self.login(self.user.username)

        begins_at = make_aware(datetime(2014, 1, 1, 13),
                               get_current_timezone())
        ends_at = make_aware(datetime(2014, 1, 1, 14),
                             get_current_timezone())

        event = add_event(self.group, begins_at, ends_at)

        self.get(reverse('event_edit', kwargs={
            'group_slug': self.group.slug,
            'event_slug': event.slug
        }))
        self.click('form input[type="submit"]')

        updated_event = Event.objects.get(id=event.id)
        self.assertEqual(updated_event.begins_at, event.begins_at)
        self.assertEqual(updated_event.ends_at, event.ends_at)


class RsvpForEventUITest(EventTestCase):
    def setUp(self):
        super(RsvpForEventUITest, self).setUp()

        self.user2 = User(username='bender',
                          email='bender@planetexpress.nyc',
                          first_name='Bender',
                          last_name='Rodríguez')
        self.user2.set_password('password')
        self.user2.clean_and_save()

        self.event = Event.objects.create(group=self.group,
                                          title="The event",
                                          slug="the-event",
                                          contact_email="a@b.com",
                                          address="123 Main St",
                                          location=Point(0, 0),
                                          max_attendees=100,
                                          begins_at=now(),
                                          ends_at=now())

    @property
    def event_detail_url(self):
        return self.event.get_absolute_url()

    def get_event_page(self):
        self.get(self.event_detail_url)

    def test_rsvp(self):
        self.assertEqual(EventRegistration.objects.all().count(), 0)
        self.login(self.user2.username)
        self.get_event_page()

        self.wait_for_text("RSVP")
        self.click('#rsvp')
        self.wait_for_text("RSVPed")
        self.assertEqual(EventRegistration.objects.all().count(), 1)
        self.assertEqual(EventRegistration.objects.all()[0].user,
                         self.user2)
        self.assertEqual(EventRegistration.objects.all()[0].event,
                         self.event)

    def test_cancel_rsvp(self):
        EventRegistration.objects.create(user=self.user2, event=self.event)

        self.login(self.user2.username)
        self.get_event_page()

        self.wait_for_text("1 / 100")
        self.click('#rsvp')
        self.wait_for_text("0 / 100")
        self.assertEqual(EventRegistration.objects.all().count(), 0)

    def test_group_admin_sees_admin_button(self):
        self.login(self.user.username)
        self.get_event_page()
        self.wait_for_text("Admin")

    def test_user_not_logged_in_can_rsvp(self):
        self.get_event_page()
        self.wait_for_text("0 / 100")
        self.click('#rsvp')
        expected_url = (self.live_server_url + reverse('login') + '?next=' +
                        self.event_detail_url)
        self.assertEqual(expected_url, self.sel.current_url)

        self.wait_for_textbox_then_type('[name="username"]',
                                        self.user2.username)
        self.wait_for_textbox_then_type('[name="password"]', 'password')
        self.click('form input[type="submit"]')

        expected_url = self.live_server_url + self.event_detail_url
        self.assertEqual(expected_url, self.sel.current_url)
        self.wait_for_text("0 / 100")
        self.click('#rsvp')
        self.wait_for_text("1 / 100")

    def test_at_capacity(self):
        self.event.max_attendees = 1
        self.event.save()
        EventRegistration.objects.create(user=self.user, event=self.event)
        self.login(self.user2.username)
        self.get_event_page()
        self.wait_for_text("At Capacity")
        self.click('#rsvp')  # clicking should do nothing
        self.wait_for_text("At Capacity")

    def test_user_not_logged_in_at_capacity(self):
        self.event.max_attendees = 1
        self.event.save()
        EventRegistration.objects.create(user=self.user, event=self.event)
        self.get_event_page()
        self.wait_for_text("At Capacity")
        self.click('#rsvp')  # clicking should do nothing
        self.wait_for_text("At Capacity")
