# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.test import TestCase

from apps.core.test_utils import make_request
from apps.geocode.views import geocode


class GeocodeTestCase(TestCase):
    def assert_candidate_exists_for(self, address):
        params = {'address': address}
        response = geocode(make_request(params=params))
        self.assertTrue('candidates' in response,
                        'Expected the response to be a dict with a '
                        '"candidates" key')
        self.assertTrue(len(response['candidates']) > 0, 'Expected '
                        'at least 1 candidate in the response')

    def test_geocoder_returns_a_response_without_borough(self):
        self.assert_candidate_exists_for('416 Lorimer St')

    def test_geocoder_returns_a_response_with_borough(self):
        self.assert_candidate_exists_for('416 Lorimer St Brooklyn')
