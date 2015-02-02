# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.test import TestCase
from django.http import Http404
from django.conf import settings

from django.contrib.flatpages.models import FlatPage

from django_tinsel.utils import decorate as do

from apps.core.models import User
from apps.core.test_utils import make_request
from apps.home.training.decorators import mark_user, render_flatpage
from apps.home.training.types import Quiz, Question


class TrainingTrackingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='foo')
        self.request = make_request(user=self.user)

    def requery_user(self):
        self.user = User.objects.get(id=self.user.pk)

    def test_visit_marks_boolean_true(self):
        """assert that any successful view function, when wrapped with
        the decorator, will mark the associated boolean"""
        view = lambda request: {}
        wrapped_view = do(mark_user('is_banned'),
                          view)

        self.assertFalse(self.user.is_banned)
        view(self.request)
        self.assertFalse(self.user.is_banned)
        wrapped_view(self.request)
        self.assertTrue(self.user.is_banned)

    def test_flatpage_marks_boolean_true(self):
        """like above, but test the flat page redirect in particular,
        with a freshly created flat page"""
        view = render_flatpage('/foo/')
        wrapped_view = do(mark_user('is_banned'),
                          view)

        fp = FlatPage.objects.create(url='/foo/',
                                     content='<p>foo</p>')
        fp.sites.add(settings.SITE_ID)

        self.assertFalse(self.user.is_banned)
        view(self.request)
        self.assertFalse(self.user.is_banned)
        wrapped_view(self.request)
        self.assertTrue(self.user.is_banned)

    def test_404_does_not_mark(self):
        """assert that any failed view function, when wrapped with
        the decorator, will not mark the associated boolean"""
        def view(*args, **kwargs):
            raise Http404()
        wrapped_view = do(
            mark_user('is_banned'),
            view)

        self.assertFalse(self.user.is_banned)
        with self.assertRaises(Http404):
            view(self.request)
        self.assertFalse(self.user.is_banned)
        with self.assertRaises(Http404):
            wrapped_view(self.request)

        # a wrinkle - the transaction successfully rolled back, so the
        # database is correct, but the rr-cycle will be in a not-awesome
        # state unless the user is requeried. for the common use case,
        # this will not be a problem.
        self.assertTrue(self.user.is_banned)
        self.requery_user()
        self.assertFalse(self.user.is_banned)

    def test_flatpage_404_does_not_mark(self):
        """like above, but test the flat page redirect in particular,
        with a nonexistent flatpage"""
        view = render_flatpage('/DOESNOTEXIST/')
        wrapped_view = do(
            mark_user('is_banned'),
            view)

        self.assertFalse(self.user.is_banned)
        with self.assertRaises(Http404):
            view(self.request)
        self.assertFalse(self.user.is_banned)
        with self.assertRaises(Http404):
            wrapped_view(self.request)

        self.requery_user()
        self.assertFalse(self.user.is_banned)


class QuizTestCase(TestCase):
    def test_quiz_assertions(self):
        # Must be at least one question
        with self.assertRaises(AssertionError):
            Quiz(title='Test quiz', passing_score=0, questions=[])

        # Passing score must be <= number of questions
        with self.assertRaises(AssertionError):
            Quiz(title='Test quiz', passing_score=2, questions=['A'])

        # Must be at least one choice
        with self.assertRaises(AssertionError):
            Question(text='A', answer=0, choices=[])

        # Answer must be > 0
        with self.assertRaises(AssertionError):
            Question(text='A', answer=-1, choices=['A'])

        # Answer must be <= number of choices
        with self.assertRaises(AssertionError):
            Question(text='A', answer=2, choices=['A'])

    def test_quiz_score(self):
        quiz = Quiz(
            title='Test quiz',
            passing_score=1,
            questions=(
                Question(
                    text='Which one?',
                    answer=0,
                    choices=('A', 'B')),
                Question(
                    text='Which one?',
                    answer=1,
                    choices=('A', 'B'))))

        self.assertEqual(0, quiz.score({}))
        self.assertEqual(0, quiz.score({98: 0, 99: 1}))
        self.assertEqual(0, quiz.score({0:  1, 1: 0}))
        self.assertEqual(1, quiz.score({0:  0, 1: 0}))
        self.assertEqual(2, quiz.score({0:  0, 1: 1}))

    def test_quiz_extract_answers(self):
        post_fields = {
            'foo': ['bar'],
            'foo.bar': 'baz',
            'question.0': [1],
            'question.99': [2]
        }
        self.assertEqual({0: 1, 99: 2},
                         Quiz.extract_answers(post_fields))
