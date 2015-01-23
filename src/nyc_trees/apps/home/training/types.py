# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse
from django_tinsel.decorators import route
from django_tinsel.utils import decorate as do
from apps.home.training.decorators import render_flatpage, mark_user

_PURE_URL_NAME_TEMPLATE = '%s_pure'
_MARK_PROGRESS_URL_NAME_TEMPLATE = '%s_mark_progress'
_TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE = 'training_finished_%s'
_FLATPAGE_VIEW = 'django.contrib.flatpages.views.flatpage'


class AbstractTrainingStep(object):
    def pure_kwargs(self):
        """
        This dictionary, when given as a **kwarg argument to a
        `url()` function call, produce an endpoint that will render
        the associated training step without marking progress on
        any previously visited page. This is necessary
        """
        raise NotImplementedError()

    def mark_kwargs(self):
        """
        This dictionary, when given as a **kwarg argument to a
        `url()` function call, produce an endpoint that will mark progress
        for the associated boolean when visited.
        """
        raise NotImplementedError()

    def is_complete(self):
        raise NotImplementedError()

    def is_flatpage(self):
        """
        TODO: refactor into classes,
        `FlatPageTrainingStep` and `ViewTrainingStep`
        """
        raise NotImplementedError()


class TrainingGateway(AbstractTrainingStep):
    """
    A TrainingGateway is a doubly-linked list of step objects.

    TrainingGateway is step-like, allowing the list of steps to
    function as a cycle, so that no step need function as a terminal
    node. This is important because individual steps need to point to
    a next and/or previous step in order to build a 'mark_progress'
    url, a URL to another page that indicates the current page has
    been completed.

    A TrainingGateway is the main interface by which the rest of the
    application should talk to the training workflow. Where possible,
    TrainingStep objects should not be referenced directly.
    """
    def __init__(self, name, view, steps):
        # read the step array and link the end nodes into
        # a cycle through the training gateway
        first_step, last_step = steps[0], steps[-1]
        self.previous_step = last_step
        self.next_step = first_step

        # read the step array and link non-end nodes together
        # bi-directionally
        first_step.previous_step = self
        for i, step in enumerate(steps):
            if i > 0:
                step.previous_step = steps[i - 1]
            if i < len(steps) - 1:
                step.next_step = steps[i + 1]
        for i in range(1, len(steps) - 1):
            steps[i].previous_step = steps[i-1]
            steps[i].next_step = steps[i+1]
        last_step.next_step = self

        self.name = name
        self.view = view
        self.steps = steps

    def is_flatpage(self):
        return False

    def get_step(self, name):
        for step in self.steps:
            if step.name == name:
                return step
        raise ValueError()

    def is_complete(self, user):
        return all([step.is_complete(user) for step in self.steps])

    def get_context(self, user):
        last_was_complete = True
        next_step = None

        training_steps = []
        for step in self.steps:
            is_complete = step.is_complete(user)
            if next_step is None and last_was_complete and not is_complete:
                next_step = step
                is_next = True
            else:
                is_next = False
            training_steps.append({'step': step,
                                   'is_complete': is_complete,
                                   'is_next': is_next})
            last_was_complete = is_complete

        return training_steps

    def pure_kwargs(self):
        return {'name': '%s_pure' % self.name, 'view': self.view}

    def mark_kwargs(self):
        raise ValueError('Gateways do not have a progress boolean')


class TrainingStep(AbstractTrainingStep):
    def __init__(self, name, description, duration, view=None):
        self.name = name
        self.description = description
        self.duration = duration
        self.next_step = None
        self.previous_step = None
        self.view = view or _FLATPAGE_VIEW

    def is_flatpage(self):
        return self.view == _FLATPAGE_VIEW

    def pure_url(self):
        return reverse(_PURE_URL_NAME_TEMPLATE % self.name)

    def mark_progress_url(self):
        return reverse(_MARK_PROGRESS_URL_NAME_TEMPLATE % self.name)

    def pure_kwargs(self):
        kwargs = {'url': '/%s/' % self.name} if self.is_flatpage() else {}
        return {'name': _PURE_URL_NAME_TEMPLATE % self.name,
                'view': self.view,
                'kwargs': kwargs}

    def mark_kwargs(self):
        inner_view = (render_flatpage('/%s/' % self.next_step.name)
                      if self.next_step.is_flatpage() else self.next_step.view)
        view = route(GET=do(
            mark_user(_TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE % self.name),
            inner_view))
        return {'name': _MARK_PROGRESS_URL_NAME_TEMPLATE % self.name,
                'view': view}

    def is_complete(self, user):
        return getattr(user,
                       _TRAINING_FINISHED_BOOLEAN_FIELD_TEMPLATE % self.name,
                       False)

    def __str__(self):
        return self.name
