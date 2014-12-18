# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from floppyforms.__future__ import Form, CharField, Textarea


class EmailForm(Form):
    subject = CharField(label='Subject')
    body = CharField(label='Message', widget=Textarea)
