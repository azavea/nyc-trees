# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import models


class NycModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False,
        help_text='Time when row was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False,
        help_text='Time when row was last updated'
    )

    class Meta:
        abstract = True

    def clean_and_save(self):
        """Validates and saves the Model.
        Should be called instead of save() when ModelForms are not being used
        to handle validation.
        """
        self.full_clean()
        self.save()
