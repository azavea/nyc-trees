from apps.event.models import EventRegistration


def user_is_rsvped_for_event(user, event):
    if not user.is_authenticated():
        return False
    # Group admins are implicitly RSVPd to their own events.
    if event.group.admin == user:
        return True
    return EventRegistration.objects.filter(user=user, event=event).exists()


def user_is_checked_in_to_event(user, event):
    """Return True if user is checked-in to event"""
    if not user.is_authenticated():
        return False
    # Group admins are implicitly RSVPd to their own events.
    if event.group.admin == user:
        return True
    return EventRegistration.objects.filter(user=user,
                                            event=event,
                                            did_attend=True).exists()
