(SELECT
  block.id,
  block.geom,
  <% if (is_utf_grid) { %>
  ST_AsGeoJSON(block.geom) AS geojson,
  <% } %>
  CASE
    WHEN (block.is_available AND reservation.id IS NULL) THEN 'available'
    ELSE 'unavailable'
  END AS survey_type,
  'none' AS restriction
  FROM survey_blockface AS block
  INNER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
  WHERE turf.group_id = <%= group_id %>
) AS query
