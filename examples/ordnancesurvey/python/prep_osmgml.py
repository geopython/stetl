#!/usr/bin/python

## Copyright (c) 2011 Astun Technology

## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

"""
A collection of classes used to manipulate Ordnance Survey GB GML data,
used with prepgml4ogr.py. (But here used/called from Stetl Filter)
"""

import os
from lxml import etree


class prep_osgml():
    """
    Base class that provides the main interface methods `prepare_feature` and
    `get_feat_types` and performs basic manipulation such as exposing the fid,
    adding and element containing the filename of the source and adding an
    element with the orientation in degrees.

    """
    def __init__(self, inputfile):
        self.inputfile = inputfile
        self.feat_types = []

    def get_feat_types(self):
        return self.feat_types

    def prepare_feature(self, feat_str):

        # Parse the xml string into something useful
        feat_elm = etree.fromstring(feat_str)
        feat_elm = self._prepare_feat_elm(feat_elm)

        return etree.tostring(feat_elm,
                              encoding='UTF-8',
                              pretty_print=True).decode('utf_8')

    def _prepare_feat_elm(self, feat_elm):

        feat_elm = self._add_fid_elm(feat_elm)
        feat_elm = self._add_filename_elm(feat_elm)
        feat_elm = self._add_orientation_degree_elms(feat_elm)

        return feat_elm

    def _add_fid_elm(self, feat_elm):

        # Create an element with the fid
        elm = etree.SubElement(feat_elm, "fid")
        elm.text = feat_elm.get('fid')

        return feat_elm

    def _add_filename_elm(self, feat_elm):

        # Create an element with the filename
        elm = etree.SubElement(feat_elm, "filename")
        elm.text = os.path.basename(self.inputfile)

        return feat_elm

    def _add_orientation_degree_elms(self, feat_elm):

        # Correct any orientation values to be a
        # tenth of their original value
        orientation_elms = feat_elm.xpath('//orientation')
        for elm in orientation_elms:
            # Add a new orientDeg element as a child to the
            # the orientation elm to be orientation/10
            # (this applies integer division which is fine in
            # this instance as we are not concerned with the decimals)
            degree_elm = etree.SubElement(elm.getparent(), "orientDeg")
            degree_elm.text = str(int(elm.text) / 10)

        return feat_elm


class prep_vml(prep_osgml):
    """
    Preperation class for OS VectorMap Local features.

    """
    def __init__(self, inputfile):
        prep_osgml.__init__(self, inputfile)
        self.feat_types = [
            'Text',
            'VectorMapPoint',
            'Line',
            'RoadCLine',
            'Area'
        ]


class prep_osmm_topo(prep_osgml):
    """
    Preperation class for OS MasterMap features which in addition to the work
    performed by `prep_osgml` adds `themes`, `descriptiveGroups` and
    `descriptiveTerms` elements containing a delimited string of the attributes
    that can appear multiple times.

    """
    def __init__(self, inputfile):
        prep_osgml.__init__(self, inputfile)
        self.feat_types = [
            'BoundaryLine',
            'CartographicSymbol',
            'CartographicText',
            'TopographicArea',
            'TopographicLine',
            'TopographicPoint'
        ]
        self.list_seperator = ', '

    def _prepare_feat_elm(self, feat_elm):

        feat_elm = prep_osgml._prepare_feat_elm(self, feat_elm)
        feat_elm = self._add_lists_elms(feat_elm)

        return feat_elm

    def _add_lists_elms(self, feat_elm):

        feat_elm = self._create_list_of_terms(feat_elm, 'theme')
        feat_elm = self._create_list_of_terms(feat_elm, 'descriptiveGroup')
        feat_elm = self._create_list_of_terms(feat_elm, 'descriptiveTerm')

        return feat_elm

    def _create_list_of_terms(self, feat_elm, name):
        text_list = feat_elm.xpath('//%s/text()' % name)
        if len(text_list):
            elm = etree.SubElement(feat_elm, "%ss" % name)
            elm.text = self.list_seperator.join(text_list)
        return feat_elm


