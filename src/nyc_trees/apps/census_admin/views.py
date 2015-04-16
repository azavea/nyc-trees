# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from collections import OrderedDict
import json

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import transaction

from apps.core.models import Group


def upload_group_polygons(request):
    try:
        file_obj = request.FILES['file']
        file_obj.seek(0)
        text = file_obj.read()
    except Exception as e:
        return {'error': "Error retrieving uploaded file: " + e.message}

    group_data = OrderedDict([
        (group.name, {
            'group': group,
            'previous_polygon_count':
                len(group.border.coords) if group.border else 0,
            'polygons': []})
        for group in Group.objects.all()
    ])

    unknown_group_names = set()
    try:
        data = json.loads(text)
        for feature in data['features']:
            group_name = feature['attributes']['GroupName']
            polygon_points = feature['geometry']['rings'][0]
            if group_name not in group_data:
                unknown_group_names.add(group_name)
            else:
                group_data[group_name]['polygons'].append(polygon_points)

    except Exception as e:
        return {'error': "Error in JSON structure: " + e.message}

    if unknown_group_names:
        names = list(unknown_group_names)
        names.sort()
        return {'unknown_group_names': names}

    context = _update_group_polygons(group_data)
    return context


@transaction.atomic
def _update_group_polygons(group_data):
    for g in group_data.values():
        group = g['group']
        polygon_points = g['polygons']
        polygon_count = len(polygon_points)
        updated = polygon_count > 0
        g['updated'] = updated
        g['updated_polygon_count'] = \
            polygon_count if updated else g['previous_polygon_count']

        if updated:
            try:
                polygons = [Polygon(points) for points in polygon_points]
                group.border = MultiPolygon(polygons)
                group.clean_and_save()
            except Exception as e:
                return {'error': ("Error updating polygons for group %s: %s"
                                  % (group.name, e.message))}

    return {'updates': group_data.values()}
