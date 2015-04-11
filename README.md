nyc-trees
=========

NYC Parks Trees Count! 2015 tree census

## Local Development

A combination of Vagrant 1.5+ and Ansible 1.8+ is used to setup the development environment for this project. It of the following virtual machines:

- `app`
- `tiler`
- `services`

The `app` virtual machine contains an instance of the Django application, `tiler` contains a tiling server, and `services` contains shared resources of `app` and `tiler`:

- PostgreSQL
- Redis
- Logstash
- Kibana
- Graphite
- Statsite

Use the following command to bring up a local development environment:

```bash
$ vagrant up
```

After provisioning is complete, you can login to the application server to execute Django management commands:

```bash
$ vagrant ssh app
vagrant@app:~$ envdir /etc/nyc-trees.d/env /opt/app/manage.py test
```

**Note**: If you get an error that resembles the following, try logging into the `app` virtual machine again for the group permissions changes to take effect:

```
envdir: fatal: unable to switch to directory /etc/nyc-trees.d/env: access denied
```

### Ports

The Vagrant configuration maps the following host ports to services
running in the VMs. You can change the host port numbers by setting
the environment variables listed in the ``Env Variable Override``
column.

Service                | Port  | URL
---------------------- | ----- | ------------------------------------------------
Django Web Application | 8000  | [http://localhost:8000](http://localhost:8000)
Graphite Dashboard     | 8080  | [http://localhost:8080](http://localhost:8080)
Kibana Dashboard       | 15601 | [http://localhost:15601](http://localhost:15601)
Tasseo                 | 15000 | [http://localhost:15000](http://localhost:15000)
PostgreSQL             | 15432 |
pgweb                  | 15433 | [http://localhost:15433](http://localhost:15433)
Redis                  | 16379 | `redis-cli -h localhost 16379`
livereload             | 35729 | (for gulp watch)
LiveServer Tests       | 9001  | (for Sauce Labs)
Testem                 | 7357  |


### JavaScript and CSS

The main tool used is [gulp](http://gulpjs.com/), which is exposed through `npm run` to avoid version conflicts.

 - To create JS bundles, compile sass, and concatenate third-party css, minify CSS and JS, and version files using `gulp-rev-all`, use `gulp` or `npm run build`.
 - To do the above but skip minification and versioning, use `gulp build --debug` or `npm run build-debug`.
 - To watch files and automatically rebuild the JS or sass files when they change, use `gulp watch --debug` or `npm run watch`.  This will also start a [livereload server](http://livereload.com/).

`gulp build` and `gulp watch` without the `--debug` flag are intentionally not exposed through `npm run`.

### Caching

In order to speed up things up, you may want to consider using a local caching proxy. The `VAGRANT_PROXYCONF_ENDPOINT` environment variable provides a way to supply a caching proxy endpoint for the virtual machines to use:

```bash
$ VAGRANT_PROXYCONF_ENDPOINT="http://192.168.96.10:8123/" vagrant up
```

## Data

The blockface data is being provided in borough-level
shapefiles. These shapefiles are in a state plane projection that is
not installed in PostGIS by default. The projection can be installed
with the following SQL:

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

The borough shapefiles can be loaded into the database with ``shp2pgsql``:

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
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  geom
FROM bronx_compiled
WHERE geom IS NOT NULL
);

```

On deployment the blockfaces are loaded from the
``src/nyc_trees/apps/survey/fixtures/blockface.json`` fixture. This fixture is maintained by filling the ``survey_blockface`` table with
the appropriate data, then exporting the fixture:

```
./scripts/manage.sh dumpdata survey.Blockface > src/nyc_trees/apps/survey/fixtures/blockface.json
```

When all 5 boroughs have been added, the resulting fixture is too
large for the ``loaddata`` command. The fixture needs to be split into
chunks. This process is not fully automated.

This pipline will take a fixture created with ``dumpdata`` on stdin
and output one object per line.

```
# convert a JSON array to linewise objects with trailing commas
# embedded newline is IMPORTANT
# sed -e 's/ *$//' trims whitespace
sed -e 's/{"fields/\
{"fields/g' |  sed -e '$s/]$/,/' | sed -e 's/ *$//' | tail -n +2
```

The ``split`` program can chunk up the resulting file

```
split -l 20000 blockface-linewise.json
```

This pipeline will take a file containing linewise objects and convert
it to a valid JSON array. Each of the files created by the split
command should be run through this pipeline to create usable fixtures.

```
# wrap linewise trailing comma objects with array
sed -e '1s/^/[/' | sed -e '$s/,$/]/'
```

## Testing

In order to simulate the testing environment used in CI, bring up the testing environment with:

```
$ VAGRANT_ENV="TEST" vagrant up
```

Once that is complete, execute the top-level test suite responsible for linting and unit testing the client and server-side components:

```bash
$ ./scripts/test.sh
```

If you want to run the integration tests, use the following command:

```bash
$ ./scripts/manage.sh selenium
```

In addition, other [scripts](scripts/) exist if you want to test just one of the client or server-side components.

## Deployment

For more details around the Amazon Web Services deployment process, please see the deployment [README](deployment/README.md).d
