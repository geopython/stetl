# -*- coding: utf-8 -*-
#
# Reads an XML file and returns XML elements.
# Based on inputs.fileinput.XmlElementStreamFileInput.
#
# Author: Frank Steggink
#
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util, etree
from stetl.packet import FORMAT

log = Util.get_log('xmlelementreader')


class XmlElementReader(Filter):
    """
    Extracts XML elements from a file, outputs each feature element in Packet.
    Parsing is streaming (no internal DOM buildup) so any file size can be handled.
    Use this class for your big GML files!

    consumes=FORMAT.string, produces=FORMAT.etree_element
    """

    # Start attribute config meta
    @Config(ptype=list, default=None, required=True)
    def element_tags(self):
        """
        Comma-separated string of XML (feature) element tag names of the elements that should be extracted
        and added to the output element stream.

        Required: True

        Default: None
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def strip_namespaces(self):
        """
        should namespaces be removed from the input document and thus not be present in the output element stream?

        Required: False

        Default: False
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.etree_element)
        self.context = None
        self.root = None
        self.cur_file_path = None
        self.elem_count = 0
        log.info("Element tags to be matched: %s" % self.element_tags)

    def invoke(self, packet):
        if packet.data is None:
            log.info("No XML file given")
            return packet

        if self.cur_file_path is None:
            self.cur_file_path = packet.data

        event = None
        packet.data = None
        
        if self.context is None:
            # Open file
            fd = open(self.cur_file_path)
            self.elem_count = 0
            log.info("file opened : %s" % self.cur_file_path)
            self.context = etree.iterparse(fd, events=("start", "end"))
            self.context = iter(self.context)
            event, self.root = self.context.next()

        packet = self.process_xml(packet)

        return packet

    def process_xml(self, packet):
        while not self.context is None:
            #while not packet.is_end_of_doc():
            try:
                event, elem = self.context.next()
            except (etree.XMLSyntaxError, StopIteration):
                # workaround for etree.XMLSyntaxError https://bugs.launchpad.net/lxml/+bug/1185701
                self.context = None

            if self.context is None:
                # Always end of doc
                # TODO: is this still useful for a non-input component?
                packet.set_end_of_doc()
                log.info("End of doc: %s elem_count=%d" % (self.cur_file_path, self.elem_count))

                return packet

            # Filter out Namespace from the tag
            # this is the easiest way to go for now
            tag = elem.tag.split('}')
            if len(tag) == 2:
                # Namespaced tag: 2nd is tag
                tag = tag[1]
            else:
                # Non-namespaced tag: first
                tag = tag[0]

            if tag in self.element_tags:
                if event == "start":
                    # TODO check if deepcopy is the right thing to do here.
                    # packet.data = elem
                    pass
                # self.root.remove(elem)
                elif event == "end":
                    # Delete the element from the tree
                    # self.root.clear()
                    packet.data = elem
                    self.elem_count += 1
                    self.root.remove(elem)

                    if self.strip_namespaces:
                        packet.data = Util.stripNamespaces(elem).getroot()

            # If there is a next component, let it process
            if self.next:
                # Hand-over data (line, doc whatever) to the next component
                packet.format = self._output_format
                packet = self.next.process(packet)

        return packet
