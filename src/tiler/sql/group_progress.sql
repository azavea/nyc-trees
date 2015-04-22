(SELECT
  block.geom, block.id,
  CASE
    WHEN block.latest_survey_id IS NOT NULL THEN 'T'
    ELSE 'F'
  END AS is_mapped
  FROM survey_blockface AS block
  JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  WHERE turf.group_id = <%= group_id %>
) AS query
