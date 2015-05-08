(SELECT
  block.geom, 'reserved' as survey_type, 'none' AS restriction
  FROM survey_blockface AS block
  INNER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.user_id = <%= user_id %>
        AND reservation.expires_at > now() at time zone 'utc')
  WHERE block.is_available
) AS query
