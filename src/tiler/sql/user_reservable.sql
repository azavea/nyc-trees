(SELECT
  block.geom, block.id, turf.group_id,
  CASE
    WHEN (block.is_available AND reservation.id IS NULL
          AND (turf.id IS NULL OR trustedmapper.id IS NOT NULL)) THEN 'available'
    ELSE 'unavailable'
  END AS survey_type,
  CASE
    WHEN turf.id IS NOT NULL AND trustedmapper.id IS NULL THEN 'group_territory'
    WHEN reservation.id IS NOT NULL THEN 'reserved'
    WHEN NOT block.is_available THEN 'unavailable'
    ELSE 'none'
  END AS restriction
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
  LEFT OUTER JOIN users_trustedmapper AS trustedmapper
    ON (turf.group_id = trustedmapper.group_id
        AND trustedmapper.user_id = <%= user_id %>)
) AS query
