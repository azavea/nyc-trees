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
    row = _get_rows(sql, params)[0]
    return row[0]


def _get_rows(sql, params=[]):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def get_user_tree_count(user, from_date=None):
    sql = _survey_sql + """
        SELECT COUNT(*)
        FROM survey_tree AS tree
        JOIN most_recent_survey
          ON tree.survey_id = most_recent_survey.id
        WHERE (most_recent_survey.user_id = %s
          OR most_recent_survey.teammate_id = %s)"""

    params = [user.pk, user.pk]

    if from_date is not None:
        sql += " AND most_recent_survey.created_at > %s at time zone 'utc'"
        params.append(from_date)

    return _get_count(sql, params)


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


def get_total_tree_count(past_week=False):
    sql = _survey_sql + """
        SELECT COUNT(*)
        FROM survey_tree AS tree
        JOIN most_recent_survey
          ON tree.survey_id = most_recent_survey.id"""
    if past_week:
        sql += " WHERE most_recent_survey.created_at" \
               " > now() at time zone 'utc' - INTERVAL '7 days'"
    return _get_count(sql)


def get_user_surveyed_species(user):
    sql = _survey_sql + """
        SELECT species.common_name, COUNT(*) AS count
        FROM most_recent_survey
        INNER JOIN survey_tree AS tree
          ON tree.survey_id = most_recent_survey.id
        INNER JOIN survey_species AS species
          ON species.id = tree.species_id
        WHERE tree.species_id IS NOT NULL
          AND (most_recent_survey.user_id = %s
               OR most_recent_survey.teammate_id = %s)
        GROUP BY species.common_name
        ORDER BY count DESC
        """
    return _get_rows(sql, [user.pk, user.pk])


def get_surveyed_species():
    sql = _survey_sql + """
        SELECT species.common_name, COUNT(*) AS count
        FROM most_recent_survey
        INNER JOIN survey_tree AS tree
          ON tree.survey_id = most_recent_survey.id
        INNER JOIN survey_species AS species
          ON species.id = tree.species_id
        WHERE tree.species_id IS NOT NULL
        GROUP BY species.common_name
        ORDER BY count DESC
        """
    return _get_rows(sql)


def get_block_count_past_week():
    sql = _survey_sql + """
        SELECT COUNT(*)
        FROM survey_blockface AS block
        JOIN most_recent_survey
          ON block.id = most_recent_survey.blockface_id
       WHERE most_recent_survey.created_at
             > now() at time zone 'utc' - INTERVAL '7 days'"""

    return _get_count(sql)
