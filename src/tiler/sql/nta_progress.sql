(SELECT geom, name, agg.* FROM (
  SELECT nta_id,
         SUM(is_mapped) as mapped,
         COUNT(is_mapped) as total,
         100 * SUM(is_mapped) / COUNT(is_mapped)::float as percent,
         ROUND(100 * SUM(is_mapped) / COUNT(is_mapped)::float)::text || '%' as label
  FROM (
    SELECT
    DISTINCT ON (block.id)
    block.nta_id,
    CASE
      WHEN survey.id IS NOT NULL THEN 1
      ELSE 0
    END AS is_mapped
    FROM survey_blockface AS block
    LEFT OUTER JOIN survey_survey AS survey
      ON block.id = survey.blockface_id
    ORDER BY block.id
  ) AS s
  GROUP BY nta_id
) AS agg
LEFT JOIN survey_neighborhoodtabulationarea on agg.nta_id = survey_neighborhoodtabulationarea.id) as query
