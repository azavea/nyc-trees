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

/* If you change these colors, also change src/nyc_trees/sass/partials/_legend.scss */
#survey_borough,#survey_neighborhoodtabulationarea {
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
  [percent >= 80] { polygon-fill: #006d2c }
  [percent >= 90] { polygon-fill: #00441b }
}

/*

Running this command in the windshaft module directory will list available fonts
node -e "var m=require('mapnik');m.register_system_fonts();console.log(m.fontFiles())"

*/

#survey_borough::labels,
#survey_neighborhoodtabulationarea::labels {
  text-name: '[label]';
  text-face-name: 'DejaVu Sans Bold';
  text-fill: #000;
  text-size: 12;
  text-halo-fill:  fadeout(#fff, 30%);
  text-halo-radius: 2;
}
