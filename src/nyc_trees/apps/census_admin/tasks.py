# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import tempfile
import json
import shutil
import zipfile
from io import BytesIO

import fiona
from celery import task
from djqscsv import write_csv
import importlib

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection


from apps.survey.models import Blockface


if getattr(settings, 'PRIVATE_AWS_STORAGE_BUCKET_NAME', None):
    # Delay import to prevent failure on dev VMs that do not
    # have boto/s3 tooling
    from libs.custom_storages import PrivateS3BotoStorage
    _storage = PrivateS3BotoStorage()
else:
    _storage = default_storage


TREES_QUERY_FILE = os.path.join(os.path.dirname(__file__), 'trees.sql')

with open(TREES_QUERY_FILE, 'r') as f:
    TREES_QUERY = f.read()


@task
def zip_dumps(file_lists, dump_id):
    file_paths = [path for sublist in file_lists for path in sublist]

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_f:

        for path in file_paths:
            with _storage.open(path) as dump_f:
                zip_f.writestr(os.path.basename(path), dump_f.read())

    buffer.flush()
    buffer.seek(0)

    _storage.save('dump/%s/dump.zip' % dump_id, buffer)


@task
def dump_trees_to_shapefile(dump_id):
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

    paths = []
    with open(shp_file, 'r') as f:
        paths.append(_storage.save('dump/%s/trees.shp' % dump_id, f))

    with open(os.path.join(tmp_dir, 'trees.dbf'), 'r') as f:
        paths.append(_storage.save('dump/%s/trees.dbf' % dump_id, f))

    with open(os.path.join(tmp_dir, 'trees.prj'), 'r') as f:
        paths.append(_storage.save('dump/%s/trees.prj' % dump_id, f))

    with open(os.path.join(tmp_dir, 'trees.cpg'), 'r') as f:
        paths.append(_storage.save('dump/%s/trees.cpg' % dump_id, f))

    with open(os.path.join(tmp_dir, 'trees.shx'), 'r') as f:
        paths.append(_storage.save('dump/%s/trees.shx' % dump_id, f))

    shutil.rmtree(tmp_dir)

    return paths


@task
def dump_blockface_to_shapefile(dump_id):
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

    paths = []
    with open(shp_file, 'r') as f:
        paths.append(_storage.save('dump/%s/blockface.shp' % dump_id, f))

    with open(os.path.join(tmp_dir, 'blockface.dbf'), 'r') as f:
        paths.append(_storage.save('dump/%s/blockface.dbf' % dump_id, f))

    with open(os.path.join(tmp_dir, 'blockface.prj'), 'r') as f:
        paths.append(_storage.save('dump/%s/blockface.prj' % dump_id, f))

    with open(os.path.join(tmp_dir, 'blockface.cpg'), 'r') as f:
        paths.append(_storage.save('dump/%s/blockface.cpg' % dump_id, f))

    with open(os.path.join(tmp_dir, 'blockface.shx'), 'r') as f:
        paths.append(_storage.save('dump/%s/blockface.shx' % dump_id, f))

    shutil.rmtree(tmp_dir)

    return paths


@task
def dump_model(fq_name, dump_id):
    _, temp_file_path = tempfile.mkstemp()
    Model = _model_from_fq_name(fq_name)
    with open(temp_file_path, 'w') as f:
        write_csv(Model.objects.all(), f)

    model_name = Model.__name__.lower()
    file_name = 'dump/{}/{}.csv'.format(dump_id, model_name)

    with open(temp_file_path, 'r') as f:
        destination_path = _storage.save(file_name, f)
    os.remove(temp_file_path)

    return [destination_path]


def _class_for_name(module_name, class_name):
    m = importlib.import_module(module_name)
    return getattr(m, class_name)


def _model_from_fq_name(fq_name):
    module_name, class_name = fq_name.rsplit('.', 1)
    return _class_for_name(module_name, class_name)
