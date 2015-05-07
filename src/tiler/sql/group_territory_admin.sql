(SELECT
  block.id,
  block.geom,
  turf.group_id AS turf_group_id,
  CASE
    WHEN block.is_available THEN
      CASE
        WHEN turf.group_id = <%= group_id %> THEN 'reserved'
        WHEN turf.group_id IS NOT NULL
          OR reservation.id IS NOT NULL THEN 'unavailable'
        ELSE 'available'
      END
    ELSE
      CASE
        WHEN turf.group_id = <%= group_id %> THEN 'surveyed-by-me'
        ELSE 'surveyed-by-others'
      END
  END AS survey_type,
  'none' AS restriction

  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
) AS query
