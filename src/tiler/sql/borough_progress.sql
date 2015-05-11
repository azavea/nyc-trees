(SELECT geom, name, agg.* FROM (
  SELECT borough_id,
         SUM(is_mapped) as mapped,
         COUNT(is_mapped) as total,
         100 * SUM(is_mapped) / COUNT(is_mapped)::float as percent,
         ROUND(100 * SUM(is_mapped) / COUNT(is_mapped)::float)::text || '%'  as label
  FROM (
    SELECT
    DISTINCT ON (block.id)
    block.borough_id,
    CASE
      WHEN survey.id IS NOT NULL THEN 1
      ELSE 0
    END AS is_mapped
    FROM survey_blockface AS block
    LEFT OUTER JOIN survey_survey AS survey
      ON (block.id = survey.blockface_id
          AND COALESCE(survey.quit_reason, '') = '')
    ORDER BY block.id
  ) AS s
  GROUP BY borough_id
) AS agg
LEFT JOIN survey_borough on agg.borough_id = survey_borough.id) as query
