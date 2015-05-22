# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import boto.ses

from email.mime.text import MIMEText


class BotoMailer():

    def __init__(self, aws_region):
        self.aws_region = aws_region

    def send_plain_text_message(self, text, subject, from_email, to):
        message = MIMEText(text)
        message['Subject'] = subject
        message['From'] = from_email
        message['To'] = to
        self.send_message_bytes(message.as_string(), from_email, to)

    def send_message_bytes(self, message_bytes, from_email, to):
        return self._connection().send_raw_email(message_bytes, from_email, to)

    def get_remaining_message_quota(self):
        response = self._connection().get_send_quota()
        quota = response['GetSendQuotaResponse']['GetSendQuotaResult']
        limit = int(float(quota['Max24HourSend']))
        sent_count = int(float(quota['SentLast24Hours']))
        return limit - sent_count

    def _connection(self):
        return boto.ses.connect_to_region(self.aws_region)
