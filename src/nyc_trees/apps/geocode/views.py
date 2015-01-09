# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.contrib.gis.geos.point import Point

from omgeo import Geocoder
from omgeo.places import Viewbox, PlaceQuery

from libs.response import make_json_404

geocoder = Geocoder(sources=settings.OMGEO_SETTINGS)
GEOCODE_FALLBACK_SUFFIX = getattr(settings, 'GEOCODE_FALLBACK_SUFFIX', None)


def geocode(request):
    """
    Geocode a string address.

    Configuration for sources is pulled from the OMGEO_SETTINGS
    settings key
    """
    address = request.REQUEST['address']

    candidates = _get_candidates(address)
    if candidates:
        return _make_response_dict(candidates)
    else:
        address_with_city = address + GEOCODE_FALLBACK_SUFFIX
        candidates = _get_candidates(address_with_city)
        if candidates:
            return _make_response_dict(candidates)
        else:
            return _make_no_results_response(address_with_city)


def _get_candidates(query):
    pq = PlaceQuery(query=query, viewbox=_build_viewbox())

    geocode_result = geocoder.geocode(pq)
    candidates = geocode_result.get('candidates', None)

    if not candidates or len(candidates) == 0:
        return None
    else:
        candidates = [_omgeo_candidate_to_dict(c) for c in candidates]

        bbox_dict = _build_bbox_dict()
        candidates = [c for c in candidates if _in_bbox(bbox_dict, c)]
        if len(candidates) > 0:
            return candidates
        else:
            return None


def _make_response_dict(candidates):
    return {'candidates': candidates}


def _omgeo_candidate_to_dict(candidate, srid=4326):
    p = Point(candidate.x, candidate.y, srid=candidate.wkid)
    if candidate.wkid != srid:
        p.transform(srid)
    return {'address': candidate.match_addr,
            'srid': p.srid,
            'score': candidate.score,
            'x': p.x,
            'y': p.y}


def _make_no_results_response(address):
    err = "No results found for %(address)s"
    content = {'error': err % {'address': address}}
    return make_json_404(content)


def _in_bbox(bbox, c):
    x, y = c['x'], c['y']

    valid_x = x >= float(bbox['xmin']) and x <= float(bbox['xmax'])
    valid_y = y >= float(bbox['ymin']) and y <= float(bbox['ymax'])

    return valid_x and valid_y


def _build_viewbox():
    xmin, ymin, xmax, ymax = settings.NYC_BOUNDS
    return Viewbox(left=float(xmin),
                   right=float(xmax),
                   bottom=float(ymin),
                   top=float(ymax),
                   wkid=4326)


def _build_bbox_dict():
    xmin, ymin, xmax, ymax = settings.NYC_BOUNDS
    return {'xmin': xmin, 'ymin': ymin,
            'xmax': xmax, 'ymax': ymax}
