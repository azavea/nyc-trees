# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from datetime import timedelta

from django.core.urlresolvers import reverse
from django.http import (Http404, HttpResponseRedirect, HttpResponseBadRequest,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from apps.core.models import User
from apps.event.models import EventRegistration
from apps.users import user_profile_context, get_privacy_categories
from apps.users.forms import ProfileSettingsForm, EventRegistrationFormSet, \
    PrivacySettingsForm

USER_SETTINGS_PRIVACY_TAB_ID = 'privacy-pane'


# TODO: make a route?
def user_detail_redirect(request):
    return HttpResponseRedirect(
        reverse('user_detail', kwargs={'username': request.user.username}))


def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    its_me = (user.id == request.user.id)

    if not its_me and not user.profile_is_public:
        # Private profile acts like a missing page to others
        raise Http404()

    return user_profile_context(user, its_me=its_me, home_page=False)


def profile_settings(request):
    user = request.user
    privacy_form = PrivacySettingsForm(instance=user)
    profile_form = ProfileSettingsForm(instance=user, label_suffix='')
    profile_form.fields['opt_in_stewardship_info'].label = ''

    a_week_ago = timezone.now().date() - timedelta(days=7)
    events = EventRegistration.objects \
        .filter(event__begins_at__gt=a_week_ago) \
        .order_by('event__begins_at')
    event_formset = EventRegistrationFormSet(
        instance=user, queryset=events)

    context = {
        'profile_form': profile_form,
        'privacy_form': privacy_form,
        'event_formset': event_formset,
        'privacy_categories': get_privacy_categories(privacy_form),
        'username': request.user.username,
        'user_settings_privacy_tab_id': USER_SETTINGS_PRIVACY_TAB_ID,
    }
    return context


def update_profile_settings(request):
    user = request.user
    profile_form = ProfileSettingsForm(request.POST, instance=user)
    privacy_form = PrivacySettingsForm(request.POST, instance=user)
    event_formset = EventRegistrationFormSet(request.POST, instance=user)

    if privacy_form.is_valid():
        privacy_form.save()
    else:
        # Client-side code should prevent making invalid privacy settings,
        # so the view does not use the standard form validation workflow.
        return HttpResponseBadRequest('The requested privacy settings '
                                      'are invalid')

    # It's not possible to create invalid data with this form,
    # so don't check form.is_valid()
    profile_form.save()
    event_formset.save()

    return profile_settings(request)


def set_privacy(request, username):
    user = request.user
    privacy_form = PrivacySettingsForm(request.POST, instance=user)
    if privacy_form.is_valid():
        privacy_form.save()
        return user_detail(request, username)
    else:
        # Client-side code should prevent making invalid privacy settings,
        # so the view does not use the standard form validation workflow.
        return HttpResponseBadRequest('The requested privacy settings '
                                      'are invalid')


def update_user(request, username):
    # TODO: implement
    pass


def request_individual_mapper_status(request, username):
    user = request.user
    if not user.eligible_to_become_individual_mapper:
        return HttpResponseForbidden()
    if not user.individual_mapper:
        user.individual_mapper = True
        user.requested_individual_mapping_at = timezone.now()
        user.clean_and_save()
    return redirect('individual_mapper_instructions')


def start_form_for_reservation_job(request, username):
    # TODO: implement
    pass


def start_map_for_reservation_job(request, username):
    # TODO: implement
    pass


def start_map_for_tool_depots_job(request, username):
    # TODO: implement
    pass


def achievements_page(request):
    # TODO: implement
    return {}
