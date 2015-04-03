# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from waffle.models import Flag

from django.test import TestCase
from django.http import Http404, QueryDict
from django.conf import settings

from django.contrib.auth.models import AnonymousUser
from django.contrib.flatpages.models import FlatPage

from django_tinsel.utils import decorate as do

from apps.core.models import User
from apps.core.test_utils import make_request
from apps.home.training.decorators import mark_user, render_flatpage
from apps.home.training.types import (Quiz, Question, SingleAnswer,
                                      MultipleAnswer)
from apps.home.routes import home_page
from apps.users.tests import UsersTestCase


class TrainingTrackingTest(TestCase):
    def setUp(self):
        Flag.objects.create(name='full_access', everyone=True)

        self.user = User.objects.create(username='foo')
        self.request = make_request(user=self.user)

    def requery_user(self):
        self.user = User.objects.get(id=self.user.pk)

    def test_visit_marks_boolean_true(self):
        """assert that any successful view function, when wrapped with
        the decorator, will mark the associated boolean"""
        def view(request):
            return {}
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
    def setUp(self):
        Flag.objects.create(name='full_access', everyone=True)

    def test_quiz_assertions(self):
        # Must be at least one question
        with self.assertRaises(AssertionError):
            Quiz(title='Test quiz', passing_score=0, questions=[])

        # Passing score must be <= number of questions
        with self.assertRaises(AssertionError):
            Quiz(title='Test quiz', passing_score=2, questions=['A'])

    def test_question_assertions(self):
        # Must be at least one choice
        with self.assertRaises(AssertionError):
            Question(text='A', answer=SingleAnswer(0), choices=[])

        # Answer must be > 0
        with self.assertRaises(AssertionError):
            Question(text='A', answer=SingleAnswer(-1), choices=['A'])

        # Answer must be <= number of choices
        with self.assertRaises(AssertionError):
            Question(text='A', answer=SingleAnswer(2), choices=['A'])

    def test_multichoice_assertions(self):
        # Must be at least one choice
        with self.assertRaises(AssertionError):
            Question(text='A', answer=MultipleAnswer(), choices=[])

        # Answer must be > 0
        with self.assertRaises(AssertionError):
            Question(text='A', answer=MultipleAnswer(0, -1), choices=['A'])

        # Answer must be <= number of choices
        with self.assertRaises(AssertionError):
            Question(text='A', answer=MultipleAnswer(0, 2), choices=['A'])

    def test_quiz_score(self):
        quiz = Quiz(
            title='Test quiz',
            passing_score=1,
            questions=(
                Question(
                    text='Which one?',
                    answer=SingleAnswer(0),
                    choices=('A', 'B')),
                Question(
                    text='Which one?',
                    answer=MultipleAnswer(0, 1),
                    choices=('A', 'B'))))

        self.assertEqual(0, quiz.score({}))
        self.assertEqual(0, quiz.score({98: [0],
                                        99: [1]}))
        self.assertEqual(0, quiz.score({0: [1],
                                        1: [0]}))
        self.assertEqual(1, quiz.score({0: [0],
                                        1: [0]}))
        self.assertEqual(2, quiz.score({0: [0],
                                        1: [0, 1]}))

    def test_quiz_extract_answers(self):
        post_fields = QueryDict('foo=bar'
                                '&foo.bar=baz'
                                '&question.0=1'
                                '&question.0=2'
                                '&question.99=2')
        self.assertEqual({0: [1, 2], 99: [2]},
                         Quiz.extract_answers(post_fields))


class HomeTestCase(UsersTestCase):

    class HomePageTestResponse(object):
        def __init__(self, test, response):
            self.test = test
            self.response = response

        def _assertContains(self, text, it_is):
            count = 1 if it_is else 0
            self.test.assertContains(self.response, text, count=count)

        def assert_training_visible(self, it_is):
            self._assertContains('Continue your training', it_is)

        def assert_about_visible(self, it_is):
            self._assertContains(
                '<section class="section-about">', it_is)

        def assert_progress_visible(self, it_is):
            self._assertContains(
                '<div class="progress-circles', it_is)

        def assert_achievements_visible(self, it_is):
            self._assertContains(
                '<section class="achievements"', it_is)

    def _render_homepage(self, user=None):
        if not user:
            user = AnonymousUser()
        request = make_request(user=user)
        return self.HomePageTestResponse(self, home_page(request))

    def _complete_user_online_training(self):
        for f in ['training_finished_getting_started',
                  'training_finished_the_mapping_method',
                  'training_finished_tree_data',
                  'training_finished_tree_surroundings',
                  'training_finished_intro_quiz',
                  'training_finished_groups_to_follow']:
            setattr(self.user, f, True)
        self.user.save()

    def test_public_homepage_content(self):
        response = self._render_homepage()
        response.assert_about_visible(True)
        response.assert_training_visible(False)
        response.assert_progress_visible(True)

    def test_untrained_user_content(self):
        response = self._render_homepage(self.user)
        response.assert_about_visible(False)
        response.assert_training_visible(True)
        response.assert_achievements_visible(False)

    def test_online_trained_user_content(self):
        self._complete_user_online_training()
        response = self._render_homepage(self.user)
        response.assert_about_visible(False)
        response.assert_training_visible(False)
        response.assert_achievements_visible(True)
