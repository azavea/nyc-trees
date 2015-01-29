# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import transaction

from apps.quiz.models import Quiz
from apps.quiz.utils import get_quiz_or_404
from apps.users.models import TrainingResult


def quiz_page(request, quiz_slug):
    quiz = get_quiz_or_404(quiz_slug)
    return {
        'quiz': quiz,
        'quiz_slug': quiz_slug
    }


@transaction.atomic
def complete_quiz(request, quiz_slug):
    quiz = get_quiz_or_404(quiz_slug)
    user = request.user

    answers = Quiz.extract_answers(request.POST)
    score = quiz.score(answers)

    result, created = TrainingResult.objects.get_or_create(
        user_id=user.id,
        module_name=quiz_slug)

    result.score = max(result.score, score)
    result.save()

    passed_quiz = (score >= quiz.passing_score)

    passed_quiz_bool = 'training_finished_%s' % quiz_slug
    if passed_quiz and getattr(user, passed_quiz_bool) is False:
        setattr(user, passed_quiz_bool, True)
        user.save()

    return {
        'quiz': quiz,
        'quiz_slug': quiz_slug,
        'score': score,
        'passed_quiz': passed_quiz,
    }
