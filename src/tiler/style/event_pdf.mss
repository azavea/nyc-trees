#survey_blockface {
  line-join: round;
  line-cap: round;
  line-opacity: 1;

  [is_mapped = 'F'] {
    line-width: 4;
    line-color: #82471a;
  }
  [is_mapped = 'T'] {
    line-width: 2;
    line-color: #8BC34A;
  }
}
