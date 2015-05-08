/* If you change these colors, also change src/nyc_trees/sass/partials/_legend.scss */
@surveyed-by-me: #228F73;
@surveyed-by-others: #8BC34A;
@available: #36b5db;
@reserved: #e55934;
@unavailable: #aaa;

#survey_blockface {
  line-join: round;
  line-cap: round;

  line-opacity: 1;

  // Note: this must be kept in sync with src/nyc_trees/js/src/BlockfaceLayer.js
  line-width: 1;
  [zoom = 16]{ line-width: 2; }
  [zoom = 17]{ line-width: 4; }
  [zoom = 18]{ line-width: 8; }
  [zoom = 19]{ line-width: 16; }

  [survey_type = 'surveyed-by-me'] {
    line-color: @surveyed-by-me;
  }
  [survey_type = 'surveyed-by-others'] {
    line-color: @surveyed-by-others;
  }
  [survey_type = 'available'] {
    line-color: @available;
  }
  [survey_type = 'reserved'] {
    line-color: @reserved;
  }
  [survey_type = 'unavailable'] {
    line-color: @unavailable;
  }

  /* restriction rules must come after the survey_type rules so they can override styling */
  [restriction = 'unavailable'] {
    line-color: @unavailable;
  }
}
