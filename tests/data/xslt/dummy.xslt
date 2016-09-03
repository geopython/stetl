<?xml version="1.0" encoding="UTF-8"?>

<!--
Voorbewerking Top10NL GML Objecten

Auteur: Just van den Broecke

Aangepast voor Top10NL versie 1.1.1 en 1.2 door Frank Steggink

Dit XSLT script doet een voorbewerking op de ruwe Top10NL GML zoals door Het Kadaster
geleverd. Dit is nodig omdat GDAL ogr2ogr niet alle mogelijkheden van GML goed aankan
en omdat met ingang van versie 1.2 de plaats van de geometrie in een feature is gewijzigd.

Voornamelijk gaat het om meerdere geometrie-attributen per Top10 Object. Het interne
GDAL model kent maar 1 geometrie per feature. Daarnaast is het bij visualiseren bijv.
met SLDs voor een WMS vaak het handigst om 1 geometrie per laag te hebben. Dit geldt ook
als we bijvoorbeeld een OGR conversie naar ESRI Shapefile willen doen met ogr2ogr.

Dit script splitst objecten uit Top10NL uit in geometrie-specifieke objecten.
Bijvoorbeeld een weg (objecttype Wegdeel) heeft twee geometrie-attributen. Het attribuut
hoofdGeometrie kan weer een vlak, lijn of punt bevatten en het attribuut hartGeometrie kan
een lijn of punt bevatten. Na uitsplitsen ontstaan max. 5 verschillende objecttypen, namelijk
Wegdeel_Vlak, Wegdeel_Lijn, Wegdeel_hartLijn etc. Ieder van deze objecten bevat slechts een
geometrie.

-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xalan="http://xml.apache.org/xalan" exclude-result-prefixes="xalan"
                xmlns:top10nl="http://register.geostandaarden.nl/gmlapplicatieschema/top10nl/1.2.0"
                xmlns:brt="http://register.geostandaarden.nl/gmlapplicatieschema/brt-algemeen/1.2.0"
                xmlns:gml="http://www.opengis.net/gml/3.2"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:smil20="http://www.w3.org/2001/SMIL20/"
                xmlns:smil20lang="http://www.w3.org/2001/SMIL20/Language">
    <xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <!-- Start: output omhullende FeatureCollection -->
    <xsl:template match="/">
        <dummy>
            <xsl:apply-templates/>
        </dummy>
    </xsl:template>

    <xsl:template match="top10nl:FeatureMember">
        <xsl:for-each select="top10nl:FunctioneelGebied">
            <funcgeb>
                <xsl:attribute name="id">
                    <xsl:value-of select="@gml:id"/>
                </xsl:attribute>
            </funcgeb>
        </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>
