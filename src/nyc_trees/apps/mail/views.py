# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.utils.timezone import now

from django_statsd.clients import statsd

from apps.core.models import User

# Message Types
GROUP_MAPPING_APPROVED = 'group_mapping_approved'


def _send_to(user, message_type, *args, **kwargs):
    """
    Send a templated email to a single, registered user. The
    message_type argument is the string prefix of the subject and body
    templates to be used (e.g. a message_type of 'welcome' will send an
    email using the subject template 'mail/welcome_subject.txt' and body
    template 'mail/welcome.txt'
    """
    kwargs['user'] = user
    context = Context(kwargs)

    body_text_template = get_template('mail/%s.txt' % message_type)
    body_text = body_text_template.render(context)

    subject_template = get_template('mail/%s_subject.txt' % message_type)
    # Use rstrip to ensure that the subject does not end with \n
    subject = subject_template.render(context).rstrip()

    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email

    msg = EmailMessage(subject, body_text, from_email, [to])
    msg.send()
    statsd.incr('email.message.types.%s' % message_type)
    return {
        'to': to,
        'from_email': from_email,
        'subject': subject,
        'body_text': body_text,
        'sent_at': now()
    }


def notify_group_mapping_approved(request, group, username):
    user = get_object_or_404(User, username=username)
    reservations_url = request.build_absolute_uri(reverse('reservations'))
    return _send_to(user,
                    GROUP_MAPPING_APPROVED,
                    group=group,
                    reservations_url=reservations_url)
