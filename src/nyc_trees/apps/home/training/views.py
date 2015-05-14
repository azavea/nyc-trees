# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import transaction

from apps.home.training.utils import get_quiz_or_404
from apps.users.models import TrainingResult

from apps.mail.views import send_online_training_complete


def training_list_page(request):
    from apps.home.training import training_summary
    return training_summary.get_context(request.user)


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
    correct_answers = list(quiz.correct_answers(answers))
    quiz_summary = list(_quiz_summary(quiz, answers))

    # set the quiz as finished upon *reaching* success confirmation,
    # not clicking 'Finish'. We're breaking the pattern of the training
    # tracking workflow here intentionally, to avoid someone finishing
    # the quiz and not receiving credit.
    #
    # note that both the TrainingResult creation and the user boolean
    # flipping are required for this step to be considered done.

    result, training_result_created = TrainingResult.objects.get_or_create(
        user_id=user.id,
        module_name=quiz_slug)

    best_score = max(result.score, score)
    result.score = best_score
    result.save()

    passed_quiz = (score >= quiz.passing_score)

    passed_quiz_bool = 'training_finished_%s' % quiz_slug
    if passed_quiz and getattr(user, passed_quiz_bool) is False:
        first_time_passing = True
        setattr(user, passed_quiz_bool, True)
        user.save()
    else:
        first_time_passing = False

    if first_time_passing and training_result_created:
        send_online_training_complete(user)

    return {
        'user': request.user,
        'quiz': quiz,
        'quiz_slug': quiz_slug,
        'quiz_summary': quiz_summary,
        'score': score,
        'best_score': best_score,
        'passed_quiz': passed_quiz,
        'correct_answers': correct_answers
    }


def _quiz_summary(quiz, submitted_answers):
    for i, question in enumerate(quiz.questions):
        candidate = submitted_answers[i]
        yield {
            'question': question,
            'submitted_answers': [ans for i, ans in enumerate(question.choices)
                                  if i in candidate],
            'is_correct': question.is_correct(candidate)
        }


def training_instructions(request):
    user = request.user
    step1_complete = False
    step2_complete = False
    if user.is_authenticated():
        step1_complete = user.online_training_complete
        step2_complete = step1_complete and user.field_training_complete
    return {
        'step1_complete': step1_complete,
        'step2_complete': step2_complete,
    }
