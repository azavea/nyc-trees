# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template
from django_tinsel.utils import decorate as do

from apps.home import views as v
from apps.core.views import map_legend

home_page = route(GET=do(render_template('home/home.html'),
                         v.home_page))

progress_page = route(GET=do(render_template('home/progress.html'),
                             map_legend))

retrieve_job_status = do(v.retrieve_job_status)

training_list_page = route(GET=do(render_template('home/training.html'),
                                  v.training_list_page))

groups_to_follow = route(GET=do(render_template('home/groups_to_follow.html'),
                                v.groups_to_follow))


##############################################################
#
# TRAINING ROUTES
#
# Each training page can be accessed one of two ways:
# 1) when completing a previous training step, and thus marking
#    that step as complete. This is covered by the routes below.
# 2) when being visited from the training summary page. This will
#    not have the side effect of marking a step as complete. This
#    is covered mostly by vanilla flatpages but also by some regular
#    routes.
#

the_mapping_method_from_previous = route(GET=do(
    v.mark_user_on_success('training_finished_getting_started'),
    v.redirect_to_flat_page('/the_mapping_method/')))

tree_data_from_previous = route(GET=do(
    v.mark_user_on_success('training_finished_the_mapping_method'),
    v.redirect_to_flat_page('/tree_data/')))

tree_surroundings_from_previous = route(GET=do(
    v.mark_user_on_success('training_finished_tree_data'),
    v.redirect_to_flat_page('/tree_surroundings/')))

groups_to_follow_from_previous = route(GET=do(
    v.mark_user_on_success('training_finished_tree_surroundings'),
    groups_to_follow))

training_list_from_groups_to_follow = route(GET=do(
    v.mark_user_on_success('training_finished_groups_to_follow'),
    training_list_page))
