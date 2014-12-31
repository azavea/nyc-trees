# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import connection


_survey_sql = """
    WITH most_recent_survey AS (
        SELECT DISTINCT ON (survey.blockface_id) survey.*
        FROM survey_survey AS survey
        ORDER BY survey.blockface_id, survey.created_at DESC
    )"""


def _get_count(sql, params=[]):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()

        return row[0]


def get_user_tree_count(user):
    sql = _survey_sql + """
        SELECT COUNT(*)
        FROM survey_tree AS tree
        JOIN most_recent_survey
          ON tree.survey_id = most_recent_survey.id
        WHERE most_recent_survey.user_id = %s"""

    return _get_count(sql, [user.pk])


def get_group_tree_count(group):
    sql = _survey_sql + """
        SELECT COUNT(*)
        FROM survey_tree AS tree
        JOIN most_recent_survey
          ON tree.survey_id = most_recent_survey.id
        JOIN survey_territory AS turf
          ON most_recent_survey.blockface_id = turf.blockface_id
        WHERE turf.group_id = %s"""

    return _get_count(sql, [group.pk])


def get_user_species_count(user):
    sql = _survey_sql + """
        SELECT COUNT(*) FROM (
          SELECT DISTINCT ON (tree.species_id) tree.species_id
          FROM survey_tree AS tree
          JOIN most_recent_survey
            ON tree.survey_id = most_recent_survey.id
          WHERE most_recent_survey.user_id = %s
            AND tree.species_id IS NOT NULL
        ) subquery"""

    return _get_count(sql, [user.pk])
