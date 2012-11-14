<?xml version="1.0" encoding="UTF-8"?>
<!--

Transform plain XML cities XML to valid GML.

Author:  Just van den Broecke, Just Objects B.V.
-->
<xsl:stylesheet version="1.0"
                xmlns:ogr="http://ogr.maptools.org/"
                xmlns:gml="http://www.opengis.net/gml"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                 >
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <ogr:FeatureCollection
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:ogr="http://ogr.maptools.org/"
                xmlns:gml="http://www.opengis.net/gml"
                xsi:schemaLocation="http://ogr.maptools.org/ ../gmlcities.xsd  http://www.opengis.net/gml http://schemas.opengis.net/gml/2.1.2/feature.xsd"
                >
            <gml:boundedBy>
              <gml:Box>
                <gml:coord><gml:X>-180.0</gml:X><gml:Y>-90.0</gml:Y></gml:coord>
                <gml:coord><gml:X>180.0</gml:X><gml:Y>90.0</gml:Y></gml:coord>
              </gml:Box>
            </gml:boundedBy>
             <!-- Loop through all cities. -->
            <xsl:apply-templates/>
        </ogr:FeatureCollection>
    </xsl:template>

    <!-- Make each city an ogr:featureMember. -->
    <xsl:template match="city">
        <gml:featureMember>
            <ogr:City>
                <ogr:name>
                    <xsl:value-of select="name"/>
                </ogr:name>
                <ogr:geometry>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG:4326">
                        <gml:coordinates><xsl:value-of select="lat"/>,<xsl:value-of select="lon"/></gml:coordinates>
                     </gml:Point>
                </ogr:geometry>
            </ogr:City>
        </gml:featureMember>
    </xsl:template>
</xsl:stylesheet>
