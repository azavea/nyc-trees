# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import tempfile
import json
import shutil

import fiona
from celery import task

from django.core.files.storage import default_storage
from django.db import connection

from apps.survey.models import Blockface


TREES_QUERY_FILE = os.path.join(os.path.dirname(__file__), 'trees.sql')

with open(TREES_QUERY_FILE, 'r') as f:
    TREES_QUERY = f.read()


@task
def dump_trees_to_shapefile():
    tmp_dir = tempfile.mkdtemp()
    shp_file = os.path.join(tmp_dir, 'trees.shp')

    with connection.cursor() as cursor:
        cursor.execute(TREES_QUERY)

        crs = {'no_defs': True,
               'ellps': 'WGS84',
               'datum': 'WGS84',
               'proj': 'longlat'}

        schema = {
            'geometry': 'Point',
            'properties': [
                ('tree_id', 'int'),
                ('survey_id', 'int'),
                ('species_id', 'int'),
                ('dist_tree', 'float'),
                ('dist_end', 'float'),
                ('tree_circ', 'int'),
                ('stump_diam', 'int'),
                ('curb_loc', 'str'),
                ('status', 'str'),
                ('speci_cert', 'str'),
                ('health', 'str'),
                ('steward', 'str'),
                ('guards', 'str'),
                ('sidewalk', 'str'),
                ('problems', 'str:130'),
                ('created_at', 'str'),
                ('updated_at', 'str'),
            ]
        }

        with fiona.open(shp_file, 'w', driver='ESRI Shapefile', crs=crs,
                        schema=schema) as shp:

            for row in cursor.fetchall():
                # Note: The column order here needs to match the column order
                # specified in trees.sql
                rec = {
                    'geometry': json.loads(row[0]),
                    'properties': {
                        'tree_id': row[1],
                        'survey_id': row[2],
                        'species_id': row[3],
                        'dist_tree': row[4],
                        'dist_end': row[5],
                        'tree_circ': row[6],
                        'stump_diam': row[7],
                        'curb_loc': row[8],
                        'status': row[9],
                        'speci_cert': row[10],
                        'health': row[11],
                        'steward': row[12],
                        'guards': row[13],
                        'sidewalk': row[14],
                        'problems': row[15],
                        'created_at': row[16].strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': row[17].strftime('%Y-%m-%d %H:%M:%S'),
                    }
                }
                shp.write(rec)

    # TODO: This should *not* go to the default storage, as it should not
    # be publicly readable
    with open(shp_file, 'r') as f:
        default_storage.save('dump/trees.shp', f)

    with open(os.path.join(tmp_dir, 'trees.dbf'), 'r') as f:
        default_storage.save('dump/trees.dbf', f)

    with open(os.path.join(tmp_dir, 'trees.prj'), 'r') as f:
        default_storage.save('dump/trees.prj', f)

    with open(os.path.join(tmp_dir, 'trees.cpg'), 'r') as f:
        default_storage.save('dump/trees.cpg', f)

    with open(os.path.join(tmp_dir, 'trees.shx'), 'r') as f:
        default_storage.save('dump/trees.shx', f)

    shutil.rmtree(tmp_dir)


@task
def dump_blockface_to_shapefile():
    tmp_dir = tempfile.mkdtemp()
    shp_file = os.path.join(tmp_dir, 'blockface.shp')

    blockfaces = Blockface.objects.all().values(
        'id', 'geom', 'is_available', 'expert_required', 'updated_at'
    )

    crs = {'no_defs': True,
           'ellps': 'WGS84',
           'datum': 'WGS84',
           'proj': 'longlat'}

    schema = {
        'geometry': 'MultiLineString',
        'properties': [
            ('block_id', 'int'),
            ('is_avail', 'str'),
            ('expert_req', 'str'),
            ('updated_at', 'str'),
        ]
    }

    with fiona.open(shp_file, 'w', driver='ESRI Shapefile', crs=crs,
                    schema=schema) as shp:

        for row in blockfaces:
            rec = {
                'geometry': json.loads(row['geom'].json),
                'properties': {
                    'block_id': row['id'],
                    'is_avail': 'T' if row['is_available'] else 'F',
                    'expert_req': 'T' if row['expert_required'] else 'F',
                    'updated_at': row['updated_at'].strftime(
                        '%Y-%m-%d %H:%M:%S'),
                }
            }
            shp.write(rec)

    # TODO: This should *not* go to the default storage, as it should not
    # be publicly readable
    with open(shp_file, 'r') as f:
        default_storage.save('dump/blockface.shp', f)

    with open(os.path.join(tmp_dir, 'blockface.dbf'), 'r') as f:
        default_storage.save('dump/blockface.dbf', f)

    with open(os.path.join(tmp_dir, 'blockface.prj'), 'r') as f:
        default_storage.save('dump/blockface.prj', f)

    with open(os.path.join(tmp_dir, 'blockface.cpg'), 'r') as f:
        default_storage.save('dump/blockface.cpg', f)

    with open(os.path.join(tmp_dir, 'blockface.shx'), 'r') as f:
        default_storage.save('dump/blockface.shx', f)

    shutil.rmtree(tmp_dir)
