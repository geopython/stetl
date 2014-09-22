<?xml version="1.0" encoding="UTF-8"?>


<base:SpatialDataSet xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2"
                     xmlns:AD="urn:x-inspire:specification:gmlas:Addresses:3.0"
                     xmlns:GN="urn:x-inspire:specification:gmlas:GeographicalNames:3.0"
                     xmlns:gmd="http://www.isotc211.org/2005/gmd"
                     xmlns:xlink="http://www.w3.org/1999/xlink"
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                     xmlns:gml="http://www.opengis.net/gml/3.2"
                     xsi:schemaLocation="urn:x-inspire:specification:gmlas:BaseTypes:3.2 http://inspire.ec.europa.eu/schemas/base/3.2/BaseTypes.xsd
                            urn:x-inspire:specification:gmlas:Addresses:3.0 http://inspire.ec.europa.eu/schemas/ad/3.0/Addresses.xsd
                                urn:x-inspire:specification:gmlas:GeographicalNames:3.0 http://inspire.ec.europa.eu/schemas/gn/3.0/GeographicalNames.xsd"
                     gml:id="NL.KAD.BAG.AD">
    <base:identifier>
        <base:Identifier>
            <base:localId>0</base:localId>
            <base:namespace>NL.KAD.BAG.AD</base:namespace>
        </base:Identifier>
    </base:identifier>
    <base:metadata xsi:nil="true"/>

    <base:member>
        <AD:Address gml:id="NL.KAD.BAG.AD.Address.362010002013564">
            <gml:identifier
                    codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362010002013564</gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>362010002013564</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:position>
                <AD:GeographicPosition>
                    <AD:geometry>
                        <gml:Point gml:id="NL.KAD.BAG.AD.Address.362010002013564_P"
                                   srsName="urn:ogc:def:crs:EPSG::4258">
                            <gml:pos>52.31217 4.85291</gml:pos>
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
                            <AD:designator>3</AD:designator>
                            <AD:type>2</AD:type>
                        </AD:LocatorDesignator>
                    </AD:designator>
                    <AD:level>unitLevel</AD:level>
                </AD:AddressLocator>
            </AD:locator>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>

            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <!-- Inline reference to address components: street (ThoroughfareName_, city (AddressAreaName)
            and postal code (PostalDescriptor)  -->
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000018600"/>
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181PL"/>
        </AD:Address>
    </base:member>

    <base:member>
        <AD:ThoroughfareName gml:id="NL.KAD.BAG.AD.ThoroughfareName.362300000018600">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.ThoroughfareName.362300000018600
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>362300000018600</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:name>
                <AD:ThoroughfareNameValue>
                    <AD:name>
                        <GN:GeographicalName>
                                     <GN:language xsi:nil="true"/>
                                     <GN:nativeness codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NativenessValue.xml">endonym</GN:nativeness>
                                     <GN:nameStatus codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NameStatusValue.xml">official</GN:nameStatus>
                                     <GN:sourceOfName>Het Kadaster</GN:sourceOfName>
                                     <GN:pronunciation xsi:nil="true" nilReason="other:unpopulated"/>
                                     <GN:spelling>
                                         <GN:SpellingOfName>
                                             <GN:text>Van der Hoochlaan</GN:text>
                                             <GN:script>Latn</GN:script>
                                         </GN:SpellingOfName>
                                     </GN:spelling>
                                     <GN:grammaticalGender xsi:nil="true"/>
                                     <GN:grammaticalNumber xsi:nil="true"/>
                                 </GN:GeographicalName>
                    </AD:name>
                </AD:ThoroughfareNameValue>
            </AD:name>
        </AD:ThoroughfareName>
    </base:member>
    <base:member>
        <AD:AddressAreaName gml:id="NL.KAD.BAG.AD.AddressAreaName.1050">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.AddressAreaName.1050
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>1050</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
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
        <AD:PostalDescriptor gml:id="NL.KAD.BAG.AD.PostalDescriptor.1181PL">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.PostalDescriptor.1181PL
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>1181PL</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
           </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:postCode>1181PL</AD:postCode>
        </AD:PostalDescriptor>
    </base:member>
    <base:member>
        <AD:Address gml:id="NL.KAD.BAG.AD.Address.362010002038696">
            <gml:identifier
                    codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.362010002038696</gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>362010002038696</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:position>
                <AD:GeographicPosition>
                    <AD:geometry>
                        <gml:Point gml:id="NL.KAD.BAG.AD.Address.362010002038696_P"
                                   srsName="urn:ogc:def:crs:EPSG::4258">
                            <gml:pos>52.30955 4.85947</gml:pos>
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
                            <AD:designator>26</AD:designator>
                            <AD:type>2</AD:type>
                        </AD:LocatorDesignator>
                    </AD:designator>
                    <AD:level>unitLevel</AD:level>
                </AD:AddressLocator>
            </AD:locator>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>

            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <!-- Inline reference to address components: street (ThoroughfareName_, city (AddressAreaName)
            and postal code (PostalDescriptor)  -->
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.362300000054003"/>
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.AddressAreaName.1050"/>
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1181PV"/>
        </AD:Address>
    </base:member>

    <base:member>
        <AD:ThoroughfareName gml:id="NL.KAD.BAG.AD.ThoroughfareName.362300000054003">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.ThoroughfareName.362300000054003
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>362300000054003</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:name>
                <AD:ThoroughfareNameValue>
                    <AD:name>
                        <GN:GeographicalName>
                                     <GN:language xsi:nil="true"/>
                                     <GN:nativeness codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NativenessValue.xml">endonym</GN:nativeness>
                                     <GN:nameStatus codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NameStatusValue.xml">official</GN:nameStatus>
                                     <GN:sourceOfName>Het Kadaster</GN:sourceOfName>
                                     <GN:pronunciation xsi:nil="true" nilReason="other:unpopulated"/>
                                     <GN:spelling>
                                         <GN:SpellingOfName>
                                             <GN:text>Van IJsselsteinlaan</GN:text>
                                             <GN:script>Latn</GN:script>
                                         </GN:SpellingOfName>
                                     </GN:spelling>
                                     <GN:grammaticalGender xsi:nil="true"/>
                                     <GN:grammaticalNumber xsi:nil="true"/>
                                 </GN:GeographicalName>
                    </AD:name>
                </AD:ThoroughfareNameValue>
            </AD:name>
        </AD:ThoroughfareName>
    </base:member>

    <base:member>
        <AD:PostalDescriptor gml:id="NL.KAD.BAG.AD.PostalDescriptor.1181PV">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.PostalDescriptor.1181PV
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>1181PV</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
           </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:postCode>1181PV</AD:postCode>
        </AD:PostalDescriptor>
    </base:member>
    <base:member>
        <AD:Address gml:id="NL.KAD.BAG.AD.Address.363010000596724">
            <gml:identifier
                    codeSpace="http://inspire.jrc.ec.europa.eu/">urn:x-inspire:object:id:NL.KAD.BAG.AD.Address.363010000596724</gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>363010000596724</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:position>
                <AD:GeographicPosition>
                    <AD:geometry>
                        <gml:Point gml:id="NL.KAD.BAG.AD.Address.363010000596724_P"
                                   srsName="urn:ogc:def:crs:EPSG::4258">
                            <gml:pos>47.993188 4.937363</gml:pos>
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
                            <AD:designator>6</AD:designator>
                            <AD:type>2</AD:type>
                        </AD:LocatorDesignator>
                    </AD:designator>
                        <!-- Optional House Number Addition, e.g. Floornumber "Huisnummertoevoeging" in The Netherlands -->
                        <AD:designator>
                            <AD:LocatorDesignator>
                                <AD:designator>3</AD:designator>
                                <AD:type>4</AD:type>
                            </AD:LocatorDesignator>
                        </AD:designator>
                    <AD:level>unitLevel</AD:level>
                </AD:AddressLocator>
            </AD:locator>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>

            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <!-- Inline reference to address components: street (ThoroughfareName_, city (AddressAreaName)
            and postal code (PostalDescriptor)  -->
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.ThoroughfareName.363300000003032"/>
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.AddressAreaName.3594"/>
            <AD:component xmlns:xlink="http://www.w3.org/1999/xlink"
                       xlink:href="#NL.KAD.BAG.AD.PostalDescriptor.1013GW"/>
        </AD:Address>
    </base:member>

    <base:member>
        <AD:ThoroughfareName gml:id="NL.KAD.BAG.AD.ThoroughfareName.363300000003032">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.ThoroughfareName.363300000003032
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>363300000003032</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:name>
                <AD:ThoroughfareNameValue>
                    <AD:name>
                        <GN:GeographicalName>
                                     <GN:language xsi:nil="true"/>
                                     <GN:nativeness codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NativenessValue.xml">endonym</GN:nativeness>
                                     <GN:nameStatus codeSpace="http://schemas.kademo.nl/inspire/codelist-1004/NameStatusValue.xml">official</GN:nameStatus>
                                     <GN:sourceOfName>Het Kadaster</GN:sourceOfName>
                                     <GN:pronunciation xsi:nil="true" nilReason="other:unpopulated"/>
                                     <GN:spelling>
                                         <GN:SpellingOfName>
                                             <GN:text>Brouwersgracht</GN:text>
                                             <GN:script>Latn</GN:script>
                                         </GN:SpellingOfName>
                                     </GN:spelling>
                                     <GN:grammaticalGender xsi:nil="true"/>
                                     <GN:grammaticalNumber xsi:nil="true"/>
                                 </GN:GeographicalName>
                    </AD:name>
                </AD:ThoroughfareNameValue>
            </AD:name>
        </AD:ThoroughfareName>
    </base:member>
    <base:member>
        <AD:AddressAreaName gml:id="NL.KAD.BAG.AD.AddressAreaName.3594">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.AddressAreaName.3594
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>3594</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
            </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
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
                                             <GN:text>Amsterdam</GN:text>
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
        <AD:PostalDescriptor gml:id="NL.KAD.BAG.AD.PostalDescriptor.1013GW">
            <gml:identifier codeSpace="http://inspire.jrc.ec.europa.eu/">
                urn:x-inspire:object:id:NL.KAD.BAG.AD.PostalDescriptor.1013GW
            </gml:identifier>
            <AD:inspireId>
                <!-- Rendered by macro render_inspire_id() -->
                            <base:Identifier>
                                 <base:localId>1013GW</base:localId>
                                 <base:namespace>NL.KAD.BAG.AD</base:namespace>
                             </base:Identifier>
           </AD:inspireId>
            <AD:beginLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:endLifespanVersion xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:validFrom>2014-09-17T00:00:00Z</AD:validFrom>
            <AD:validTo xsi:nil="true" nilReason="other:unpopulated"/>
            <AD:postCode>1013GW</AD:postCode>
        </AD:PostalDescriptor>
    </base:member>

</base:SpatialDataSet>