-- The 'DISTINCT ON' and 'ORDER BY' clause are needed so that we only use
-- the latest survey for a blockface
(SELECT
  DISTINCT ON (block.id)
  <% if (is_utf_grid) { %>
  ST_AsGeoJSON(block.geom) AS geojson,
  <% } %>
  block.geom, block.id, turf.group_id,
  CASE
    WHEN survey.id IS NOT NULL THEN 'surveyed-by-others'
    WHEN (turf.id IS NULL AND block.is_available AND reservation.id IS NULL) THEN 'available'
    ELSE 'unavailable'
  END AS survey_type
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT OUTER JOIN survey_survey AS survey
    ON block.id = survey.blockface_id
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
  ORDER BY block.id, survey.created_at DESC NULLS LAST
) AS query
