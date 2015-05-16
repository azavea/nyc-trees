# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from cStringIO import StringIO

from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import Point
from django.test import RequestFactory
from django.utils.timezone import now

from apps.users.models import TrustedMapper

from apps.event.models import Event
from apps.survey.models import (BlockfaceReservation, Territory,
                                Survey, Tree, Species)


def make_request(params={}, user=None, method='GET', body=None, file=None,
                 group=None, **extra):
    if user is None:
        user = AnonymousUser()

    if not extra:
        extra = {}
    if body:
        body_stream = StringIO(body)
        extra['wsgi.input'] = body_stream
        extra['CONTENT_LENGTH'] = len(body)

    if file:
        post_data = {'file': file}
        req = RequestFactory().post("hello/world", post_data, **extra)
    elif method == 'POST':
        req = RequestFactory().post("hello/world", params, **extra)
    else:
        req = RequestFactory().get("hello/world", params, **extra)
        req.method = method

    setattr(req, 'user', user)
    setattr(req, 'group', group)

    return req


def make_event(group, **kwargs):
    right_now = now()
    defaults = {
        'group': group,
        'title': "The event",
        'contact_email': "a@b.com",
        'address': "123 Main St",
        'location': Point(-73.9679007, 40.7764977),
        'max_attendees': 100,
        'begins_at': right_now,
        'ends_at': right_now + timedelta(hours=1),
    }
    defaults.update(kwargs)

    e = Event(**defaults)
    e.clean_and_save()

    return e


def survey_defaults():
    return {
        'has_trees': True,
        'is_left_side': False,
        'is_mapped_in_blockface_polyline_direction': True,
        }


def make_survey(user, blockface, **kwargs):
    defaults = survey_defaults()
    defaults['user_id'] = user.id
    defaults['blockface_id'] = blockface.id
    defaults.update(kwargs)

    s = Survey(**defaults)
    s.full_clean()
    s.save()

    return s


def tree_defaults():
    return {
        'circumference': 1,
        'distance_to_tree': 1,
        'curb_location': 'OnCurb',
        'status': 'Alive',
        'species_certainty': 'Yes',
        'health': 'Good',
        'stewardship': 'None',
        'guards': 'None',
        'sidewalk_damage': 'NoDamage',
        'problems': 'Stones,Sneakers',
    }


def make_tree(survey, **kwargs):
    defaults = tree_defaults()
    defaults['survey'] = survey
    defaults.update(kwargs)

    t = Tree(**defaults)
    t.clean_and_save()

    return t


def make_species(**kwargs):
    defaults = {
        'forms_id': '123',
        'species_code': 'BDL',
        'scientific_name': 'Ulmus Americanan',
        'common_name': 'Elm'
    }
    defaults.update(kwargs)

    s = Species(**defaults)
    s.clean_and_save()

    return s


def make_territory(group, block):
    return Territory.objects.create(group=group, blockface=block)


def make_trusted_mapper(user, group, **kwargs):
    defaults = {
        'user': user,
        'group': group,
        'is_approved': True,
    }
    defaults.update(kwargs)
    return TrustedMapper.objects.create(**defaults)


def make_reservation(user, block, **kwargs):
    defaults = {
        'user': user,
        'blockface': block,
        'is_mapping_with_paper': False,
        'expires_at': now() + timedelta(days=1),
        'created_at': now(),
        'updated_at': now(),
    }
    defaults.update(kwargs)
    return BlockfaceReservation.objects.create(**defaults)


def complete_online_training(user):
    user.training_finished_getting_started = True
    user.training_finished_the_mapping_method = True
    user.training_finished_tree_data = True
    user.training_finished_tree_surroundings = True
    user.training_finished_wrapping_up = True
    user.training_finished_intro_quiz = True
    user.training_finished_groups_to_follow = True
    user.clean_and_save()
