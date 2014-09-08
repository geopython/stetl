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
    

    <!-- Rendered by macro render_bounded_by() -->
    <gml:boundedBy>
        <gml:Box>
            <gml:coord>
                <gml:X>4.9</gml:X>
                <gml:Y>41.9</gml:Y>
            </gml:coord>
            <gml:coord>
                <gml:X>12.5</gml:X>
                <gml:Y>52.4</gml:Y>
            </gml:coord>
        </gml:Box>
    </gml:boundedBy>

        <gml:featureMember>
            <cities:City>
                <cities:name>Amsterdam</cities:name>
                <cities:geometry>
                    <gml:Point srsName="EPSG:4326">
                        <gml:coordinates>4.9, 52.4</gml:coordinates>
                    </gml:Point>
                </cities:geometry>
            </cities:City>
        </gml:featureMember>
        <gml:featureMember>
            <cities:City>
                <cities:name>Bonn</cities:name>
                <cities:geometry>
                    <gml:Point srsName="EPSG:4326">
                        <gml:coordinates>7.1, 50.7</gml:coordinates>
                    </gml:Point>
                </cities:geometry>
            </cities:City>
        </gml:featureMember>
        <gml:featureMember>
            <cities:City>
                <cities:name>Rome</cities:name>
                <cities:geometry>
                    <gml:Point srsName="EPSG:4326">
                        <gml:coordinates>12.5, 41.9</gml:coordinates>
                    </gml:Point>
                </cities:geometry>
            </cities:City>
        </gml:featureMember>

</cities:FeatureCollection>