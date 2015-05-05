(SELECT
  block.geom,
  block.id,
  turf.group_id,
  core_group.slug AS group_slug,
  CASE
    WHEN (block.is_available AND reservation.id IS NULL
          AND (turf.id IS NULL
               OR trustedmapper.id IS NOT NULL
               OR core_group.admin_id = <%= user_id %>)) THEN 'available'
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
    WHEN (core_group.id IS NOT NULL
          AND NOT core_group.allows_individual_mappers
          AND NOT core_group.admin_id = <%= user_id %>) THEN 'unavailable'
    WHEN reservation.id IS NOT NULL AND reservation.user_id <> <%= user_id %> THEN 'reserved'
    -- Designate as "group_territory" if block belongs to a group and the user
    -- is neither a trusted mapper nor a group admin.
    -- Don't filter out inactive groups or else non trusted mappers will be
    -- able to reserve blocks in the "expert" group.
    WHEN (turf.id IS NOT NULL
          AND trustedmapper.id IS NULL
          AND core_group.admin_id <> <%= user_id %>) THEN 'group_territory'
    ELSE 'none'
  END AS restriction
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT JOIN core_group ON core_group.id = turf.group_id
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
  LEFT OUTER JOIN users_trustedmapper AS trustedmapper
    ON (turf.group_id = trustedmapper.group_id
        AND trustedmapper.user_id = <%= user_id %>
        AND trustedmapper.is_approved)
) AS query
