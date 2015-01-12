# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase

from apps.core.models import User
from apps.core.test_utils import make_request
from apps.survey.models import Blockface, Survey

from nyc_trees.context_processors import tiler_cache_busters


class CacheBustersContextProcessorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='pat',
            email='pat@rat.com'
        )
        self.blockface = Blockface.objects.create(
            geom=MultiLineString(LineString(((0, 0), (1, 1))))
        )
        self.survey = Survey.objects.create(user=self.user,
                                            blockface=self.blockface)

    def test_full_request(self):
        context = tiler_cache_busters(make_request())
        self.assertTrue('cache_buster' in context,
                        'Expected the context to have a "cache_buster" key.')
        self.assertTrue('progress' in context['cache_buster'],
                        'Expected the "cache_buster" dict to have a '
                        '"progress" key.')
        self.assertTrue(context['cache_buster']['progress'],
                        'Expected the "progress" key of the "cache_buster" '
                        'dict to be truthy.')

    def test_ajax_request(self):
        context = tiler_cache_busters(make_request(
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertFalse('cache_buster' in context,
                         'Expected the context to not have a "cache_buster" '
                         'key when the HTTP_X_REQUESTED_WITH header is set '
                         'to "XMLHttpRequest"')
