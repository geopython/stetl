# -*- coding: utf-8 -*-
#
# Input classes for ETL, Files.
#
# Author: Just van den Broecke
#
from stetl.input import Input
from stetl.util import Util, etree
from stetl.packet import FORMAT

log = Util.get_log('fileinput')

class FileInput(Input):
    """
    Abstract base class for specific FileInputs.
    """

    def __init__(self, configdict, section, produces):
        Input.__init__(self, configdict, section, produces)

        # path to file or files: can be a dir or files or even multiple, comma separated
        self.file_path = self.cfg.get('file_path')

        # The filename pattern according to Python glob.glob
        self.filename_pattern = self.cfg.get('filename_pattern', '*.[gxGX][mM][lL]')

        # Recurse into directories ?
        self.depth_search = self.cfg.get_bool('depth_search', False)

        # Create the list of files to be used as input
        self.file_list = Util.make_file_list(self.file_path, None, self.filename_pattern, self.depth_search)
        log.info("file_list=%s" % str(self.file_list))

    def read(self, packet):
        """
        Override in subclass.
        """
        pass

class StringFileInput(FileInput):
    """
    Reads and produces file as String.

    produces=FORMAT.string
    """

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.string)
        self.file_list_done = []
        self.file = None

        # Optional formatting of content according to Python String.format()
        # Input file should have substitutable values like {schema} {foo}
        # format_args should be of the form format_args = schema:test foo:bar
        self.format_args = self.cfg.get('format_args')

        if self.format_args:
            # Convert string to dict: http://stackoverflow.com/a/1248990
            self.format_args = Util.string_to_dict(self.format_args, ':')

    def read(self, packet):
        # No more files left and done with current file ?
        if not len(self.file_list) and self.file is None:
            packet.set_end_of_stream()
            log.info("EOF file list, all files done")
            return packet

        # Done with current file or first file ?
        if self.file is None:
            self.cur_file_path = self.file_list.pop(0)
            self.file = open(self.cur_file_path, 'r')
            log.info("file opened : %s" % self.cur_file_path)

        # Assume valid file content
        file_content = self.file.read()

        # Optional: string substitution based on Python String.format()
        # But you can also use StringSubstitutionFilter from filters.
        if self.format_args:
            file_content = file_content.format(**self.format_args)

        # Cleanup
        self.file.close()
        self.file = None

        log.info("file read : %s size=%d" % (self.cur_file_path, len(file_content)))

        packet.data = file_content
        return packet


class XmlFileInput(FileInput):
    """
    Parses XML files into etree docs (do not use for large files!).

    produces=FORMAT.etree_doc
    """

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.etree_doc)
        self.file_list_done = []

    def read(self, packet):
        if not len(self.file_list):
            return packet

        file_path = self.file_list.pop(0)
        # One-time read/parse only
        try:
            packet.data = etree.parse(file_path)
            log.info("file read and parsed OK : %s" % file_path)
        except Exception, e:
            log.info("file read and parsed NOT OK : %s" % file_path)

        # One-time read: we're all done
        packet.set_end_of_doc()
        if not len(self.file_list):
            log.info("all files done")
            packet.set_end_of_stream()

        self.file_list_done.append(file_path)
        return packet


class XmlLineStreamerFileInput(FileInput):
    """
    DEPRECATED Streams lines from an XML file(s)
    NB assumed is that lines in the file have newlines !!
    DEPRECATED better is to use XmlElementStreamerFileInput for GML features.

    produces=FORMAT.xml_line_stream
    """

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.xml_line_stream)
        self.file_list_done = []
        self.file = None

    def read(self, packet):
        # No more files left and done with current file ?
        if not len(self.file_list) and self.file is None:
            packet.set_end_of_stream()
            log.info("EOF file list")
            return packet

        # Done with current file or first file ?
        if self.file is None:
            self.cur_file_path = self.file_list.pop(0)
            self.file = open(self.cur_file_path, 'r')
            log.info("file opened : %s" % self.cur_file_path)

        if packet.is_end_of_stream():
            return packet

        # Assume valid line
        line = self.file.readline()

        # EOF reached ?
        if not line or line == '':
            packet.data = None

            packet.set_end_of_doc()
            log.info("EOF file")
            if self.cur_file_path is not None:
                self.file_list_done.append(self.cur_file_path)
                self.cur_file_path = None
                if not len(self.file_list):
                    # No more files left: end of stream reached
                    packet.set_end_of_stream()
                    log.info("EOF file list")

            self.file = None

            return packet

        packet.data = line.decode('utf-8')
        return packet

class XmlElementStreamerFileInput(FileInput):
    """
    Extracts XML elements from a file, outputs each feature element in Packet.
    Parsing is streaming (no internal DOM buildup) so any file size can be handled.
    Use this class for your big GML files!

    produces=FORMAT.etree_element_stream
    """

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.etree_element_stream)
        self.element_tags = self.cfg.get('element_tags').split(',')
        self.file_list_done = []
        self.strip_namespaces = self.cfg.get('strip_namespaces', False)
        self.context = None
        self.root = None
        self.cur_file_path = None
        self.elem_count = 0

    def read(self, packet):
        event = None
        packet.data = None

        if self.context is None:
            if not len(self.file_list):
                # No more files left, all done
                log.info("No more files left")
                return packet

            # Files available: pop next file
            self.cur_file_path = self.file_list.pop(0)
            fd = open(self.cur_file_path)
            self.elem_count = 0
            log.info("file opened : %s" % self.cur_file_path)
            self.context = etree.iterparse(fd, events=("start", "end"))
            self.context = iter(self.context)
            event, self.root = self.context.next()

        try:
            event, elem = self.context.next()
        except (etree.XMLSyntaxError, StopIteration):
            # workaround for etree.XMLSyntaxError https://bugs.launchpad.net/lxml/+bug/1185701
            self.context = None

        if self.context is None:
            # Always end of doc
            packet.set_end_of_doc()
            log.info("End of doc: %s elem_count=%d" % (self.cur_file_path, self.elem_count))

            # Maybe end of stream (all docs done)
            if not len(self.file_list):
                # No more files left: end of stream
                packet.set_end_of_stream()
                log.info("End of stream")

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

        return packet
