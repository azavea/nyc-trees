# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import csv
import os
import tempfile
import json
import shutil
import zipfile
from io import BytesIO
from collections import namedtuple

import fiona
from celery import task
from djqscsv import write_csv
import importlib

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection


from apps.survey.models import Blockface
from apps.event.models import Event


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


Mapping = namedtuple('Mapping', ['shp_record', 'type', 'column'])


def _datetime_attr(col):
    return lambda row: row[col].strftime('%Y-%m-%d %H:%M:%S')


def _boolean_attr(col):
    return lambda row: 'T' if row[col] else 'F'


def _json_attr(col):
    return lambda row: row[col].json


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
    with connection.cursor() as cursor:
        cursor.execute(TREES_QUERY)

        mappings = [
            Mapping('tree_id', 'int', 1),
            Mapping('survey_id', 'int', 2),
            Mapping('species_id', 'int', 3),
            Mapping('dist_tree', 'float', 4),
            Mapping('dist_end', 'float', 5),
            Mapping('tree_circ', 'int', 6),
            Mapping('stump_diam', 'int', 7),
            Mapping('curb_loc', 'str', 8),
            Mapping('status', 'str', 9),
            Mapping('speci_cert', 'str', 10),
            Mapping('health', 'str', 11),
            Mapping('steward', 'str', 12),
            Mapping('guards', 'str', 13),
            Mapping('sidewalk', 'str', 14),
            Mapping('problems', 'str:130', 15),
            Mapping('created_at', 'str', _datetime_attr(16)),
            Mapping('updated_at', 'str', _datetime_attr(17)),
        ]

        rows = cursor.fetchall()

    return _dump_to_shapefile(dump_id, mappings, rows, filename='trees',
                              geom=0, geom_type='Point')


@task
def dump_blockface_to_shapefile(dump_id):
    blockfaces = Blockface.objects.all().values(
        'id', 'geom', 'is_available', 'expert_required', 'updated_at'
    )

    mappings = [
        Mapping('block_id', 'int', 'id'),
        Mapping('is_avail', 'str', _boolean_attr('is_available')),
        Mapping('expert_req', 'str', _boolean_attr('expert_required')),
        Mapping('updated_at', 'str', _datetime_attr('updated_at')),
    ]

    return _dump_to_shapefile(dump_id, mappings, blockfaces,
                              filename='blockface', geom=_json_attr('geom'),
                              geom_type='MultiLineString')


@task
def dump_events_to_shapefile(dump_id):
    mappings = [
        Mapping('event_id', 'int', 'id'),
        Mapping('group_id', 'int', 'group_id'),
        Mapping('title', 'str:255', 'title'),
        Mapping('slug', 'str', 'slug'),
        Mapping('desc', 'str:1000', 'description'),
        Mapping('loc_desc', 'str:1000', 'location_description'),
        Mapping('con_email', 'str', 'contact_email'),
        Mapping('con_name', 'str:255', 'contact_name'),
        Mapping('begins_at', 'str', _datetime_attr('begins_at')),
        Mapping('ends_at', 'str', _datetime_attr('ends_at')),
        Mapping('address', 'str:1000', 'address'),
        Mapping('max_rsvps', 'int', 'max_attendees'),
        Mapping('training', 'str', _boolean_attr('includes_training')),
        Mapping('canceled', 'str', _boolean_attr('is_canceled')),
        Mapping('private', 'str', _boolean_attr('is_private')),
        Mapping('created_at', 'str', _datetime_attr('created_at')),
        Mapping('updated_at', 'str', _datetime_attr('updated_at')),
    ]

    events = Event.objects.all().values()

    return _dump_to_shapefile(dump_id, mappings, events, filename='event',
                              geom=_json_attr('location'), geom_type='Point')


def _dump_to_shapefile(dump_id, mappings, rows, filename, geom, geom_type):
    tmp_dir = tempfile.mkdtemp()
    shp_file = os.path.join(tmp_dir, '%s.shp' % filename)

    crs = {'no_defs': True,
           'ellps': 'WGS84',
           'datum': 'WGS84',
           'proj': 'longlat'}

    schema = {
        'geometry': geom_type,
        'properties': [
            (mapping.shp_record, mapping.type)
            for mapping in mappings
        ]
    }

    def get_val(row, column):
        if callable(column):
            return column(row)

        return row[column]

    with fiona.open(shp_file, 'w', driver='ESRI Shapefile', crs=crs,
                    schema=schema) as shp:

        for row in rows:
            rec = {
                'geometry': json.loads(get_val(row, geom)),
                'properties': {
                    mapping.shp_record: get_val(row, mapping.column)
                    for mapping in mappings
                }
            }
            shp.write(rec)

    paths = []

    for ext in ['shp', 'dbf', 'prj', 'cpg', 'shx']:
        tmp_file = os.path.join(tmp_dir, '%(filename)s.%(ext)s' % {
            'filename': filename, 'ext': ext})

        with open(tmp_file, 'r') as f:
            paths.append(_storage.save(
                'dump/%(dump_id)s/%(filename)s.%(ext)s' % {
                    'dump_id': dump_id, 'filename': filename, 'ext': ext
                }, f))

    shutil.rmtree(tmp_dir)

    return paths


@task
def dump_model(fq_name, dump_id):
    _, temp_file_path = tempfile.mkstemp()
    Model = _model_from_fq_name(fq_name)
    with open(temp_file_path, 'w') as f:
        # We specify QUOTE_NONNUMERIC here but the current version of
        # djqscsv coerces everything to a string. Overquoting is better
        # than underquoting.
        write_csv(Model.objects.all(), f, quoting=csv.QUOTE_NONNUMERIC)

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
