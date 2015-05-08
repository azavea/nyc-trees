# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib import admin
import apps.survey.models as m


class TreeInline(admin.TabularInline):
    extra = 0
    model = m.Tree


class SurveyAdmin(admin.ModelAdmin):
    inlines = [TreeInline]
    search_fields = ('id', 'quit_reason', 'user__username', 'blockface__id')
    list_display = ('blockface', 'user', 'has_trees',
                    'is_flagged', 'teammate', 'quit_reason')
    list_filter = ('is_flagged', 'has_trees')
    raw_id_fields = ("blockface",)


class BlockfaceReservationAdmin(admin.ModelAdmin):
    raw_id_fields = ("blockface",)
    search_fields = ('blockface__id',)


admin.site.register(m.Blockface)
admin.site.register(m.Territory)
admin.site.register(m.Survey, SurveyAdmin)
admin.site.register(m.Tree)
admin.site.register(m.BlockfaceReservation, BlockfaceReservationAdmin)
admin.site.register(m.Species)
