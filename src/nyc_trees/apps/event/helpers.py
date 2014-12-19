from apps.event.models import EventRegistration


def user_is_rsvped_for_event(user, event):
    # The filter uses user.id so that the user argument can be either
    # a real User or the anonymous user (not logged in). The anonymous
    # user is a SimpleLazyObject, which you cannot use in a filter.
    return EventRegistration.objects\
                            .filter(user=user.id, event=event)\
                            .count() > 0
