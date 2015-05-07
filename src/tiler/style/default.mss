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


#survey_borough {
  line-color: #555;
  line-width: 1;
  polygon-opacity: 0.50;
  polygon-fill: #fff;
  [percent >= 10] { polygon-fill: #f7fcfd }
  [percent >= 20] { polygon-fill: #e5f5f9 }
  [percent >= 30] { polygon-fill: #ccece6 }
  [percent >= 40] { polygon-fill: #99d8c9 }
  [percent >= 50] { polygon-fill: #66c2a4 }
  [percent >= 60] { polygon-fill: #41ae76 }
  [percent >= 70] { polygon-fill: #238b45 }
  [percent >= 80] { polygon-fill: #005824 }
}

/*

Running this command in the windshaft module directory will list available fonts
node -e "var m=require('mapnik');m.register_system_fonts();console.log(m.fontFiles())"

*/

#survey_borough::labels {
  text-name: '[label]';
  text-face-name: 'DejaVu Sans Bold';
  text-fill: #000;
  text-size: 12;
  text-halo-fill:  fadeout(#fff, 30%);
  text-halo-radius: 2;
}


#survey_neighborhoodtabulationarea {
  line-color: #555;
  line-width: 1;
  polygon-opacity: 0.50;
  polygon-fill: #fff;
  [percent >= 10] { polygon-fill: #f7fcfd }
  [percent >= 20] { polygon-fill: #e5f5f9 }
  [percent >= 30] { polygon-fill: #ccece6 }
  [percent >= 40] { polygon-fill: #99d8c9 }
  [percent >= 50] { polygon-fill: #66c2a4 }
  [percent >= 60] { polygon-fill: #41ae76 }
  [percent >= 70] { polygon-fill: #238b45 }
  [percent >= 80] { polygon-fill: #005824 }
}

#survey_neighborhoodtabulationarea::labels {
  text-name: '[label]';
  text-face-name: 'DejaVu Sans Bold';
  text-fill: #000;
  text-size: 12;
  text-halo-fill: fadeout(#fff, 30%);
  text-halo-radius: 2;
}
