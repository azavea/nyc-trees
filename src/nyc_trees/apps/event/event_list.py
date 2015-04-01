# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from collections import OrderedDict

from urllib import urlencode
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from apps.users.models import Follow
from apps.event.models import Event, EventRegistration


class Filter(object):
    def __init__(self, name,
                 empty_template=None,
                 empty_template_url=None,
                 should_show=None):

        # name is used as a string key that gets compared to
        # data sent in via the querystring
        self.name = name

        # a text string to show the user when there are no values
        # for this filter. Must take 0 or 1 '%s' arguments.
        self.empty_template = empty_template or 'No Events'

        # if `empty_template_url` is not None, then empty_template
        # should take one '%s' argument, which will be the redirect
        # url.
        self.empty_template_url = empty_template_url

        # pass in predicate function to enable conditional visibility
        # of this filter
        self.should_show = should_show or (lambda request: True)

    def get_empty_markup(self):
        if self.empty_template_url:
            return self.empty_template % reverse(self.empty_template_url)
        else:
            return self.empty_template

_ALL = Filter('all')
_MAPPING = Filter('mapping')
_TRAINING = Filter('training')
_CURRENT = Filter('current')
_PAST = Filter('past')


class _Filters(object):
    ALL = _ALL.name
    MAPPING = _MAPPING.name
    TRAINING = _TRAINING.name
    CURRENT = _CURRENT.name
    PAST = _PAST.name

    def __getitem__(self, name):
        for f in [_ALL, _MAPPING, _TRAINING, _CURRENT,
                  _PAST, _ATTENDING, _RECOMMENDED]:
            if f.name == name:
                return f
        else:
            return None


