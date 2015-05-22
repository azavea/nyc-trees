(SELECT
  block.geom,
  block.id,
  CASE
    -- Not even census admins can reserve an unavailable or already reserved blockface.
    WHEN (block.is_available AND reservation.id IS NULL) THEN 'available'
    -- If a blockface is currently reserved, we should make it look
    -- 'available'.  We use a GeoJSON layer in the UI for the user's
    -- reserved blockfaces, and when a blockface is deselected we want to
    -- be able to reselect it
    WHEN (block.is_available
          AND reservation.user_id IS NOT DISTINCT FROM <%= user_id %>) THEN 'available'
    ELSE 'unavailable'
  END AS survey_type,
  CASE
    WHEN NOT block.is_available THEN 'unavailable'
    WHEN reservation.id IS NOT NULL AND reservation.user_id <> <%= user_id %> THEN 'reserved'
    ELSE 'none'
  END AS restriction
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
) AS query
