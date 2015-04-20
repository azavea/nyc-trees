/* If you change these colors, also change src/nyc_trees/sass/partials/_legend.scss */
@mapped: #8BC34A;
@not-mapped: #85664B;
@not-mapped-zoomed-out: #85664B;

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

  [is_mapped = 'T'] {
    line-color: @mapped;
    [zoom <= 17]{ line-width: 6; }
  }
  [is_mapped = 'F'] {
    line-color: @not-mapped;
    [zoom <= 15]{
      line-color: @not-mapped-zoomed-out;
    }
  }
}
