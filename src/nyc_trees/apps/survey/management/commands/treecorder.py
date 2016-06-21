# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
import csv
import json
import fileinput
import itertools

from collections import namedtuple

from django.core.management.base import BaseCommand

from apps.survey.models import Survey
from apps.survey.views import _survey_geojson


Record = namedtuple('Record', ['report_id',
                               'plot_number',
                               'block_face_number',
                               'tree_id_number',
                               'distance_along_curb',
                               'distance_along_curb_units',
                               'street_side_numbers',
                               'on_st',
                               'from_st',
                               'to_st',
                               'address_order',
                               'side_of_centerline'])


class Command(BaseCommand):
    """
    Execute the Treekit geometry constructor for each row of tree data
    in a CSV file. The output CSV should match the original input with
    additional columns for lat/lng.
    """

    def handle(self, *args, **options):
        fp = fileinput.input('-')
        reader = csv.reader(fp)
        writer = csv.writer(sys.stdout)

        headers = reader.next()
        headers = headers + ['LAT', 'LNG']
        writer.writerow(headers)

        records = (Record(*line) for line in reader)

        # Group rows in chunks by block_face_number. Assumes that the CSV
        # is sorted by block_face_number.
        grouped_records = itertools.groupby(records,
                                            lambda r: r.block_face_number)

        for blockface_id, rows in grouped_records:
            rows = list(rows)
            survey = self.create_survey(rows[0])

            if not survey.blockface_id:
                continue

            trees = list(self.create_trees(rows))

            # Execute Treekit geometry constructor to determine
            # tree locations.
            points = _survey_geojson(survey, trees)

            # Parse GeoJSON result.
            points = (json.loads(p) for p in points)

            # Combine tree location with original CSV row.
            for row, point in itertools.izip(rows, points):
                lat, lng = point['coordinates']
                writer.writerow(row + (lat, lng))

    def create_survey(self, row):
        """
        Return fake survey with the minimum amount of information
        necessary to generate tree locations.
        """
        survey = Survey()
        survey.blockface_id = row.block_face_number
        survey.is_left_side = row.side_of_centerline == 'Left'

        # TODO: How to determine if they started at the beginning
        # or end of blockface?
        survey.is_mapped_in_blockface_polyline_direction = True

        return survey

    def create_trees(self, rows):
        """
        Return survey formatted data to calculate tree locations.
        Assumes all rows belong to the same blockface.
        """
        rows = list(rows)
        for row in rows:
            distance_to_tree = float(row.distance_along_curb or 0)

            # Add distances from trees behind current tree.
            for other in rows:
                if other.tree_id_number < row.tree_id_number:
                    distance_to_tree += float(other.distance_along_curb or 0)

            yield {
                'distance_to_tree': distance_to_tree,
                'curb_location': 'OnCurb',
            }
