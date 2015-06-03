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


class BlockfaceAdmin(admin.ModelAdmin):
    search_fields = ('id',)
    list_filter = ('is_available',)
    exclude = ('geom',)

    def has_add_permission(self, request):
        return False


class BlockfaceReservationAdmin(admin.ModelAdmin):
    raw_id_fields = ("blockface",)
    search_fields = ('blockface__id',)
    list_filter = ('canceled_at', 'expires_at', 'blockface__is_available')
    list_display = ('canceled_at', 'expires_at', 'blockface', 'user')


admin.site.register(m.Blockface, BlockfaceAdmin)
admin.site.register(m.Territory)
admin.site.register(m.Survey, SurveyAdmin)
admin.site.register(m.Tree)
admin.site.register(m.BlockfaceReservation, BlockfaceReservationAdmin)
admin.site.register(m.Species)
