# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from waffle.models import Flag

from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase

from apps.core.models import User
from apps.core.test_utils import make_request, make_survey
from apps.survey.models import Blockface

from nyc_trees.context_processors import config


class ContextProcessorTest(TestCase):
    def setUp(self):
        Flag.objects.create(name='full_access', everyone=True)

        self.user = User.objects.create(
            username='pat',
            email='pat@rat.com'
        )
        self.blockface = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        self.survey = make_survey(self.user, self.blockface)

    def test_full_request(self):
        context = config(make_request())
        self.assertTrue('nyc_bounds' in context,
                        'Expected the context dict to have a "nyc_bounds" '
                        'key.')

    def test_ajax_request(self):
        context = config(make_request(
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertEquals({}, context,
                          'Expected the context to be an empty dict when the '
                          'HTTP_X_REQUESTED_WITH header is set to '
                          '"XMLHttpRequest"')
