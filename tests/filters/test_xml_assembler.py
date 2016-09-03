import os

from stetl.etl import ETL
from stetl.filters.xmlassembler import XmlAssembler
from stetl.filters.packetbuffer import PacketBuffer
from tests.stetl_test_case import StetlTestCase

class XmlAssemblerTest(StetlTestCase):
    """Unit tests for XmlAssembler"""

    def setUp(self):
        super(XmlAssemblerTest, self).setUp()

        # Initialize Stetl
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(curr_dir, 'configs/xmlassembler.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')
        
        self.assertEqual('filters.xmlassembler.XmlAssembler', class_name)
    
    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.get_by_index(1), XmlAssembler))
        
    def test_execute(self):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        buffer_filter = chain.get_by_class(PacketBuffer)
        packet_list = buffer_filter.packet_list

        # most Packets are empty, but we need to find 2 filled with etree docs
        doc_packet_list = []
        for packet in packet_list:
            if packet.data is not None:
                doc_packet_list.append(packet)

        # Assertion: we need to see 2 documents
        self.assertEqual(len(doc_packet_list), 4)
        namespaces={'gml': 'http://www.opengis.net/gml/3.2', 'top10nl': 'http://register.geostandaarden.nl/gmlapplicatieschema/top10nl/1.2.0'}

        # Assertion: first doc has two FeatureMember elements with proper Namespaces
        xml_doc1 = doc_packet_list[0].data
        feature_elms = xml_doc1.xpath('/gml:FeatureCollectionT10NL/top10nl:FeatureMember', namespaces=namespaces)
        self.assertEqual(len(feature_elms), 2)

        # Assertion: last doc has one FeatureMember with proper Namespaces
        last = len(doc_packet_list) - 1
        xml_doc2 = doc_packet_list[last].data
        feature_elms = xml_doc2.xpath('/gml:FeatureCollectionT10NL/top10nl:FeatureMember', namespaces=namespaces)
        self.assertEqual(len(feature_elms), 1)

        # Assertion: first doc has end_of_doc but not end_of_stream set
        self.assertTrue(doc_packet_list[0].end_of_doc, msg='doc1: end_of_doc if False')
        self.assertFalse(doc_packet_list[0].end_of_stream, msg='doc1: end_of_stream is True')

        # Assertion: last doc has end_of_doc and end_of_stream set
        self.assertTrue(doc_packet_list[last].end_of_doc, msg='doc2: end_of_doc if False')
        self.assertTrue(doc_packet_list[last].end_of_stream, msg='doc2: end_of_stream if False')
