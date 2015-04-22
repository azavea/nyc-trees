(SELECT
  block.geom, block.id,
  CASE
    WHEN (survey.user_id IS NOT DISTINCT FROM <%= user_id %>
          OR survey.teammate_id IS NOT DISTINCT FROM <%= user_id %>) THEN 'T'
    ELSE 'F'
  END AS is_mapped
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_survey AS survey
    ON block.latest_survey_id = survey.id
) AS query
