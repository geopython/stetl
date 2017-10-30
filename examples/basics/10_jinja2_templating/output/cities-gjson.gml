<?xml version='1.0' encoding='utf-8'?>
<cities:FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:cities="http://cities.maptools.org/"
                       xmlns:gml="http://www.opengis.net/gml"
                       xsi:schemaLocation="http://cities.maptools.org/ ../gmlcities.xsd  http://www.opengis.net/gml http://schemas.opengis.net/gml/2.1.2/feature.xsd">

    <!--
    Generated with a Jinja2 template. The 'globs' variables come from the file globals.json containing global
    variables/structures. The actual/dynamic data (cities) comes from the input CSV file cities.json.
    Also a file with macros templates/macros.tpl.xml is imported, allowing reuse for common structures like INSPIRE id's.
    -->


    <gml:description>
       This example tests GML generation with Jinja2 templating, including the use of Jinja2 globals., such as for this description. Globals provide more or less constant/semi static information like point of contacts, global names, id-prefixes etc.
    </gml:description>



    <!-- Rendered by macro render_name() -->
    <gml:name>
       Test for GML generation via Jinja2 templating
    </gml:name>


    <!-- bbox present in geojson input -->
    <gml:boundedBy>
        <gml:Box>
            <gml:coord>
                <gml:X>4.88</gml:X>
                <gml:Y>41.88</gml:Y>
            </gml:coord>
            <gml:coord>
                <gml:X>12.52</gml:X>
                <gml:Y>53.98</gml:Y>
            </gml:coord>
        </gml:Box>
    </gml:boundedBy>

        <gml:featureMember>
            <cities:City>
                <cities:name>Amsterdam</cities:name>
                <cities:population>779808</cities:population>
                <cities:geometry>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::4258" gml:id="point-1"><gml:pos>52.3730454545455 4.89483636363636</gml:pos></gml:Point>
                </cities:geometry>
            </cities:City>
        </gml:featureMember>
        <gml:featureMember>
            <cities:City>
                <cities:name>Bonn</cities:name>
                <cities:population>327913</cities:population>
                <cities:geometry>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::4258" gml:id="point-2"><gml:pos>50.7345545454545 7.09981818181818</gml:pos></gml:Point>
                </cities:geometry>
            </cities:City>
        </gml:featureMember>
        <gml:featureMember>
            <cities:City>
                <cities:name>Rome</cities:name>
                <cities:population>2753000</cities:population>
                <cities:geometry>
                    <gml:Point srsName="urn:ogc:def:crs:EPSG::4258" gml:id="point-3"><gml:pos>41.88 12.52</gml:pos></gml:Point>
                </cities:geometry>
            </cities:City>
        </gml:featureMember>

</cities:FeatureCollection>