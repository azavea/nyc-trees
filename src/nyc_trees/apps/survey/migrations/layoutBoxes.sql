--
-- This file is part of Treekit.
--
-- Copyright (C) 2015 Sandro Santilli <strk@keybit.net>
--
-- Treekit is free software: you can redistribute it and/or modify
-- it under the terms of the Affero GNU General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License, or (at your option) any later version.
--
-- Treekit is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the Affero GNU General Public License
-- along with Treekit.  If not, see <http://www.gnu.org/licenses/>.
--


-- {
--
-- Given two points and an offset return an offsetted segment
--
-- Positive offset will generate line on the left,
-- negative on the right. Direction will be the same of input.
--
-- Author: Sandro Santilli <strk@keybit.net>
--
-- }{
CREATE OR REPLACE FUNCTION _tk_OffsetSegment(p0 geometry, p1 geometry, off float8)
RETURNS geometry  AS
$$
DECLARE
  theta FLOAT8;
  x0 FLOAT8;
  y0 FLOAT8;
  x1 FLOAT8;
  y1 FLOAT8;
  g GEOMETRY;
BEGIN
  x0 := ST_X(p0);
  y0 := ST_Y(p0);
  x1 := ST_X(p1);
  y1 := ST_Y(p1);
  theta := atan2(y1 - y0, x1 - x0);
  x0 := x0 - sin(theta) * off;
  y0 := y0 + cos(theta) * off;
  x1 := x1 - sin(theta) * off;
  y1 := y1 + cos(theta) * off;

  g := ST_MakeLine(
    ST_MakePoint(x0, y0),
    ST_MakePoint(x1, y1)
  );

  return ST_SetSRID(g, ST_SRID(p0));
END;
$$
LANGUAGE 'plpgsql' IMMUTABLE STRICT;

-- {
--
-- Given a linestring and an ordered array of box data, return an array of
-- boxes placed along the given geometry.
--
-- Box data arrays meaning: dist is the distance from the end of previous box
-- (or start of line for the first element); length is the length along the
-- line of the box; width is the width of the box, hortogonal to the line.
--
-- Tree measures are expected to be in the linestring's coordinate units.
--
-- Author: Sandro Santilli <strk@keybit.net>
--
-- }{
CREATE OR REPLACE FUNCTION layoutBoxes(line geometry, left_side boolean, dist float8[], len float8[], width float8[], off float8[])
RETURNS geometry[] AS
$$
DECLARE
  l0 GEOMETRY; -- offsetted geometry 0
  l1 GEOMETRY; -- offsetted geometry 1
  roadrec RECORD;
  tree RECORD;
  curdst FLOAT8; -- current distance from road's start point, in meters
  p0 GEOMETRY;
  p1 GEOMETRY;
  distfrac FLOAT8; -- fraction of distance along the line
  ret GEOMETRY;
  boxes GEOMETRY[];
  i INTEGER;
BEGIN


  SELECT line as geom, ST_Length(line) as len,
         CASE WHEN left_side THEN 1 ELSE -1 END as side
    INTO roadrec;

  curdst := 0;
  FOR i IN 1 .. array_upper(dist, 1)
  LOOP
    SELECT dist[i] as dist,
           len[i] as len,
           width[i] as width,
           off[i] as off
    INTO tree;

    --RAISE DEBUG 'Box % dist:% len:% width:% offset:%', i, tree.dist, tree.len, tree.width, tree.off;

    curdst := curdst + tree.dist;
    distfrac := curdst/roadrec.len;
    distfrac := greatest(least(distfrac,1),0); -- warn if clamped ?
    p0 := ST_Line_Interpolate_Point(roadrec.geom, distfrac);
    IF tree.len = 0 THEN
      -- This is an arbitrarily small number used
      -- to obtain another point possibly on the same segment
      IF distfrac >= 1 - 1e-7 THEN
        distfrac := distfrac - 1e-7;
        tree.off := -tree.off;
        tree.width := -tree.width;
      ELSE
        distfrac := distfrac + 1e-7;
      END IF;
    ELSE
      IF curdst >= roadrec.len THEN
        RAISE WARNING 'Tree bed cannot start at the end of road';
        CONTINUE;
      END IF;
      curdst := curdst + tree.len;
      distfrac := curdst/roadrec.len;
      distfrac := greatest(least(distfrac,1),0); -- warn if clamped ?
    END IF;
    p1 := ST_Line_Interpolate_Point(roadrec.geom, distfrac);
    l0 := ST_MakeLine(p0, p1);

    IF tree.off IS NOT NULL THEN
      l0 := _tk_OffsetSegment(ST_PointN(l0,1), ST_PointN(l0,2), tree.off*roadrec.side);
    END IF;

    l1 := _tk_OffsetSegment(ST_PointN(l0,1), ST_PointN(l0,2), tree.width*roadrec.side);

    IF tree.len = 0 THEN
      ret := ST_PointN(l1, 1);
    ELSE
      ret := ST_MakeLine(l0, ST_Reverse(l1));
      ret := ST_MakeLine(ret, ST_StartPoint(l0)); -- add closing point
      ret := ST_MakePolygon(ret); -- turn into a polygon
    END IF;

    --RAISE DEBUG 'Box %: %', i, ST_AsEWKT(ret);

    boxes := array_append(boxes, ret);

  END LOOP;

  RETURN boxes;

END
$$
LANGUAGE 'plpgsql' IMMUTABLE STRICT;
-- }{
-- Kept for backward compatibility
CREATE OR REPLACE FUNCTION layoutBoxes(line geometry, left_side boolean, dist float8[], len float8[], width float8[])
RETURNS geometry[] AS
$$
 SELECT layoutBoxes($1, $2, $3, $4, $5, ARRAY[]::float8[]);
$$
LANGUAGE 'sql' IMMUTABLE STRICT;
-- }
