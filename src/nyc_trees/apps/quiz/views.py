# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.quiz.models import Quiz, quizzes
from apps.quiz.utils import get_quiz_or_404
from apps.users.models import TrainingResult


def quiz_list_page(request):
    return {
        'quizzes': quizzes.iteritems()
    }


def quiz_page(request, quiz_slug):
    quiz = get_quiz_or_404(quiz_slug)
    return {
        'quiz': quiz,
        'quiz_slug': quiz_slug
    }


def complete_quiz(request, quiz_slug):
    quiz = get_quiz_or_404(quiz_slug)

    answers = Quiz.extract_answers(request.POST)
    score = quiz.score(answers)

    result, created = TrainingResult.objects.get_or_create(
        user_id=request.user.id,
        module_name=quiz_slug)

    result.score = max(result.score, score)
    result.save()

    return {
        'quiz': quiz,
        'quiz_slug': quiz_slug,
        'score': score,
        'passed_quiz': score >= quiz.passing_score
    }
