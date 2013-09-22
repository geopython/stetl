CREATE TABLE itn.ferrylink
(
  ogc_fid serial NOT NULL,
  wkb_geometry geometry,
  version integer,
  versiondate text,
  theme text,
  changedate character varying[],
  reasonforchange character varying[],
  descriptivegroup text,
  directednode_ref character varying[],
  directednode_orientation integer[],
  fid text,
  filename text,
  CONSTRAINT ferrylink_pk PRIMARY KEY (ogc_fid ),
  CONSTRAINT enforce_dims_wkb_geometry CHECK (st_ndims(wkb_geometry) = 2),
  CONSTRAINT enforce_srid_wkb_geometry CHECK (st_srid(wkb_geometry) = (-1))
)
WITH (
  OIDS=FALSE
);

CREATE TABLE itn.ferrynode
(
  ogc_fid serial NOT NULL,
  wkb_geometry geometry,
  version integer,
  versiondate text,
  theme text,
  changedate character varying[],
  reasonforchange character varying[],
  descriptivegroup text,
  fid text,
  filename text,
  CONSTRAINT ferrynode_pk PRIMARY KEY (ogc_fid ),
  CONSTRAINT enforce_dims_wkb_geometry CHECK (st_ndims(wkb_geometry) = 2),
  CONSTRAINT enforce_geotype_wkb_geometry CHECK (geometrytype(wkb_geometry) = 'POINT'::text OR wkb_geometry IS NULL),
  CONSTRAINT enforce_srid_wkb_geometry CHECK (st_srid(wkb_geometry) = 27700)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE itn.informationpoint
(
  ogc_fid serial NOT NULL,
  wkb_geometry geometry,
  version integer,
  versiondate text,
  theme text,
  changedate character varying[],
  reasonforchange character varying[],
  descriptivegroup text,
  junctionname text,
  fid text,
  filename text,
  CONSTRAINT informationpoint_pk PRIMARY KEY (ogc_fid ),
  CONSTRAINT enforce_dims_wkb_geometry CHECK (st_ndims(wkb_geometry) = 2),
  CONSTRAINT enforce_geotype_wkb_geometry CHECK (geometrytype(wkb_geometry) = 'POINT'::text OR wkb_geometry IS NULL),
  CONSTRAINT enforce_srid_wkb_geometry CHECK (st_srid(wkb_geometry) = 27700)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE itn.road
(
  ogc_fid serial NOT NULL,
  wkb_geometry geometry,
  version integer,
  versiondate text,
  theme text,
  changedate character varying[],
  reasonforchange character varying[],
  descriptivegroup text,
  roadname character varying[],
  networkmember_ref character varying[],
  fid text,
  filename text,
  descriptiveterm text,
  CONSTRAINT road_pk PRIMARY KEY (ogc_fid ),
  CONSTRAINT enforce_dims_wkb_geometry CHECK (st_ndims(wkb_geometry) = 2),
  CONSTRAINT enforce_srid_wkb_geometry CHECK (st_srid(wkb_geometry) = (-1))
)
WITH (
  OIDS=FALSE
);

CREATE TABLE itn.roadlinkinformation
(
  ogc_fid serial NOT NULL,
  wkb_geometry geometry,
  version integer,
  versiondate text,
  theme text,
  changedate character varying[],
  reasonforchange character varying[],
  descriptivegroup text,
  classification text,
  referencetoroadlink_ref text,
  distancefromstart double precision,
  fid text,
  filename text,
  feet integer,
  inches integer,
  maxheight double precision,
  type text,
  use character varying[],
  instruction text,
  starttime text,
  endtime text,
  CONSTRAINT roadlinkinformation_pk PRIMARY KEY (ogc_fid ),
  CONSTRAINT enforce_dims_wkb_geometry CHECK (st_ndims(wkb_geometry) = 2),
  CONSTRAINT enforce_geotype_wkb_geometry CHECK (geometrytype(wkb_geometry) = 'POINT'::text OR wkb_geometry IS NULL),
  CONSTRAINT enforce_srid_wkb_geometry CHECK (st_srid(wkb_geometry) = 27700)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE itn.roadrouteinformation
(
  ogc_fid serial NOT NULL,
  wkb_geometry geometry,
  version integer,
  versiondate text,
  theme text,
  changedate character varying[],
  reasonforchange character varying[],
  descriptivegroup text,
  classification text,
  directedlink_ref character varying[],
  directedlink_orientation integer[],
  fid text,
  filename text,
  type character varying[],
  instruction text,
  distancefromstart double precision,
  use character varying[],
  day character varying[],
  starttime character varying[],
  endtime character varying[],
  load character varying[],
  namedtime text,
  startdate text,
  enddate text,
  nameddate character varying[],
  CONSTRAINT roadrouteinformation_pk PRIMARY KEY (ogc_fid ),
  CONSTRAINT enforce_dims_wkb_geometry CHECK (st_ndims(wkb_geometry) = 2),
  CONSTRAINT enforce_srid_wkb_geometry CHECK (st_srid(wkb_geometry) = 27700)
)
WITH (
  OIDS=FALSE
);
