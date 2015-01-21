/* If you change these colors, also change src/nyc_trees/sass/partials/_legend.scss */
@surveyed-by-me: #8BC34A;
@surveyed-by-others: #03A9F4;
@available: #7B1FA2;
@reserved: #E64A19;
@unavailable: #455A64;

#survey_blockface {
  line-join: round;
  line-cap: round;

  line-opacity: 1;

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
}
