# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from urllib import urlencode
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from apps.users.models import Follow
from apps.event.models import Event, EventRegistration


class EventList(object):
    """
    Wrap a queryset building function into a workflow that supports
    rendering into pages and reloading asychronously using endpoints
    that return markup.
    """

    @staticmethod
    def simple_context(request, qs):
        """
        Render an Event queryset as an event_list context.

        Useful for cases where you don't need post-back controls and
        don't want to bother creating an EventList instance.
        """
        return {'event_infos': EventList.make_event_infos(request, qs),
                'filters': None,
                'load_more_url': None}

    @staticmethod
    def render_singleton(context):
        """
        Render a single event_list context as html.

        When event_lists are added to pages, they require post-back to
        toggle their filters or load more chunks. This markup is
        delivered using this function.
        """
        return render_to_response('event/partials/event_list.html',
                                  {'event_list': context})

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
                 'user_is_registered': event.pk in user_registered_event_ids}
                for event in qs]

    #########################################
    # instance and type configuration
    #########################################

    def __init__(self, qs_builder,
                 chunk_size=None, show_filters=False):
        object.__setattr__(self, 'name', qs_builder.__code__.co_name)
        object.__setattr__(self, 'qs_builder', qs_builder)
        object.__setattr__(self, 'chunk_size', chunk_size)
        object.__setattr__(self, 'show_filters', show_filters)

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
        return EventList(self.qs_builder, **kwargs)

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
        return self.render_singleton(self.as_context(*args, **kwargs))

    #########################################
    # event list control management
    #########################################

    def as_context(self, request):
        qs = self.qs_builder(request)
        filter_type = request.GET.get('filter_type')

        # filters will be shown if the event_list is configured to show
        # filters, or if a request is sent with a filter activated.
        if filter_type == 'training':
            qs = qs.filter(includes_training=True)
            show_filters = True
        elif filter_type == 'mapping':
            qs = qs.filter(includes_training=False)
            show_filters = True
        elif filter_type == 'all' or self.show_filters:
            filter_type = 'all'
            show_filters = True
        else:
            show_filters = False

        if self.chunk_size and qs.count() > self.chunk_size:
            qs = qs[:self.chunk_size]
            load_more_url = reverse(self.url_name())
        else:
            load_more_url = None

        filters = ([{'name': k,
                     'active': k == filter_type,
                     'url': '%s?%s' % (reverse(self.url_name()),
                                       urlencode({'filter_type': k}))}
                    for k in ('all', 'training', 'mapping')]
                   if show_filters else [])

        return {
            'filters': filters,
            'load_more_url': load_more_url,
            'event_infos': self.make_event_infos(request, qs),
        }


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
                      begins_at__gte=now() - seven_days,
                      begins_at__lte=now() + seven_days)
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
    return Event.objects.filter(is_private=False).order_by('begins_at')
