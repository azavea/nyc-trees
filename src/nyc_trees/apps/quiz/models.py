# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


class Quiz(object):
    """
    title - string
    questions - iterable<Question>
    passing_score - int; How many correct answers are needed to pass the quiz
    """
    def __init__(self, title, questions, passing_score):
        assert passing_score <= len(questions)
        self.title = unicode(title)
        self.questions = list(questions)
        self.passing_score = int(passing_score)

    @classmethod
    def extract_answers(cls, post_fields):
        """
        Return dict of {question_index => answer_index, ...} from post fields.
        post_fields - QueryDict; Probably from request.POST
        """
        result = []
        for field_name, values in post_fields.iteritems():
            # Parse field name format like "question.1", "question.2", etc.
            parts = field_name.split('.')
            if len(parts) == 2:
                try:
                    value = int(values[0])
                    question_index = int(parts[1])
                    result.append((question_index, value))
                except ValueError:
                    pass
        return dict(result)

    def score(self, answers):
        """
        How many correct answers are selected?
        answers - dict of {question_index => answer_index, ...}
        """
        result = 0
        for i, question in enumerate(self.questions):
            if answers.get(i, -1) == question.answer:
                result += 1
        return result


class Question(object):
    """
    text - string
    answer - int; Index of the correct answer in choices iterable
    choices - iterable<string>
    """
    def __init__(self, text, answer, choices):
        assert answer >= 0
        assert answer < len(choices)
        self.text = unicode(text)
        self.answer = int(answer)
        self.choices = list(choices)


# The keys represent the quiz_slug part of urls.
quizzes = {
    'intro_quiz': Quiz(
        title='Introduction Quiz',
        passing_score=2,
        questions=(
            Question(
                text='Lorem ipsum dolor sit amet, consectetur '
                     'adipiscing elit?',
                answer=0,
                choices=('Answer A', 'Answer B', 'Answer C')),
            Question(
                text='Lorem ipsum dolor sit amet, consectetur '
                     'adipiscing elit?',
                answer=1,
                choices=('Answer A', 'Answer B', 'Answer C')),
            Question(
                text='Lorem ipsum dolor sit amet, consectetur '
                     'adipiscing elit?',
                answer=2,
                choices=('Answer A', 'Answer B', 'Answer C')),
        )
    )
}
