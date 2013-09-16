<?xml version="1.0" encoding="UTF-8"?>
<!--

Transformeer BGT levering naar GML featureCollection.

Author:  Just van den Broecke, Just Objects B.V. for PDOK (first)
Author:  Richard Duivenvoorde (improvements, Crotec sample)

Input: BGT LV file
Output: GML FeatureCollection met als featureMember's IMGEO objecten

2 extra bewerkingen nodig:
- uitfilteren xlinks  plaatsbepalingspuntWaterdeel en plaatsbepalingspuntWegdeel
- genereren globaal uniek gml:id uit NEN3610 identifier

-->
<xsl:stylesheet 
    xmlns:imgeo="http://www.geostandaarden.nl/imgeo/2.1"
    xmlns:gml="http://www.opengis.net/gml" 
    xmlns:imgeo-lv="http://www.geostandaarden.nl/imgeo/aanlevering" 
    xmlns:bri="http://www.opengis.net/citygml/bridge/2.0"
    xmlns:bui="http://www.opengis.net/citygml/building/2.0"
    xmlns:cif="http://www.opengis.net/citygml/cityfurniture/2.0"
    xmlns:cit="http://www.opengis.net/citygml/2.0"
    xmlns:lu="http://www.opengis.net/citygml/landuse/2.0"
    xmlns:tra="http://www.opengis.net/citygml/transportation/2.0"
    xmlns:tun="http://www.opengis.net/citygml/tunnel/2.0"
    xmlns:veg="http://www.opengis.net/citygml/vegetation/2.0"
    xmlns:wat="http://www.opengis.net/citygml/waterbody/2.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    version="1.0">

    <xsl:output method="xml" omit-xml-declaration="no" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <!-- Generate SpatialDataset -->
        <gml:FeatureCollection xmlns:imgeo="http://www.geostandaarden.nl/imgeo/2.0-0.99.2" xmlns:imgeo-lv="http://www.geostandaarden.nl/imgeo/aanlevering" xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <!-- Loop through all features. -->
            <xsl:apply-templates/>
        </gml:FeatureCollection>
    </xsl:template>

<!--
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
-->

<!--
   <cit:cityObjectMember>
      <tra:TrafficArea gml:id="ID0c832e60-0977-46da-a28d-f23d69a7935f">
         <cit:creationDate>2013-05-29</cit:creationDate>
         <imgeo:identificatie>
            <imgeo:NEN3610ID>
               <imgeo:namespace>NL.IMGEO</imgeo:namespace>
               <imgeo:lokaalID>00935.0c832e60-0977-46da-a28d-f23d69a7935f</imgeo:lokaalID>
            </imgeo:NEN3610ID>
         </imgeo:identificatie>
         <imgeo:tijdstipRegistratie>2013-05-29T16:05:00</imgeo:tijdstipRegistratie>
         <imgeo:bronhouder>00935</imgeo:bronhouder>
         <imgeo:inOnderzoek>0</imgeo:inOnderzoek>
         <imgeo:relatieveHoogteligging>0</imgeo:relatieveHoogteligging>
         <imgeo:bgt-status codeSpace="http://www.geostandaarden.nl/imgeo/def/2.1#Status">bestaand</imgeo:bgt-status>
         <tra:function codeSpace="http://www.geostandaarden.nl/imgeo/def/2.1#FunctieWeg">inrit</tra:function>
         <tra:surfaceMaterial codeSpace="http://www.geostandaarden.nl/imgeo/def/2.1#FysiekVoorkomenWeg">open verharding</tra:surfaceMaterial>
         <imgeo:plus-fysiekVoorkomenWegdeel codeSpace="http://www.geostandaarden.nl/imgeo/def/2.1#FysiekVoorkomenWegPlus">betonstraatstenen</imgeo:plus-fysiekVoorkomenWegdeel>
         <imgeo:wegdeelOpTalud>0</imgeo:wegdeelOpTalud>
         <imgeo:geometrie2dWegdeel>
            <gml:Polygon>
               <gml:exterior>
                  <gml:LinearRing>
                     <gml:posList>176787.541 316624.601 176785.84 316619.853 176785.011 316620.181 176788.116 316628.149 176790.511 316632.341 176791.079 316632.072 176787.541 316624.601</gml:posList>
                  </gml:LinearRing>
               </gml:exterior>
            </gml:Polygon>
         </imgeo:geometrie2dWegdeel>
      </tra:TrafficArea>
   </cit:cityObjectMember>
-->

    <xsl:template match="tra:AuxiliaryTrafficArea|tra:TrafficArea|veg:PlantCover|imgeo:Waterdeel|imgeo:OnbegroeidTerreindeel|imgeo:OndersteunendWaterdeel|bui:BuildingPart|imgeo:OverigBouwwerk|bri:BridgeConstructionElement|imgeo:Scheiding">
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

    <!-- te negeren items voor nu -->
    <!--<xsl:template match="imgeo:Scheiding|bui:BuildingPart|bri:BridgeConstructionElement|imgeo:OverigBouwwerk|veg:PlantCover|imgeo:Waterdeel|imgeo:OnbegroeidTerreindeel|imgeo:OndersteunendWaterdeel|imgeo:Plaatsbepalingspunt|imgeo:plaatsbepalingspuntWaterdeel|imgeo:plaatsbepalingspuntWegdeel"/>-->
    <xsl:template match="imgeo:Plaatsbepalingspunt"/>

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

    <xsl:template match="imgeo:geometrie2dOndersteunendWaterdeel">
        <imgeo:geometrie2dOndersteunendWaterdeel>
            <xsl:apply-templates/>
        </imgeo:geometrie2dOndersteunendWaterdeel>
    </xsl:template>

    <xsl:template match="imgeo:geometrie2dBegroeidTerreindeel">
        <imgeo:geometrie2dBegroeidTerreindeel>
            <xsl:apply-templates/>
        </imgeo:geometrie2dBegroeidTerreindeel>
    </xsl:template>

    <xsl:template match="imgeo:geometrie2dOnbegroeidTerreindeel">
        <imgeo:geometrie2dOnbegroeidTerreindeel>
            <xsl:apply-templates/>
        </imgeo:geometrie2dOnbegroeidTerreindeel>
    </xsl:template>

    <xsl:template match="imgeo:geometrie2dGrondvlak">
        <imgeo:geometrie2dGrondvlak>
            <xsl:apply-templates/>
        </imgeo:geometrie2dGrondvlak>
    </xsl:template>

    <xsl:template match="imgeo:geometrie2dOverigeConstructie">
        <imgeo:geometrie2dOverigeConstructie>
            <xsl:apply-templates/>
        </imgeo:geometrie2dOverigeConstructie>
    </xsl:template>

    <xsl:template match="imgeo:geometrie2dOverbruggingsdeel">
        <imgeo:geometrie2dOverbruggingsdeel>
            <xsl:apply-templates/>
        </imgeo:geometrie2dOverbruggingsdeel>
    </xsl:template>


    <xsl:template match="imgeo:*">
        <xsl:copy-of select="."/>
    </xsl:template>

    <!-- tra:function needed -->
    <xsl:template match="tra:*">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="wat:class">
        <xsl:copy-of select="."/>
    </xsl:template>

    <xsl:template match="veg:class">
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
