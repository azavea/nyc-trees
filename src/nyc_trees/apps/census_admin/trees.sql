WITH trees_for_this_survey AS(
  SELECT
    id,
    survey_id,
    .3408*(CASE WHEN curb_location='OnCurb' THEN 2.5 ELSE 12 END) curb_offset,
    .3408*distance_to_tree dist
  FROM survey_tree
  ORDER BY id
),
aggregated_trees AS (
  SELECT survey_id, array_agg(curb_offset) width,
         array_agg(0) length, array_agg(dist) dist, array_agg(id) tree_ids
  FROM trees_for_this_survey
  GROUP BY survey_id
),
aggs AS (
  SELECT
    s.blockface_id,
    s.is_mapped_in_blockface_polyline_direction,
    s.is_left_side as left_side,
    s.user_id, b.geom,
    r.survey_id, width, length, dist,
    r.tree_ids
  FROM
    aggregated_trees r, survey_survey s, survey_blockface b
  WHERE
    r.survey_id = s.id AND b.id = s.blockface_id
),
layed AS (
  SELECT survey_id,
         tree_ids,
         layoutBoxes(ST_Transform(
             CASE WHEN is_mapped_in_blockface_polyline_direction
             THEN st_geometryn(geom,1)
             ELSE ST_Reverse(st_geometryn(geom,1)) END,
             _ST_BestSRID(geom::geometry)),
         left_side, dist, length, width) as tbeds
  FROM aggs
),
tree_geoms AS (
  SELECT
    ST_AsGeoJSON(ST_Transform(unnest(tbeds),4326)) as geom, unnest(tree_ids) as tree_id
  FROM layed
)
SELECT
  geom,
  t.id, t.survey_id, t.species_id, t.distance_to_tree, t.distance_to_end,
  t.circumference, t.stump_diameter, t.curb_location, t.status,
  t.species_certainty, t.health, t.stewardship, t.guards, t.sidewalk_damage,
  t.problems, t.created_at, t.updated_at
FROM tree_geoms, survey_tree t
WHERE t.id = tree_geoms.tree_id
