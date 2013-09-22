-- Drops any existing OSMM related tables and creates fresh tables ready to receive data

DROP TABLE IF EXISTS "osmm"."boundaryline" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'boundaryline' AND f_table_schema = 'osmm';

CREATE TABLE "osmm"."boundaryline" ( OGC_FID SERIAL, CONSTRAINT "boundaryline_pk" PRIMARY KEY (OGC_FID) );
SELECT AddGeometryColumn('osmm','boundaryline','wkb_geometry',27700,'GEOMETRY',2);
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "fid" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "featurecode" INTEGER;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "version" INTEGER;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "versiondate" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "theme" varchar[];
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "accuracyofposition" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "changedate" varchar[];
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "reasonforchange" varchar[];
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "descriptivegroup" varchar[];
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "descriptiveterm" varchar[];
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "make" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "physicallevel" INTEGER;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "physicalpresence" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "filename" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "themes" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "descriptivegroups" varchar;
ALTER TABLE "osmm"."boundaryline" ADD COLUMN "descriptiveterms" varchar;

DROP TABLE IF EXISTS "osmm"."cartographicsymbol" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'cartographicsymbol' AND f_table_schema = 'osmm';

CREATE TABLE "osmm"."cartographicsymbol" ( OGC_FID SERIAL, CONSTRAINT "cartographicsymbol_pk" PRIMARY KEY (OGC_FID) );
SELECT AddGeometryColumn('osmm','cartographicsymbol','wkb_geometry',27700,'POINT',2);
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "fid" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "featurecode" INTEGER;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "version" INTEGER;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "versiondate" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "theme" varchar[];
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "changedate" varchar[];
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "reasonforchange" varchar[];
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "descriptivegroup" varchar[];
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "descriptiveterm" varchar[];
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "orientation" INTEGER;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "physicallevel" INTEGER;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "physicalpresence" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "referencetofeature" VARCHAR;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "filename" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "themes" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "descriptivegroups" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "descriptiveterms" varchar;
ALTER TABLE "osmm"."cartographicsymbol" ADD COLUMN "orientdeg" varchar;

DROP TABLE IF EXISTS "osmm"."cartographictext" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'cartographictext' AND f_table_schema = 'osmm';

CREATE TABLE "osmm"."cartographictext" ( OGC_FID SERIAL, CONSTRAINT "cartographictext_pk" PRIMARY KEY (OGC_FID) );
SELECT AddGeometryColumn('osmm','cartographictext','wkb_geometry',27700,'POINT',2);
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "fid" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "featurecode" INTEGER;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "version" INTEGER;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "versiondate" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "theme" varchar[];
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "changedate" varchar[];
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "reasonforchange" varchar[];
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "descriptivegroup" varchar[];
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "descriptiveterm" varchar[];
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "make" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "physicallevel" INTEGER;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "physicalpresence" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "anchorposition" INTEGER;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "font" INTEGER;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "height" FLOAT8;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "orientation" INTEGER;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "textstring" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "filename" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "themes" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "descriptivegroups" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "descriptiveterms" varchar;
ALTER TABLE "osmm"."cartographictext" ADD COLUMN "orientdeg" varchar;


DROP TABLE IF EXISTS "osmm"."topographicarea" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'topographicarea' AND f_table_schema = 'osmm';

CREATE TABLE "osmm"."topographicarea" ( OGC_FID SERIAL, CONSTRAINT "topographicarea_pk" PRIMARY KEY (OGC_FID) );
SELECT AddGeometryColumn('osmm','topographicarea','wkb_geometry',27700,'POLYGON',2);
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "fid" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "featurecode" INTEGER;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "version" INTEGER;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "versiondate" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "theme" varchar[];
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "calculatedareavalue" FLOAT8;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "changedate" varchar[];
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "reasonforchange" varchar[];
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "descriptivegroup" varchar[];
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "descriptiveterm" varchar[];
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "make" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "physicallevel" INTEGER;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "physicalpresence" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "filename" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "themes" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "descriptivegroups" varchar;
ALTER TABLE "osmm"."topographicarea" ADD COLUMN "descriptiveterms" varchar;

DROP TABLE IF EXISTS "osmm"."topographicline" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'topographicline' AND f_table_schema = 'osmm';

CREATE TABLE "osmm"."topographicline" ( OGC_FID SERIAL, CONSTRAINT "topographicline_pk" PRIMARY KEY (OGC_FID) );
SELECT AddGeometryColumn('osmm','topographicline','wkb_geometry',27700,'MULTILINESTRING',2);
ALTER TABLE "osmm"."topographicline" ADD COLUMN "fid" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "featurecode" INTEGER;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "version" INTEGER;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "versiondate" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "theme" varchar[];
ALTER TABLE "osmm"."topographicline" ADD COLUMN "accuracyofposition" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "changedate" varchar[];
ALTER TABLE "osmm"."topographicline" ADD COLUMN "reasonforchange" varchar[];
ALTER TABLE "osmm"."topographicline" ADD COLUMN "descriptivegroup" varchar[];
ALTER TABLE "osmm"."topographicline" ADD COLUMN "descriptiveterm" varchar[];
ALTER TABLE "osmm"."topographicline" ADD COLUMN "nonboundingline" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "heightabovedatum" FLOAT8;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "accuracyofheightabovedatum" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "heightabovegroundlevel" FLOAT8;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "accuracyofheightabovegroundlevel" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "make" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "physicallevel" INTEGER;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "physicalpresence" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "filename" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "themes" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "descriptivegroups" varchar;
ALTER TABLE "osmm"."topographicline" ADD COLUMN "descriptiveterms" varchar;


DROP TABLE IF EXISTS "osmm"."topographicpoint" CASCADE;
DELETE FROM geometry_columns WHERE f_table_name = 'topographicpoint' AND f_table_schema = 'osmm';

CREATE TABLE "osmm"."topographicpoint" ( OGC_FID SERIAL, CONSTRAINT "topographicpoint_pk" PRIMARY KEY (OGC_FID) );
SELECT AddGeometryColumn('osmm','topographicpoint','wkb_geometry',27700,'POINT',2);
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "fid" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "featurecode" INTEGER;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "version" INTEGER;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "versiondate" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "theme" varchar[];
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "accuracyofposition" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "changedate" varchar[];
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "reasonforchange" varchar[];
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "descriptivegroup" varchar[];
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "descriptiveterm" varchar[];
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "heightabovedatum" FLOAT8;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "accuracyofheightabovedatum" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "make" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "physicallevel" INTEGER;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "physicalpresence" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "referencetofeature" VARCHAR;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "filename" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "themes" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "descriptivegroups" varchar;
ALTER TABLE "osmm"."topographicpoint" ADD COLUMN "descriptiveterms" varchar;

