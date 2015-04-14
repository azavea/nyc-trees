/* If you change these colors, also change src/nyc_trees/sass/partials/_legend.scss */
@mapped: #8BC34A;
@not-mapped: #aaa;
@not-mapped-zoomed-out: #ccc;

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
    line-color: @mapped;
    [zoom <= 16]{ line-width: 6; }
  }
  [survey_type = 'surveyed-by-others'] {
    line-color: <% if (type === 'progress_all') { %> @mapped <% } else { %> @not-mapped <% } %>;
    [zoom <= 16]{ line-width: 6; }
  }

  [survey_type = 'available'] {
    line-color: @not-mapped;
    [zoom <= 15]{
      line-color: @not-mapped-zoomed-out;
    }
  }
  [survey_type = 'reserved'] {
    line-color: @not-mapped;
    [zoom <= 15]{
      line-color: @not-mapped-zoomed-out;
    }
  }
  [survey_type = 'unavailable'] {
    line-color: @not-mapped;
    [zoom <= 15]{
      line-color: @not-mapped-zoomed-out;
    }
  }
}
