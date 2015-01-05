# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json
from django.http import HttpResponse


def make_json_404(dict):
    """
    A JSON API helper for returning Not Found with structured data.
    """
    response = HttpResponse()
    response.status_code = 404
    response.write(json.dumps(dict))
    response['Content-length'] = str(len(response.content))
    response['Content-Type'] = "application/json"
    return response
