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

from pytz import timezone

import fiona
from celery import task
from djqscsv import write_csv
import importlib

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.template.loader import render_to_string


from apps.survey.models import Blockface
from apps.event.models import Event

_DATETIME_FIELDS = ('created_at',
                    'updated_at',
                    'territory_updated_at',
                    'canceled_at',
                    'expries_at',
                    'reminder_sent_at',
                    'begins_at',
                    'ends_at')


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


def get_dt_formatter():
    est_tz = timezone('US/Eastern')

    def f(dt):
        return dt.astimezone(est_tz).strftime('%Y-%m-%d %H:%M:%S')
    return f


def _datetime_attr(col):
    dt_format = get_dt_formatter()
    return lambda row: (dt_format(row[col]))


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
def dump_model(fq_name, fields, dump_id):
    _, temp_file_path = tempfile.mkstemp()
    Model = _model_from_fq_name(fq_name)

    if fields is None:
        queryset = Model.objects.all()
    else:
        print(fields)
        queryset = Model.objects.all().values(*fields)

    dt_format = get_dt_formatter()

    field_serializer_map = {k: dt_format
                            for k in _DATETIME_FIELDS}

    with open(temp_file_path, 'w') as f:
        # We specify QUOTE_NONNUMERIC here but the current version of
        # djqscsv coerces everything to a string. Overquoting is better
        # than underquoting.
        write_csv(queryset, f, quoting=csv.QUOTE_NONNUMERIC,
                  field_serializer_map=field_serializer_map)

    model_name = Model.__name__.lower()
    file_name = 'dump/{}/{}.csv'.format(dump_id, model_name)

    with open(temp_file_path, 'r') as f:
        destination_path = _storage.save(file_name, f)
    os.remove(temp_file_path)

    return [destination_path]


@task
def write_data_dictionary(fq_names, dump_id):
    models = [_model_context(fq_name) for fq_name in fq_names]
    models.sort(key=lambda m: m['name'])
    context = {
        'models': models,
        'date': dump_id
    }
    html = render_to_string('census_admin/data_doc.html', context)
    content = ContentFile(html)

    file_name = 'dump/{}/doc.html'.format(dump_id)
    destination_path = _storage.save(file_name, content)

    return [destination_path]


def _model_context(fq_name):
    Model = _model_from_fq_name(fq_name)
    model_name = Model.__name__

    context = {
        'name': model_name,
        'fields': [_field_context(field, model_name)
                   for field in Model._meta.fields]
        }
    return context


def _field_context(field, model_name):
    name = field.attname
    if model_name in _shapefile_fields:
        name = _shapefile_fields[model_name][name]

    type = field.get_internal_type()

    if type == 'CharField' or type == 'TextField':
        required = not field.blank
    else:
        required = not field.null

    if type == 'CharField':
        max_length = field.max_length
    else:
        max_length = ''

    context = {
        'name': name,
        'type': type,
        'required': required,
        'description': field.help_text,
        'max_length': max_length
        }
    return context


def _class_for_name(module_name, class_name):
    m = importlib.import_module(module_name)
    return getattr(m, class_name)


def _model_from_fq_name(fq_name):
    # "fq" means "fully-qualified"
    module_name, class_name = fq_name.rsplit('.', 1)
    return _class_for_name(module_name, class_name)


# Translate model fields to shapefile fields for data dictionary doc
_shapefile_fields = {
    'Blockface': {
        'id': 'block_id',
        'is_available': 'is_avail',
        'expert_required': 'expert_req',
        'updated_at': 'updated_at',
        'created_at': 'created_at',
        'borough_id': 'borough_id',
        'nta_id': 'nta_id',
        'geom': None,
        'source': None,
        },
    'Event': {
        'id': 'event_id',
        'group_id': 'group_id',
        'title': 'title',
        'slug': 'slug',
        'description': 'desc',
        'location_description': 'loc_desc',
        'contact_email': 'con_email',
        'contact_name': 'con_name',
        'begins_at': 'begins_at',
        'ends_at': 'ends_at',
        'address': 'address',
        'max_attendees': 'max_rsvps',
        'includes_training': 'training',
        'is_canceled': 'canceled',
        'is_private': 'private',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'location': None,
        'map_pdf_filename': None,
        },
    'Tree': {
        'id': 'tree_id',
        'survey_id': 'survey_id',
        'species_id': 'species_id',
        'distance_to_tree': 'dist_tree',
        'distance_to_end': 'dist_end',
        'circumference': 'tree_circ',
        'stump_diameter': 'stump_diam',
        'curb_location': 'curb_loc',
        'status': 'status',
        'species_certainty': 'speci_cert',
        'health': 'health',
        'stewardship': 'steward',
        'guards': 'guards',
        'sidewalk_damage': 'sidewalk',
        'problems': 'problems',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        }
}
