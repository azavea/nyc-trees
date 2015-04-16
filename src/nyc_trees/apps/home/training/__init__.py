# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.home.training.types import (FlatPageTrainingStep,
                                      QuizTrainingStep, TrainingGateway,
                                      Quiz, Question, SingleAnswer,
                                      MultipleAnswer)
from apps.home.training import routes as r

from quiz_strings import QuizStrings as QS

# The keys represent the quiz_slug part of urls.
quizzes = {
    'intro_quiz': Quiz(
        slug='intro_quiz',
        title='Explore Your Knowledge',
        passing_score=7,
        questions=(
            Question(
                text=QS.q1_text,
                correct_markup=QS.q1_correct_markup,
                incorrect_markup=QS.q1_incorrect_markup,
                answer=MultipleAnswer(0, 1, 2),
                choices=(QS.q1_c1, QS.q1_c2, QS.q1_c3, QS.q1_c4)),
            Question(
                text=QS.q2_text,
                correct_markup=QS.q2_correct_markup,
                incorrect_markup=QS.q2_incorrect_markup,
                answer=MultipleAnswer(0, 1, 2),
                choices=(QS.q2_c1, QS.q2_c2, QS.q2_c3)),
            Question(
                text=QS.q3_text,
                correct_markup=QS.q3_correct_markup,
                incorrect_markup=QS.q3_incorrect_markup,
                answer=SingleAnswer(0),
                choices=(QS.q3_c1, QS.q3_c2)),
            Question(
                text=QS.q4_text,
                correct_markup=QS.q4_correct_markup,
                incorrect_markup=QS.q4_incorrect_markup,
                answer=SingleAnswer(3),
                choices=(QS.q4_c1, QS.q4_c2, QS.q4_c3, QS.q4_c4)),
            Question(
                text=QS.q5_text,
                correct_markup=QS.q5_correct_markup,
                incorrect_markup=QS.q5_incorrect_markup,
                answer=SingleAnswer(2),
                choices=(QS.q5_c1, QS.q5_c2, QS.q5_c3, QS.q5_c4)),
            Question(
                text=QS.q6_text,
                correct_markup=QS.q6_correct_markup,
                incorrect_markup=QS.q6_incorrect_markup,
                answer=SingleAnswer(0),
                choices=(QS.q6_c1, QS.q6_c2)),
            Question(
                text=QS.q7_text,
                correct_markup=QS.q7_correct_markup,
                incorrect_markup=QS.q7_incorrect_markup,
                answer=SingleAnswer(0),
                choices=(QS.q7_c1, QS.q7_c2, QS.q7_c3)),
            Question(
                text=QS.q8_text,
                correct_markup=QS.q8_correct_markup,
                incorrect_markup=QS.q8_incorrect_markup,
                answer=SingleAnswer(2),
                choices=(QS.q8_c1, QS.q8_c2, QS.q8_c3)),
            Question(
                text=QS.q9_text,
                correct_markup=QS.q9_correct_markup,
                incorrect_markup=QS.q9_incorrect_markup,
                answer=SingleAnswer(0),
                choices=(QS.q9_c1, QS.q9_c2, QS.q9_c3, QS.q9_c4)),
            Question(
                text=QS.q10_text,
                correct_markup=QS.q10_correct_markup,
                incorrect_markup=QS.q10_incorrect_markup,
                answer=SingleAnswer(1),
                choices=(QS.q10_c1, QS.q10_c2, QS.q10_c3)),
        ))}


# This package attempts to keep all the particulars of training encapsulated,
# such that you can modify how things are wired together in this file without
# digging into the implementation. There are some key exceptions to this:
# * apps.home.urls - imports from this file, gets url params
# * apps.core.models
#   - the user class does a delayed import for a convenience method
#   - the user class has carefully named booleans corresponding
#     to training steps. modify with care.

getting_started = FlatPageTrainingStep('getting_started',
                                       'Getting Started', '20 minutes')
the_mapping_method = FlatPageTrainingStep('the_mapping_method',
                                          'The Mapping Method', '20 minutes')
tree_data = FlatPageTrainingStep('tree_data',
                                 'Tree Data', '20 minutes')
tree_surroundings = FlatPageTrainingStep('tree_surroundings',
                                         'Tree Surroundings', '40 minutes')

intro_quiz = QuizTrainingStep(quizzes['intro_quiz'],
                              r.intro_quiz,
                              'intro_quiz',
                              'Explore Your Knowledge',
                              '30 minutes')

training_summary = TrainingGateway(
    'training_summary',
    r.training_list_page,
    [getting_started,
     the_mapping_method,
     tree_data,
     tree_surroundings,
     intro_quiz])
