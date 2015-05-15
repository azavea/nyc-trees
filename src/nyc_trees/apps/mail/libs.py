# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os

from email.mime.application import MIMEApplication

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context

from django_statsd.clients import statsd


def send_to(user, message_type, *args, **kwargs):
    """
    Send a templated email to a single, registered user. The
    message_type argument is the string prefix of the subject and body
    templates to be used (e.g. a message_type of 'welcome' will send an
    email using the subject template 'mail/welcome_subject.txt' and body
    template 'mail/welcome.txt'

    An 'attachments' kwarg can be included. This must be a list of
    MIMEBase subclass instances.
    """
    kwargs['user'] = user
    context = Context(kwargs)

    body_text_template = get_template('mail/%s.txt' % message_type)
    body_text = body_text_template.render(context)

    subject_template = get_template('mail/%s_subject.txt' % message_type)
    # Use rstrip to ensure that the subject does not end with \n
    subject = subject_template.render(context).rstrip()

    sender_name = kwargs.get('sender_name', '')
    if sender_name:
        from_email = '%s <%s>' % (sender_name, settings.DEFAULT_FROM_EMAIL)
    else:
        from_email = settings.DEFAULT_FROM_EMAIL

    reply_to = kwargs.get('reply_to', '')
    to = user.email

    headers = {}
    if reply_to:
        headers.update({
            'Reply-To': reply_to
        })

    msg = EmailMessage(subject, body_text, from_email, [to], headers=headers)

    if 'attachments' in kwargs and kwargs['attachments']:
        for attachment in kwargs['attachments']:
            msg.attach(attachment)

    msg.send()
    statsd.incr('email.message.types.%s' % message_type)
    return {
        'to': to,
        'from_email': from_email,
        'subject': subject,
        'body_text': body_text,
    }


def pdf_to_attachment(open_fn, path):
    with open_fn(path) as pdf:
        attachment = MIMEApplication(pdf.read(), 'pdf')
        filename = os.path.basename(path)
        try:
            filename = filename.encode('ascii')
        except UnicodeEncodeError:
            filename = ('utf-8', '', filename.encode('utf-8'))

        attachment.add_header('Content-Disposition', 'attachment',
                              filename=filename)
        return attachment
