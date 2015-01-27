# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.http import Http404

from apps.quiz.models import quizzes


def get_quiz_or_404(quiz_slug):
    try:
        return quizzes[quiz_slug]
    except KeyError:
        raise Http404()
