-- This script records how I emptied and filled the survey_blockface
-- table borough by borough to generate multiple blockface
-- fixtures. It is mainly for reference, not repeated execution.

DELETE FROM survey_blockface;
SELECT setval('survey_blockface_id_seq', 99999);
INSERT INTO survey_blockface (
  is_available,
  created_at,
  updated_at,
  expert_required,
  source,
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  'manhattan',
  geom
FROM manhattansegments_compiled
WHERE geom IS NOT NULL
);

--------------------------------------------------------------------------------

DELETE FROM survey_blockface;
SELECT setval('survey_blockface_id_seq', 199999);
INSERT INTO survey_blockface (
  is_available,
  created_at,
  updated_at,
  expert_required,
  source,
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  'brooklyn',
  geom
FROM brooklyn_compiled_full
WHERE geom IS NOT NULL
);

--------------------------------------------------------------------------------

DELETE FROM survey_blockface;
SELECT setval('survey_blockface_id_seq', 299999);
INSERT INTO survey_blockface (
  is_available,
  created_at,
  updated_at,
  expert_required,
  source,
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  'queens',
  geom
FROM queens_compiled_3_21_15
WHERE geom IS NOT NULL
);


--------------------------------------------------------------------------------

DELETE FROM survey_blockface;
SELECT setval('survey_blockface_id_seq', 399999);
INSERT INTO survey_blockface (
  is_available,
  created_at,
  updated_at,
  expert_required,
  source,
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  'si',
  geom
FROM statenislandcompiled
WHERE geom IS NOT NULL
);

--------------------------------------------------------------------------------

DELETE FROM survey_blockface;
SELECT setval('survey_blockface_id_seq', 499999);
INSERT INTO survey_blockface (
  is_available,
  created_at,
  updated_at,
  expert_required,
  source,
  geom
)
(
SELECT
  TRUE,
  now() at time zone 'utc',
  now() at time zone 'utc',
  CASE WHEN expertmapp = 1 THEN TRUE ELSE FALSE END,
  'bronx',
  geom
FROM bronx_compiled
WHERE geom IS NOT NULL
);


--------------------------------------------------------------------------------

DELETE FROM survey_blockface;
