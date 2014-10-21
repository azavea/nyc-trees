from django.conf.urls import patterns, url

from decorators import (route, logged_in, has_training,
                        individual_only, group_admin, census_admin)

# census_admin can access group_admin views
# has_training == has completed the 1 required quiz



urlpatterns = patterns(
    '',
    url(r'^/$', route(GET=home_page)),
    url(r'^progress/$', route(GET=progess_page)),  # May be part of home page

    # The following are all good candidates for the Django flatpages app
    url(r'^faq/$', route(GET=faq_page)),
    url(r'^about/$', route(GET=about_page)),
    url(r'^training/$', route(GET=training_material_list_page)),
    url(r'^training/(?P<training_material_url_name>\w+)/$', route(GET=training_material__detail_page)),

    # https://github.com/macropin/django-registration/blob/master/registration/backends/default/urls.py
    # used as reference
    url(r'^register/$', route(GET=registration_page, POST=register_user)),
    url(r'^register-complete/$', route(GET=registration_complete_page)),
    url(r'^activate/(?P<hash>[^/]+)/$', route(GET=activate_registration_page, POST=activate_user)),
    url(r'^activate-complete/$', route(GET=activation_complete_page)),

    url(r'^login/$', route(GET=login_page, POST=login_user)),
    url(r'^login/forgot-password/$', route(GET=forgot_password_page, POST=forgot_password)),
    url(r'^login/forgot-username/$', route(GET=forgot_username_page, POST=forgot_username)),
    url(r'^login/forgot-username-complete/$', route(GET=forgot_username_email_sent_page)),
    url(r'^login/forgot-password-complete/$', route(GET=forgot_password_email_sent_page)),

    url(r'^user/(?P<username>\w+)/$', route(GET=user_detail, PUT=logged_in(update_user))),
    url(r'^user/(?P<username>\w+)/request-individual-mapper-status/$', logged_in(route(POST=request_individual_mapper_status))),
    url(r'^user/(?P<username>\w+)/printable-survey-form/$', route(POST=start_form_for_reservation_job)),
    url(r'^user/(?P<username>\w+)/printable-map/$', route(POST=start_map_for_reservation_job)),
    url(r'^user/(?P<username>\w+)/printable-tooldepots/$', route(POST=start_map_for_tool_depots_job)),

    url(r'^quiz/$', route(GET=quiz_list_page)),
    url(r'^quiz/(?P<quiz_id>\d+)/$', logged_in(route(GET=quiz_page, POST=complete_quiz))),  # We could maybe let people start, but not complete a quiz when not loggged in

    url(r'^group/$', route(GET=group_list_page)),
    url(r'^group/(?P<group_name>\w+)/$', route(GET=group_detail, PUT=group_admin(edit_group))),
    url(r'^group/(?P<group_name>\w+)/follow/$', logged_in(route(POST=follow_group))),
    url(r'^group/(?P<group_name>\w+)/unfollow/$', logged_in(route(POST=unfollow_group))),
    url(r'^group/(?P<group_name>\w+)/printable-map/$', route(POST=start_group_map_print_job)),
    url(r'^group/(?P<group_name>\w+)/event/$', group_admin(route(GET=event_dashboard, POST=add_event))),
    url(r'^group/(?P<group_name>\w+)/event/(?P<event_id>\d+)/$', route(GET=event_detail)),
    url(r'^group/(?P<group_name>\w+)/individual-mapper/$', group_admin(route(GET=group_mapping_priveleges_page))),
    url(r'^group/(?P<group_name>\w+)/individual-mapper/(?P<username>\w+)/$', group_admin(route(PUT=give_user_mapping_priveleges, DELETE=remove_user_mapping_priveleges))),

    url(r'^blockface/$', individual_only(route(GET=reserve_blockface_page))),
    url(r'^blockface/(?P<blockface_id>\d+)/cancel-reservation/$', individual_only(route(POST=cancel_reservation))),
    url(r'^blockface/(?P<blockface_id>\d+)/cart/$', individual_only(route(POST=add_blockface_to_cart, DELETE=remove_blockface_from_cart))),
    url(r'^blockface/checkout/$', individual_only(route(GET=blockface_cart_page, POST=reserve_blockfaces))),
    url(r'^blockface/checkout-confirmation/$', individual_only(route(GET=blockface_reservations_confirmation_page))),
    url(r'^blockface/(?P<blockface_id>\d+)/survey/$', has_training(route(GET=start_survey, POST=submit_survey))),

    # The choose_blockface_survey_page will have a GET parameter of blockface_id, which is used to change the starting map location
    url(r'^survey/$', has_training(route(GET=choose_blockface_survey_page))),

    url(r'^species/$', route(GET=species_autocomplete_list)),

    url(r'^event/$', route(GET=events_list_page)),
    url(r'^event/table/$', route(GET=events_list_page_partial)),
    url(r'^event/feed/$', route(GET=events_list_feed)),
    url(r'^event/(?P<event_url_name>\w+)/$', route(GET=event_detail, DELETE=group_admin(delete_event), PUT=group_admin(edit_event))),
    url(r'^event/(?P<event_url_name>\w+)/popup/$', route(GET=event_popup_partial)),
    url(r'^event/(?P<event_url_name>\w+)/register/$', has_training(route(POST=register_for_event, DELETE=cancel_event_registration))),
    url(r'^event/(?P<event_url_name>\w+)/printable-map/$', has_training(route(POST=start_event_map_print_job))),
    url(r'^event/(?P<event_url_name>\w+)/checkin/$', group_admin(route(GET=event_check_in_page))),
    url(r'^event/(?P<event_url_name>\w+)/checkin/(?P<username>\w+)/$', group_admin(route(POST=check_in_user_to_event, DELETE=un_check_in_user_to_event))),
    url(r'^event/(?P<event_url_name>\w+)/email/$', group_admin(route(POST=email_event_registered_users))),

    # The user, group, survey, and training sections could utilize the Django Admin site almost entirely
    # The training section POST/PUT endpoints could be replaced by Django flatpages
    url(r'^admin/$', census_admin(route(GET=census_admin_page))),
    url(r'^admin/users/$', census_admin(route(GET=admin_users_page))),
    url(r'^admin/users/(?P<username>\w+)/$', census_admin(route(GET=admin_user_detail, PUT=admin_update_user))),  # Unclear if admin_user_detail is required
    url(r'^admin/users/(?P<username>\w+)/flag/$', census_admin(route(POST=flag_user)),
    url(r'^admin/users/(?P<username>\w+)/unflag/$', census_admin(route(POST=unflag_user)),
    url(r'^admin/users/(?P<username>w+)/individual-mapper-request/$', census_admin(route(POST=confirm_individual_mapper, DELETE=deny_individual_mapper))),
    url(r'^admin/users/individual-mapper-requests/$', census_admin(route(GET=individual_mapper_requests_page))),
    url(r'^admin/group/$', census_admin(route(GET=admin_groups_page, POST=add_group))),  # Each row will link to the group's event dashboard
    url(r'^admin/group/(?P<group_name>\w+)/$', census_admin(route(GET=admin_group_detail, PUT=admin_update_group))),  # admin_update_group includes editing blockface reservations and setting admin
    url(r'^admin/group/(?P<group_name>\w+)/enable/$', census_admin(route(POST=enable_group))),
    url(r'^admin/group/(?P<group_name>\w+)/disable/$', census_admin(route(POST=disable_group))),
    url(r'^admin/blockface/$', census_admin(route(GET=admin_blockface_page))),
    url(r'^admin/blockface-partial/$', census_admin(route(GET=admin_blockface_partial))),
    url(r'^admin/blockface/(?P<blockface_id>\d+)/$', census_admin(route(GET=admin_blockface_detail_page))),
    url(r'^admin/blockface/(?P<blockface_id>\d+)/extend-reservation/$', census_admin(route(POST=admin_extend_blockface_reservation))),
    url(r'^admin/blockface/(?P<blockface_id>\d+)/set-available/$', census_admin(route(POST=admin_blockface_available))),
    url(r'^admin/users-export/$', census_admin(route(POST=start_admin_users_job))),
    url(r'^admin/surveys-export/$', census_admin(route(POST=start_admin_surveys_job))),
    url(r'^admin/survey/$', census_admin(route(GET=admin_surveys_page))),
    url(r'^admin/survey/(?P<survey_id>\d+)/$', census_admin(route(GET=admin_survey_detail_page, PUT=admin_update_survey))),
    url(r'^admin/edits/$', census_admin(route(GET=admin_edits_page))),
    url(r'^admin/edits-partial/$', census_admin(route(GET=admin_edits_partial))),
    url(r'^admin/training/$', census_admin(route(GET=admin_training_material_list, POST=add_training_material))),
    url(r'^admin/training/(?P<training_material_url_name>\w+)/$', census_admin(route(GET=admin_training_material_list, PUT=edit_training_material))),

    url(r'^jobs/(?P<job_id>\d+)/$', route(GET=retrieve_job_status)),
)
