<?xml version="1.0" encoding="UTF-8"?>

<!--

Transformeer BGT levering naar GML featureCollection.

Author:  Just van den Broecke, Just Objects B.V. for PDOK

Input: BGT LV file
Output: GML FeatureCollection met als featureMember's IMGEO objecten

2 extra bewerkingen nodig:
- uitfilteren xlinks  plaatsbepalingspuntWaterdeel en plaatsbepalingspuntWegdeel
- genereren globaal uniek gml:id uit NEN3610 identifier
-->
<xsl:stylesheet version="1.0"
                xmlns:imgeo="http://www.geostandaarden.nl/imgeo/2.0-0.99.2"
                xmlns:gml="http://www.opengis.net/gml"
                xmlns:imgeo-lv="http://www.geostandaarden.nl/imgeo/aanlevering"

                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <!-- Generate SpatialDataset -->
        <gml:FeatureCollection
                xmlns:imgeo="http://www.geostandaarden.nl/imgeo/2.0-0.99.2"
                xmlns:imgeo-lv="http://www.geostandaarden.nl/imgeo/aanlevering"
                xmlns:gml="http://www.opengis.net/gml"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

            <!-- Loop through all features. -->
            <xsl:apply-templates/>

        </gml:FeatureCollection>
    </xsl:template>

    <xsl:template match="imgeo:Wegdeel|imgeo:Waterdeel">
        <xsl:variable name="elementName">
            <xsl:value-of select="name()"/>
        </xsl:variable>
        <xsl:variable name="namespaceID">
            <xsl:value-of select="imgeo:identificatie/imgeo:NEN3610ID/imgeo:namespace/text()"/>
        </xsl:variable>
        <xsl:variable name="lokaalID">
            <xsl:value-of select="imgeo:identificatie/imgeo:NEN3610ID/imgeo:lokaalID/text()"/>
        </xsl:variable>
        <gml:featureMember>
            <xsl:element name="{$elementName}">
                <xsl:attribute name="gml:id">
                    <xsl:value-of select="concat($namespaceID, '.' ,$lokaalID)"/>
                </xsl:attribute>
                <xsl:apply-templates/>
            </xsl:element>
        </gml:featureMember>
    </xsl:template>

    <xsl:template match="imgeo:plaatsbepalingspuntWaterdeel|imgeo:plaatsbepalingspuntWegdeel"/>

    <xsl:template match="imgeo:geometrie2dWegdeel">
        <imgeo:geometrie2dWegdeel>
            <xsl:apply-templates/>
        </imgeo:geometrie2dWegdeel>
    </xsl:template>

    <xsl:template match="imgeo:geometrie2dWaterdeel">
        <imgeo:geometrie2dWaterdeel>
            <xsl:apply-templates/>
        </imgeo:geometrie2dWaterdeel>
    </xsl:template>

    <xsl:template match="imgeo:*">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="gml:Surface">
         <gml:Surface>
             <xsl:attribute name="srsName">EPSG:28992</xsl:attribute>
             <xsl:attribute name="srsDimension">2</xsl:attribute>
             <xsl:apply-templates/>
         </gml:Surface>
     </xsl:template>

    <xsl:template match="gml:Polygon">
        <gml:Polygon>
            <xsl:attribute name="srsName">EPSG:28992</xsl:attribute>
            <xsl:attribute name="srsDimension">2</xsl:attribute>
            <xsl:apply-templates/>
        </gml:Polygon>
    </xsl:template>

    <xsl:template match="gml:LinearRing">
         <gml:LinearRing>
             <xsl:attribute name="srsName">EPSG:28992</xsl:attribute>
             <xsl:attribute name="srsDimension">2</xsl:attribute>
             <xsl:apply-templates/>
         </gml:LinearRing>
     </xsl:template>
    <xsl:template match="gml:exterior">
         <gml:exterior>
             <xsl:apply-templates/>
         </gml:exterior>
     </xsl:template>
    <xsl:template match="gml:interior">
          <gml:interior>
              <xsl:apply-templates/>
          </gml:interior>
      </xsl:template>

    <xsl:template match="gml:*">
        <xsl:copy-of select="."/>
    </xsl:template>
</xsl:stylesheet>
