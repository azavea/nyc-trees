(SELECT
  block.geom, 'reserved' as survey_type, 'none' AS restriction
  FROM survey_blockface AS block
  INNER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  WHERE turf.group_id = <%= group_id %>
) AS query
