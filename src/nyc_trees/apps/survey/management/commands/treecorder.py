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

from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from apps.survey.models import Survey, Blockface
from apps.survey.views import _survey_geojson


Record = namedtuple('Record', ['record_id',
                               'report_id',
                               'boro_name',
                               'boro_code',
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
                               'side_of_centerline',
                               'make_edit',
                               'start_end',
                               'dist_to',
                               'mapped_correctly',
                               'comment',
                               'x_point',
                               'y_point'])


ny_state_plane = SpatialReference(
    '+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 '
    '+lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 '
    '+ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs ')
ny_state_plane.validate()

wgs84 = SpatialReference(4326)

ny_to_latlng = CoordTransform(ny_state_plane, wgs84)


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
            # The WITH_XY spreadsheet has a bunch of duplicate survey rows,
            # need to deduplicate...
            seen = set()
            rows = [row for row in rows
                    if row.tree_id_number not in seen and
                    not seen.add(row.tree_id_number)]
            survey = self.create_survey(rows[0])

            if survey is None:
                continue

            trees = list(self.create_trees(rows))

            # Execute Treekit geometry constructor to determine
            # tree locations.
            points = _survey_geojson(survey, trees)

            # Parse GeoJSON result.
            points = (json.loads(p) for p in points)

            # Combine tree location with original CSV row.
            for row, point in itertools.izip(rows, points):
                lng, lat = point['coordinates']
                writer.writerow(row + (lat, lng))

    def create_survey(self, row):
        """
        Return fake survey with the minimum amount of information
        necessary to generate tree locations.
        """
        survey = Survey()
        survey.blockface_id = row.block_face_number
        survey.is_left_side = row.side_of_centerline == 'Left'

        try:
            blockface = Blockface.objects.get(pk=survey.blockface_id)
        except Blockface.DoesNotExist:
            return None

        # We need to pass an srid to call .transform(), but it is ignored if we
        # give it a CoordTransform object
        survey_start_point = Point(float(row.x_point), float(row.y_point),
                                   srid=102718)
        survey_start_point.transform(ny_to_latlng)

        blockface_start = Point(blockface.geom.coords[0][0], srid=4326)
        blockface_end = Point(blockface.geom.coords[0][-1], srid=4326)

        start_dst = blockface_start.distance(survey_start_point)
        end_dst = blockface_end.distance(survey_start_point)

        survey.is_mapped_in_blockface_polyline_direction = start_dst < end_dst

        return survey

    def create_trees(self, rows):
        """
        Return survey formatted data to calculate tree locations.
        Assumes all rows belong to the same blockface.
        """
        for row in rows:
            distance_to_tree = float(row.distance_along_curb or 0)

            yield {
                'distance_to_tree': distance_to_tree,
                'curb_location': 'OnCurb',
            }
