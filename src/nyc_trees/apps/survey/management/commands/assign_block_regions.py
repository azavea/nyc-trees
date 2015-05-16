# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


from django.core.management.base import BaseCommand
from django.db import transaction, connection


class Command(BaseCommand):
    """
    Assign update the borough_id and nta_id columns
    of the survey_blockface table by intersecting the
    blockfaces with the survey_borough and
    survey_neighborhoodtabulationarea tables

    Usage:

    ./manage.py assign_block_regions
    """
    @transaction.atomic
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            sql = """
UPDATE survey_blockface
SET nta_id = a.nta_id
FROM (SELECT s.id AS blockface_id, MAX(b.id) AS nta_id
  FROM survey_blockface s, survey_neighborhoodtabulationarea b
  WHERE st_intersects(b.geom, s.geom)
  GROUP BY s.id) a
WHERE survey_blockface.id = a.blockface_id;"""
            cursor.execute(sql)

            sql = """
UPDATE survey_blockface
SET borough_id = a.borough_id
FROM (SELECT s.id AS blockface_id, MAX(b.id) AS borough_id
  FROM survey_blockface s, survey_borough b
  WHERE st_intersects(b.geom, s.geom)
  GROUP BY s.id) a
WHERE survey_blockface.id = a.blockface_id;"""
            cursor.execute(sql)
