# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import transaction

from apps.home.training.utils import get_quiz_or_404
from apps.users.views.group import group_list_page
from apps.users.models import TrainingResult


def groups_to_follow(request):
    ctx = group_list_page(request)
    ctx.update({'chunk_size': 2})
    return ctx


def training_list_page(request):
    from apps.home.training import training_summary
    return {'training_steps': training_summary.get_context(request.user)}


def intro_quiz(request):
    quiz_slug = 'intro_quiz'
    quiz = get_quiz_or_404(quiz_slug)
    return {
        'quiz': quiz,
        'quiz_slug': quiz_slug
    }


@transaction.atomic
def complete_quiz(request):
    from apps.home.training.types import Quiz
    quiz_slug = 'intro_quiz'
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
