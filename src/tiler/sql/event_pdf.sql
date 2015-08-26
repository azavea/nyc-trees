-- The 'DISTINCT ON' and 'ORDER BY' clause are needed so that we only use
-- the latest survey for a blockface
(SELECT
  DISTINCT ON (block.id)
  block.geom, block.id,
  CASE
    WHEN survey.user_id IS NOT NULL THEN 'T'
    ELSE 'F'
  END AS is_mapped
  FROM survey_blockface AS block
  JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT OUTER JOIN survey_survey AS survey
    ON block.id = survey.blockface_id
  WHERE turf.group_id = <%= group_id %>
  ORDER BY block.id, survey.created_at DESC NULLS LAST
) AS query
