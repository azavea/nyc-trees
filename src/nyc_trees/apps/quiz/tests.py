# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.test import TestCase

from apps.quiz.models import Quiz, Question


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