class prep_osmm_topo_qgis(prep_osmm_topo):
    """
    Preperation class for OS MasterMap features which in addition to the work performed by
    `prep_osmm_topo` adds QGIS specific label attributes such as `qFont` and `aAnchorPos`.

    """

    def __init__(self, filename):
        prep_osmm_topo.__init__(self, filename)

        # AC - define the font
        if os.name is 'posix':
            # Will probably need different font names
            self.fonts = ('Garamond', 'Arial', 'Roman', 'ScriptC')
        elif os.name is 'nt':
            # Ordnance Survey use
            #   'Lutheran', 'Normal', 'Light Roman', 'Suppressed text'
            self.fonts = ('GothicE', 'Monospac821 BT', 'Consolas', 'ScriptC', 'Arial Narrow')
        elif os.name is 'mac':
            # Will probably need different font name
            self.fonts = ('Garamond', 'Arial', 'Roman', 'ScriptC')

        # AC - the possible text placement positions used by QGIS
        self.anchorPosition = ('Bottom Left', 'Left', 'Top Left', 'Bottom',
                                'Over', 'Top',  'Bottom Right', 'Right', 'Top Right')

    def _prepare_feat_elm(self, feat_elm):

        feat_elm = prep_osmm_topo._prepare_feat_elm(self, feat_elm)
        feat_elm = self._add_qgis_elms(feat_elm)

        return feat_elm

    def _add_qgis_elms(self, feat_elm):

        if feat_elm.tag == 'CartographicText':
            text_render_elm = feat_elm.xpath('//textRendering')[0]

            anchor_pos = int(text_render_elm.xpath('./anchorPosition/text()')[0])
            try:
                anchor_pos = self.anchorPosition[anchor_pos]
            except:
                anchor_pos = 4
            elm = etree.SubElement(text_render_elm, 'qAnchorPos')
            elm.text = anchor_pos

            font = int(text_render_elm.xpath('./font/text()')[0])
            try:
                font = self.fonts[font]
            except:
                font = 'unknown font (%s)' % str(font)
            elm = etree.SubElement(text_render_elm, 'qFont')
            elm.text = font

        return feat_elm


class prep_osmm_itn(prep_osgml):
    """
    Preperation class for OS MasterMap ITN features.

    """

    def __init__(self, filename):

        prep_osgml.__init__(self, filename)

        self.feat_types = [
            'FerryLink',
            'FerryNode',
            'InformationPoint',
            'Road',
            'RoadNode',
            'RoadNodeInformation',
            'RoadLink',
            'RoadLinkInformation',
            'RoadRouteInformation'
        ]

    def _prepare_feat_elm(self, feat_elm):

        feat_elm = prep_osgml._prepare_feat_elm(self, feat_elm)
        feat_elm = self._expose_links(feat_elm)

        return feat_elm

    def _expose_links(self, feat_elm):

        link_list = feat_elm.xpath('//networkMember | //directedLink | //directedNode | //referenceToRoadLink | //referenceToRoadNode | //referenceToTopographicArea')
        for elm in link_list:
            for name in elm.attrib:
                value = elm.get(name)
                if name == 'href':
                    name = '%s_%s' % (elm.tag, 'ref')
                    value = value[1:]
                elif name == 'orientation':
                    name = '%s_%s' % (elm.tag, name)
                    value = '1' if value == '+' else '0'
                sub_elm = etree.SubElement(elm, name)
                sub_elm.text = value

        return feat_elm


class prep_addressbase():
    """
    Simple preperation of AddressBase data

    """
    def __init__(self, inputfile):
        self.inputfile = inputfile
        self.feat_types = ['Address']

    def get_feat_types(self):
        return self.feat_types

    def prepare_feature(self, feat_str):

        # Parse the xml string into something useful
        feat_elm = etree.fromstring(feat_str)
        feat_elm = self._prepare_feat_elm(feat_elm)

        return etree.tostring(feat_elm,
                              encoding='UTF-8',
                              pretty_print=True).decode('utf_8')

    def _prepare_feat_elm(self, feat_elm):

        feat_elm = self._drop_gmlid(feat_elm)

        return feat_elm

    def _drop_gmlid(self, feat_elm):

        feat_elm.attrib.pop('id')

        return feat_elm