class EventList(object):
    """
    Wrap a queryset building function into a workflow that supports
    rendering into pages and reloading asychronously using endpoints
    that return markup.
    """
    trainingFilters = 'training_filter'
    chronoFilters = 'chrono_filters'
    Filters = _Filters()

    @staticmethod
    def get_filterset(name, request):
        right_now = now()
        filtersets = {
            EventList.trainingFilters: OrderedDict([
                (_ALL, None),
                (_MAPPING, lambda qs: qs.filter(includes_training=False)),
                (_TRAINING, lambda qs: qs.filter(includes_training=True)),
            ]),
            EventList.chronoFilters: OrderedDict([
                (_CURRENT, lambda qs: (qs
                                       .filter(ends_at__gte=right_now)
                                       .order_by('begins_at'))),
                (_PAST, lambda qs: (qs
                                    .filter(ends_at__lt=right_now)
                                    .order_by('-begins_at'))),
            ]),
        }
        return filtersets.get(name, {})

    @staticmethod
    def make_event_infos(request, qs):
        """
        Wrap an event object with user-aware data necessary for
        rendering an event row.
        """
        user_registered_event_ids = set(EventRegistration.objects
                                        .filter(user_id=request.user.pk)
                                        .values_list('event_id', flat=True))

        return [{'event': event,
                 'event_share_url': event.get_shareable_url(request),
                 'user_is_registered': event.pk in user_registered_event_ids}
                for event in qs]

    #########################################
    # instance and type configuration
    #########################################

    def __init__(self, qs_builder,
                 name=None,
                 template_path='event/partials/event_list.html',
                 chunk_size=None,
                 active_filter=None, filterset_name=None):

        # a name only needs to be specified when two
        # EventList instances use the same qs_builder
        name = name or qs_builder.__code__.co_name
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'qs_builder', qs_builder)
        object.__setattr__(self, 'template_path', template_path)

        object.__setattr__(self, 'chunk_size', chunk_size)
        object.__setattr__(self, 'active_filter', active_filter)
        object.__setattr__(self, 'filterset_name', filterset_name)

    def __setattr__(self, *args, **kwargs):
        raise TypeError("Mutating this object is too risky because it "
                        "most likely lives the entire length of a thread. "
                        "most needs can be met with `.configure`")

    def configure(self, **kwargs):
        """
        Customize the configuration of an event list for presentation
        on a page.

        Returns a new EventList objects with modified settings.

        This is necessary if the default state of the EventList was
        constructed in some way other than how you intend to present
        it. For example, if the default state of 'foo_events' is a
        chunk_size of 4, but you want to show them all, you can
        specify this with `foo_events.configure(chunk_size=4)`. This
        will prevent mutation of the event list in other cases, but
        allow you to render it with your preferred initial
        presentation.
        """
        # preprocess chunk_size because this is sometimes
        # configured directly from an HTTP request dict.
        if 'chunk_size' in kwargs:
            chunk_size = kwargs['chunk_size']
            if chunk_size is None or chunk_size == 'None':
                chunk_size = None
            else:
                chunk_size = int(chunk_size)
            kwargs['chunk_size'] = chunk_size

        newkwargs = {key: (kwargs[key] if key in kwargs
                           else getattr(self, key))
                     for key in
                     ('chunk_size', 'active_filter', 'filterset_name')}
        return EventList(self.qs_builder,
                         name=self.name,
                         template_path=self.template_path,
                         **newkwargs)

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function directly, returning a queryset.
        """
        return self.qs_builder(*args, **kwargs)

    #########################################
    # methods for exposing url endpoints
    #########################################

    def url_name(self):
        return self.name + '_partial'

    def endpoint(self, *args, **kwargs):
        """
        The endpoint used to render a partial.
        """
        return render_to_response(
            self.template_path,
            {'event_list': self.as_context(*args, **kwargs)})

    #########################################
    # event list control management
    #########################################

    def _control_url(self, show_all, *args, **kwargs):
        params = {
            'chunk_size': self.chunk_size,
            'active_filter': self.active_filter,
            'filterset_name': self.filterset_name
        }

        if show_all:
            params['show_all'] = True
        url = reverse(self.url_name(), args=args, kwargs=kwargs)
        return '%s?%s' % (url, urlencode(params))

    def as_context(self, request, *args, **kwargs):
        results = self.qs_builder(request, *args, **kwargs)

        if isinstance(results, tuple):
            qs, extra_context = results
        else:
            qs, extra_context = results, {}

        event_list = self.configure(**request.GET.dict())

        filterset = event_list.get_filterset(
            event_list.filterset_name, request)

        filter_fn = filterset.get(self.Filters[event_list.active_filter])

        if filter_fn:
            qs = filter_fn(qs)

        if ((request.GET.get('show_all') or
             event_list.chunk_size is None or
             qs.count() <= event_list.chunk_size)):
            load_more_url = None
        else:
            qs = qs[:event_list.chunk_size]
            load_more_url = event_list._control_url(
                show_all=True, *args, **kwargs)

        filters = ([{'name': k.name,
                     'active': k.name == event_list.active_filter,
                     'no_result_markup': k.get_empty_markup(),
                     'url': (event_list
                             .configure(active_filter=k.name)
                             ._control_url(show_all=False, *args, **kwargs))}
                    for k in filterset.keys()
                    if k.should_show(request)])

        context = {
            'filters': filters,
            'load_more_url': load_more_url,
            'event_infos': event_list.make_event_infos(request, qs),
        }

        context.update(extra_context)

        return context


#########################################
# event_list functions
#########################################
#
# Add your event_list constructors here.
#
# Write a function that takes a request and returns a
# queryset. Decorate it with `@EventList` and it is ready to be used
# as an endpoint for rendering a partial, or a context for use in a
# page delivered by the server.
#

@EventList
def immediate_events(request):
    user = request.user
    seven_days = relativedelta(days=7)
    nowish = (Event.objects
              .filter(is_private=False,
                      group__is_active=True,
                      ends_at__gt=now(),
                      ends_at__lte=now() + seven_days)
              .order_by('begins_at'))

    if user.is_authenticated():
        follows = Follow.objects.filter(user_id=user.id)
        groups = follows.values_list('group', flat=True)
        immediate_events = nowish.filter(group_id__in=groups)
    else:
        immediate_events = nowish.none()

    return immediate_events


@EventList
def all_events(request):
    return Event.objects.filter(is_private=False,
                                group__is_active=True,
                                ends_at__gt=now()).order_by('begins_at')
