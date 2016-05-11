-- Note: This was adapted into trees.sql, and then further adapted to pull data
-- from the view in src/nyc_trees/survey/views.py.  Try to keep changes in sync
WITH aggs AS (
  SELECT
    %(survey_dir)s as is_mapped_in_blockface_polyline_direction,
    %(left_side)s as left_side,
    b.geom,
    %(tree_offsets)s as width,
    %(tree_distances)s as dist,
    array_fill(0, array[array_length(%(tree_distances)s, 1)]) as length
  FROM survey_blockface b
  WHERE b.id = %(blockface_id)s
),
layed AS (
  SELECT layoutBoxes(ST_Transform(
             CASE WHEN is_mapped_in_blockface_polyline_direction
             THEN st_geometryn(geom,1)
             ELSE ST_Reverse(st_geometryn(geom,1)) END,
             102718), -- state plane, for improved accuracy, feet units
         left_side, dist, length, width) as tbeds
  FROM aggs
)
SELECT
  ST_AsGeoJSON(ST_Transform(unnest(tbeds),4326)) as geom
FROM layed
