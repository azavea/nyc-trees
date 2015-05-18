# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


from django.core.management.base import BaseCommand
from django.db import transaction, connection


class Command(BaseCommand):
    """
    Add the ESRI NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet
    projection to the database (which is the projection in which the block
    edges were produced, and the projection in which geometry construction
    is the most accurate)

    Usage:

    ./manage.py insert_state_plane_projection
    """
    @transaction.atomic
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Based on http://spatialreference.org/ref/esri/102718/postgis/
            sql = """
DELETE FROM spatial_ref_sys WHERE srid = 102718;
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext)
VALUES ( 102718, 'esri', 102718, '+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs ', 'PROJCS["NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["False_Easting",984249.9999999999],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",-74],PARAMETER["Standard_Parallel_1",40.66666666666666],PARAMETER["Standard_Parallel_2",41.03333333333333],PARAMETER["Latitude_Of_Origin",40.16666666666666],UNIT["Foot_US",0.30480060960121924],AUTHORITY["EPSG","102718"]]');
"""  # NOQA
            cursor.execute(sql)
