(SELECT
  <% if (is_utf_grid) { %>
  ST_AsGeoJSON(block.geom) AS geojson,
  <% } %>
  block.geom, block.id,
  CASE
    WHEN block.is_available AND reservation.user_id = <%= user_id %> THEN 'available'
    ELSE 'unavailable'
  END as survey_type,
  'none' as restriction
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.user_id = <%= user_id %>
        AND reservation.expires_at > now() at time zone 'utc')
  <% if (is_utf_grid) { %>
    WHERE block.is_available AND reservation.user_id = <%= user_id %>
  <% } %>
) AS query
