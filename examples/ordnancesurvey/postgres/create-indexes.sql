-- Creates a spatial index for each OSMM table

CREATE INDEX "boundaryline_geom_idx" ON "osmm"."boundaryline" USING GIST ("wkb_geometry");
CREATE INDEX "cartographicsymbol_geom_idx" ON "osmm"."cartographicsymbol" USING GIST ("wkb_geometry");
CREATE INDEX "cartographictext_geom_idx" ON "osmm"."cartographictext" USING GIST ("wkb_geometry");
CREATE INDEX "topographicarea_geom_idx" ON "osmm"."topographicarea" USING GIST ("wkb_geometry");
CREATE INDEX "topographicline_geom_idx" ON "osmm"."topographicline" USING GIST ("wkb_geometry");
CREATE INDEX "topographicpoint_geom_idx" ON "osmm"."topographicpoint" USING GIST ("wkb_geometry");
