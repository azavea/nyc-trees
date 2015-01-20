# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.test import TestCase


class TrainingTrackingTest(TestCase):
    def test_visit_marks_boolean_true(self):
        """assert that any successful view function, when wrapped with
        the decorator, will mark the associated boolean"""
        pass

    def test_flat_page_marks_boolean_true(self):
        """like above, but test the flat page redirect in particular,
        with a freshly created flat page"""
        pass

    def test_404_does_not_mark(self):
        """assert that any failed view function, when wrapped with
        the decorator, will not mark the associated boolean"""
        pass

    def test_flat_page_404_does_not_mark(self):
        """like above, but test the flat page redirect in particular,
        with a nonexistent flatpage"""
        pass
