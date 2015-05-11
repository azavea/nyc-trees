Survey Fixtures
===============

## Source Data

All source data shapfiles are in a state plane projection that is not installed in PostGIS by default. The projection can be installed with the following SQL:

```sql
-- Reference: http://spatialreference.org/ref/esri/nad-1983-stateplane-new-york-long-island-fips-3104-feet/postgis/
DELETE from spatial_ref_sys WHERE srid = 102718;
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text,
srtext) values ( 102718, 'esri', 102718, '+proj=lcc
+lat_1=40.66666666666666 +lat_2=41.03333333333333
+lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80
+datum=NAD83 +to_meter=0.3048006096012192 +no_defs ',
'PROJCS["NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["False_Easting",984249.9999999999],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",-74],PARAMETER["Standard_Parallel_1",40.66666666666666],PARAMETER["Standard_Parallel_2",41.03333333333333],PARAMETER["Latitude_Of_Origin",40.16666666666666],UNIT["Foot_US",0.30480060960121924],AUTHORITY["EPSG","102718"]]');

```


## blockface*.json

The blockface data is being provided in borough-level shapefiles. The borough shapefiles can be loaded into the database with ``shp2pgsql``:

```
shp2pgsql -s 102718:4326 -g geom ManhattanSegments_Compiled.shp | psql -d nyc_trees
```

The borough blockfaces can be appended to the ``survey_blockface`` table with the following SQL:

```sql

INSERT INTO survey_blockface (
  is_available,
  created_at,
  updated_at,
  expert_required,
  source,
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  'bronx',
  geom
FROM bronx_compiled
WHERE geom IS NOT NULL
);

```

On deployment the blockfaces are loaded from files named
``blockface_*.json`` in the ``src/nyc_trees/apps/survey/fixtures/``
directory. These fixtures are maintained by filling the
``survey_blockface`` table with the appropriate data, then exporting
the fixture:

```
./scripts/manage.sh dumpdata survey.Blockface > src/nyc_trees/apps/survey/fixtures/blockface_500000_bronx.json
```

Using a single fixture for all the blockfaces causes memory errors in
``DEBUG_MODE``, so we generate fixtures for each individual borough by
emptying the blockface table, adjusting the ID sequence, importing a
borough, dumping a fixture, then repeating for the other boroughs.

The largest borough has just over 50000 blockfaces, so by manipulating
the blockface ID seqence allows use to have 6 digit IDs for every
blockface where the 6th digit represents the borough.

``SELECT setval('survey_blockface_id_seq', 99999);
-- Load Manhattan, which starts at 100000
SELECT setval('survey_blockface_id_seq', 199999);
-- Load Brooklyn, which starts at 200000
-- etc.``


## borough.json

### How to create the fixture

- Download the [boroughs shapefile](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm)

- Load the shapefile into the services vagrant VM:

```
shp2pgsql -s 102718:4326 -g geom nybb.shp | \
psql -h localhost -p 15432 -U nyc_trees -d nyc_trees
```

- Fill the Django model table with the shapefile data:

```sql
INSERT INTO survey_borough (
  created_at,
  updated_at,
  geom,
  code,
  name
)
(
SELECT
  now() at time zone 'utc',
  now() at time zone 'utc',
  geom,
  borocode,
  boroname
FROM nybb
);
```

- Dump the data as a fixture

```
./scripts/manage.sh dumpdata survey.Borough > src/nyc_trees/apps/survey/fixtures/borough.json
```

## neighborhoodtabulationarea.json

### How to create the fixture

- Download the [NTA shapefile](https://data.cityofnewyork.us/City-Government/Neighborhood-Tabulation-Areas/cpf4-rkhq)

- Load the shapefile into the services vagrant VM:

```
shp2pgsql -s 102718:4326 -g geom nynta.shp | psql -p 15432 -h localhost -U nyc_trees -d nyc_trees
```

- Fill the Django model table with the shapefile data:

```sql
INSERT INTO survey_neighborhoodtabulationarea (
  created_at,
  updated_at,
  geom,
  code,
  name
)
(
SELECT
  now() at time zone 'utc',
  now() at time zone 'utc',
  geom,
  ntacode,
  ntaname
FROM nynta
```

- Dump the data as a fixture

```
./scripts/manage.sh dumpdata survey.NeighborhoodTabulationArea > src/nyc_trees/apps/survey/fixtures/neighborhoodtabulationarea.json
```
