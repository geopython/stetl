<?xml version='1.0' encoding='utf-8'?>
<base:SpatialDataSet xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gml="http://www.opengis.net/gml/3.2" xsi:schemaLocation="urn:x-inspire:specification:gmlas:BaseTypes:3.2 http://inspire.ec.europa.eu/schemas/base/3.2/BaseTypes.xsd urn:x-inspire:specification:gmlas:Addresses:3.0 http://inspire.ec.europa.eu/schemas/ad/3.0/Addresses.xsd urn:x-inspire:specification:gmlas:GeographicalNames:3.0 http://inspire.ec.europa.eu/schemas/gn/3.0/GeographicalNames.xsd" gml:id="NL.KAD.BAG.AD">
  <base:identifier>
    <base:Identifier>
      <base:localId>0</base:localId>
      <base:namespace>NL.KAD.BAG.AD</base:namespace>
    </base:Identifier>
  </base:identifier>
  <base:metadata xsi:nil="true"/>
  <base:member>
    <AD:Address xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.Address.362200000022695">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362200000022695</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>362200000022695</base:localId>
          <base:namespace>NL.KAD.BAG.AD.Address</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:position>
        <AD:GeographicPosition>
          <AD:geometry>
            <gml:Point gml:id="NL.KAD.BAG.AD.Address.362200000022695_P" srsName="urn:ogc:def:crs:EPSG::4258">
              <gml:pos>52.299493602339524 4.867708706943735</gml:pos>
            </gml:Point>
          </AD:geometry>
          <AD:specification>entrance</AD:specification>
          <AD:method>byOtherParty</AD:method>
          <AD:default>true</AD:default>
        </AD:GeographicPosition>
      </AD:position>
      <AD:locator>
        <AD:AddressLocator>
          <AD:designator>
            <AD:LocatorDesignator>
              <AD:designator>1025</AD:designator>
              <AD:type>2</AD:type>
            </AD:LocatorDesignator>
          </AD:designator>
          <AD:level>unitLevel</AD:level>
        </AD:AddressLocator>
      </AD:locator>
      <AD:validFrom>2010-08-17T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000030694"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181WP"/>
    </AD:Address>
  </base:member>
  <base:member>
    <AD:AddressAreaName xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.AddressAreaName.1050">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.AddressAreaName.1050</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>1050</base:localId>
          <base:namespace>NL.KAD.BAG.AD.AddressAreaName</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:validFrom>2007-05-30T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:name>
        <GN:GeographicalName>
          <GN:language xsi:nil="true"/>
          <GN:nativeness codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NativenessValue.xml">endonym</GN:nativeness>
          <GN:nameStatus codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NameStatusValue.xml">official</GN:nameStatus>
          <GN:sourceOfName>Het Kadaster</GN:sourceOfName>
          <GN:pronunciation xsi:nil="true" nilReason="other:unpopulated"/>
          <GN:spelling>
            <GN:SpellingOfName>
              <GN:text>Amstelveen</GN:text>
              <GN:script>Latn</GN:script>
            </GN:SpellingOfName>
          </GN:spelling>
          <GN:grammaticalGender xsi:nil="true"/>
          <GN:grammaticalNumber xsi:nil="true"/>
        </GN:GeographicalName>
      </AD:name>
      <AD:namedPlace xsi:nil="true" nilReason="other:unpopulated"/>
    </AD:AddressAreaName>
  </base:member>
  <base:member>
    <AD:PostalDescriptor xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.PostalDescriptor.1181WP">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.PostalDescriptor.1181WP</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>1181WP</base:localId>
          <base:namespace>NL.KAD.BAG.AD.PostalDescriptor</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:validFrom xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:postCode>1181WP</AD:postCode>
    </AD:PostalDescriptor>
  </base:member>
  <base:member>
    <AD:ThoroughfareName xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.ThoroughfareName.362300000030694">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.ThoroughfareName.362300000030694</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>362300000030694</base:localId>
          <base:namespace>NL.KAD.BAG.AD.ThoroughfareName</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:validFrom>1957-04-29T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:name>
        <GN:GeographicalName>
          <GN:language xsi:nil="true"/>
          <GN:nativeness codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NativenessValue.xml">endonym</GN:nativeness>
          <GN:nameStatus codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NameStatusValue.xml">official</GN:nameStatus>
          <GN:sourceOfName>Het Kadaster</GN:sourceOfName>
          <GN:pronunciation xsi:nil="true" nilReason="other:unpopulated"/>
          <GN:spelling>
            <GN:SpellingOfName>
              <GN:text>Meander</GN:text>
              <GN:script>Latn</GN:script>
            </GN:SpellingOfName>
          </GN:spelling>
          <GN:grammaticalGender xsi:nil="true"/>
          <GN:grammaticalNumber xsi:nil="true"/>
        </GN:GeographicalName>
      </AD:name>
    </AD:ThoroughfareName>
  </base:member>
  <base:member>
    <AD:Address xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.Address.362200000022696">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362200000022696</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>362200000022696</base:localId>
          <base:namespace>NL.KAD.BAG.AD.Address</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:position>
        <AD:GeographicPosition>
          <AD:geometry>
            <gml:Point gml:id="NL.KAD.BAG.AD.Address.362200000022696_P" srsName="urn:ogc:def:crs:EPSG::4258">
              <gml:pos>52.299493602339524 4.867708706943735</gml:pos>
            </gml:Point>
          </AD:geometry>
          <AD:specification>entrance</AD:specification>
          <AD:method>byOtherParty</AD:method>
          <AD:default>true</AD:default>
        </AD:GeographicPosition>
      </AD:position>
      <AD:locator>
        <AD:AddressLocator>
          <AD:designator>
            <AD:LocatorDesignator>
              <AD:designator>1027</AD:designator>
              <AD:type>2</AD:type>
            </AD:LocatorDesignator>
          </AD:designator>
          <AD:level>unitLevel</AD:level>
        </AD:AddressLocator>
      </AD:locator>
      <AD:validFrom>2010-08-17T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000030694"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181WP"/>
    </AD:Address>
  </base:member>
  <base:member>
    <AD:Address xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.Address.362200000022700">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362200000022700</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>362200000022700</base:localId>
          <base:namespace>NL.KAD.BAG.AD.Address</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:position>
        <AD:GeographicPosition>
          <AD:geometry>
            <gml:Point gml:id="NL.KAD.BAG.AD.Address.362200000022700_P" srsName="urn:ogc:def:crs:EPSG::4258">
              <gml:pos>52.299493602339524 4.867708706943735</gml:pos>
            </gml:Point>
          </AD:geometry>
          <AD:specification>entrance</AD:specification>
          <AD:method>byOtherParty</AD:method>
          <AD:default>true</AD:default>
        </AD:GeographicPosition>
      </AD:position>
      <AD:locator>
        <AD:AddressLocator>
          <AD:designator>
            <AD:LocatorDesignator>
              <AD:designator>1035</AD:designator>
              <AD:type>2</AD:type>
            </AD:LocatorDesignator>
          </AD:designator>
          <AD:level>unitLevel</AD:level>
        </AD:AddressLocator>
      </AD:locator>
      <AD:validFrom>2010-08-17T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000030694"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181WP"/>
    </AD:Address>
  </base:member>
  <base:member>
    <AD:Address xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.Address.362200000022701">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362200000022701</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>362200000022701</base:localId>
          <base:namespace>NL.KAD.BAG.AD.Address</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:position>
        <AD:GeographicPosition>
          <AD:geometry>
            <gml:Point gml:id="NL.KAD.BAG.AD.Address.362200000022701_P" srsName="urn:ogc:def:crs:EPSG::4258">
              <gml:pos>52.299493602339524 4.867708706943735</gml:pos>
            </gml:Point>
          </AD:geometry>
          <AD:specification>entrance</AD:specification>
          <AD:method>byOtherParty</AD:method>
          <AD:default>true</AD:default>
        </AD:GeographicPosition>
      </AD:position>
      <AD:locator>
        <AD:AddressLocator>
          <AD:designator>
            <AD:LocatorDesignator>
              <AD:designator>1037</AD:designator>
              <AD:type>2</AD:type>
            </AD:LocatorDesignator>
          </AD:designator>
          <AD:level>unitLevel</AD:level>
        </AD:AddressLocator>
      </AD:locator>
      <AD:validFrom>2010-08-17T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000030694"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181WP"/>
    </AD:Address>
  </base:member>
  <base:member>
    <AD:Address xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://ogr.maptools.org/" xmlns:wfs="http://www.opengis.net/wfs" gml:id="NL.KAD.BAG.AD.Address.362200000022706">
      <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362200000022706</gml:identifier>
      <AD:inspireId>
        <base:Identifier>
          <base:localId>362200000022706</base:localId>
          <base:namespace>NL.KAD.BAG.AD.Address</base:namespace>
        </base:Identifier>
      </AD:inspireId>
      <AD:position>
        <AD:GeographicPosition>
          <AD:geometry>
            <gml:Point gml:id="NL.KAD.BAG.AD.Address.362200000022706_P" srsName="urn:ogc:def:crs:EPSG::4258">
              <gml:pos>52.299493602339524 4.867708706943735</gml:pos>
            </gml:Point>
          </AD:geometry>
          <AD:specification>entrance</AD:specification>
          <AD:method>byOtherParty</AD:method>
          <AD:default>true</AD:default>
        </AD:GeographicPosition>
      </AD:position>
      <AD:locator>
        <AD:AddressLocator>
          <AD:designator>
            <AD:LocatorDesignator>
              <AD:designator>1049</AD:designator>
              <AD:type>2</AD:type>
            </AD:LocatorDesignator>
          </AD:designator>
          <AD:level>unitLevel</AD:level>
        </AD:AddressLocator>
      </AD:locator>
      <AD:validFrom>2010-08-17T00:00:00</AD:validFrom>
      <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000030694"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
      <AD:component xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181WP"/>
    </AD:Address>
  </base:member>
</base:SpatialDataSet>
