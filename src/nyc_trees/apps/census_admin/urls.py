# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.core.decorators import is_census_admin, route
from apps.census_admin.views import (start_admin_users_job,
                                     start_admin_surveys_job, admin_edits_page,
                                     admin_edits_partial,
                                     admin_training_material_list,
                                     admin_training_material)


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
    url(r'^users-export/$',
        is_census_admin(route(POST=start_admin_users_job)),
        name='start_admin_users_job'),

    url(r'^surveys-export/$',
        is_census_admin(route(POST=start_admin_surveys_job)),
        name='start_admin_surveys_job'),

    url(r'^edits/$',
        is_census_admin(route(GET=admin_edits_page)),
        name='admin_edits_page'),

    url(r'^edits-partial/$',
        is_census_admin(route(GET=admin_edits_partial)),
        name='admin_edits_partial'),

    # TODO: Use Django flatpages for training POST/PUT endpoints

    url(r'^training/$',
        is_census_admin(route(GET=admin_training_material_list,
                           # POST=add_training_material
                           )),
        name='admin_training_material_list'),

    url(r'^training/(?P<training_material_url_name>\w+)/$',
        is_census_admin(route(GET=admin_training_material,
                           # PUT=edit_training_material
                           )),
        name='admin_training_material'),

    # TODO: Use Django Admin site for these
    #
    # url(r'^admin/$', census_admin(route(GET=census_admin_page))),
    # url(r'^admin/users/$', census_admin(route(GET=admin_users_page))),
    # url(r'^admin/users/(?P<username>\w+)/$', census_admin(route(GET=admin_user_detail, PUT=admin_update_user))),  # Unclear if admin_user_detail is required
    # url(r'^admin/users/(?P<username>\w+)/flag/$', census_admin(route(POST=flag_user))),
    # url(r'^admin/users/(?P<username>\w+)/unflag/$', census_admin(route(POST=unflag_user))),
    #
    # url(r'^admin/users/(?P<username>\w+)/individual-mapper-request/$', census_admin(route(POST=confirm_individual_mapper, DELETE=deny_individual_mapper))),
    #
    # url(r'^admin/users/individual-mapper-requests/$', census_admin(route(GET=individual_mapper_requests_page))),
    # url(r'^admin/group/$', census_admin(route(GET=admin_groups_page, POST=add_group))),  # Each row will link to the group's event dashboard
    # url(r'^admin/group/(?P<group_name>\w+)/$', census_admin(route(GET=admin_group_detail, PUT=admin_update_group))),  # admin_update_group includes editing blockface reservations and setting admin
    # url(r'^admin/group/(?P<group_name>\w+)/enable/$', census_admin(route(POST=enable_group))),
    # url(r'^admin/group/(?P<group_name>\w+)/disable/$', census_admin(route(POST=disable_group))),
    #
    # url(r'^admin/survey/$', census_admin(route(GET=admin_surveys_page))),
    # url(r'^admin/survey/(?P<survey_id>\d+)/$', census_admin(route(GET=admin_survey_detail_page, PUT=admin_update_survey))),
)
