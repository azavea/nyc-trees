WITH trees_for_this_survey AS(
  SELECT
    id,
    survey_id,
    .3408*(CASE WHEN curb_location='OnCurb' THEN 2.5 ELSE 12 END) curb_offset,
    .3408*distance_to_tree dist
  FROM survey_tree
  WHERE survey_id = %s
  ORDER BY id
),
aggregated_trees AS (
  SELECT survey_id, array_agg(curb_offset) width,
         array_agg(0) length, array_agg(dist) dist
  FROM trees_for_this_survey
  GROUP BY survey_id
),
aggs AS (
  SELECT
    s.blockface_id,
    s.is_mapped_in_blockface_polyline_direction,
    s.is_left_side as left_side,
    s.user_id, b.geom,
    r.survey_id, width, length, dist
  FROM
    aggregated_trees r, survey_survey s, survey_blockface b
  WHERE
    r.survey_id = s.id AND b.id = s.blockface_id
),
layed AS (
  SELECT survey_id,
         layoutBoxes(ST_Transform(
             CASE WHEN is_mapped_in_blockface_polyline_direction
             THEN st_geometryn(geom,1)
             ELSE ST_Reverse(st_geometryn(geom,1)) END,
             _ST_BestSRID(geom::geometry)),
         left_side, dist, length, width) as tbeds
  FROM aggs
)
SELECT
  ST_AsGeoJSON(ST_Transform(unnest(tbeds),4326)) as geom
FROM layed
