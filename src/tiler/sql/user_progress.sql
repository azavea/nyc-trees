-- The 'DISTINCT ON' and 'ORDER BY' clause are needed so that we only use
-- the latest survey for a blockface
(SELECT
  DISTINCT ON (block.id)
  block.geom, block.id,
  CASE
    WHEN survey.user_id IS NOT DISTINCT FROM <%= user_id %> THEN 'T'
    WHEN survey.teammate_id IS NOT DISTINCT FROM <%= user_id %> THEN 'T'
    ELSE 'F'
  END AS is_mapped
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_survey AS survey
    ON (block.id = survey.blockface_id
        AND COALESCE(survey.quit_reason, '') = '')
  ORDER BY block.id, survey.created_at DESC NULLS LAST
) AS query
