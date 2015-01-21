(SELECT
  block.geom, block.id, 'reserved' as survey_type
  FROM survey_blockface AS block
  INNER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
  WHERE reservation.user_id = <%= user_id %>
) AS query
