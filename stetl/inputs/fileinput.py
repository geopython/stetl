# -*- coding: utf-8 -*-
#
# Input classes for ETL, Files.
#
# Author: Just van den Broecke
#
from stetl.component import Config
from stetl.input import Input
from stetl.util import Util, etree
from stetl.packet import FORMAT
import csv

log = Util.get_log('fileinput')


class FileInput(Input):
    """
    Abstract base class for specific FileInputs, use derived classes.
    """

    # Start attribute config meta
    # Applying Decorator pattern with the Config class to provide
    # read-only config values from the configured properties.
    
    @Config(ptype=str, default=None, required=False)
    def file_path(self):
        """
        Path to file or files or URLs: can be a dir or files or URLs
        or even multiple, comma separated. For URLs only JSON is supported now.

        Required: True

        Default: None
        """
        pass


    @Config(ptype=str, default='*.[gxGX][mM][lL]', required=False)
    def filename_pattern(self):
        """
        Filename pattern according to Python ``glob.glob`` for example:
        '\*.[gxGX][mM][lL]'

        Required: False

        Default: '\*.[gxGX][mM][lL]'
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def depth_search(self):
        """
        Should we recurse into sub-directories to find files?

        Required: False

        Default: False
        """
        pass

    # End attribute config meta

    def __init__(self, configdict, section, produces):
        Input.__init__(self, configdict, section, produces)

        # Create the list of files to be used as input
        self.file_list = Util.make_file_list(self.file_path, None, self.filename_pattern, self.depth_search)
        log.info("file_list=%s" % str(self.file_list))
        if not len(self.file_list):
            raise Exception('File list is empty!!')

        self.file_list_done = []

    def read(self, packet):
        if not len(self.file_list):
            return packet

        file_path = self.file_list.pop(0)

        log.info("Read/parse for start for file=%s...." % file_path)
        packet.data = self.read_file(file_path)
        log.info("Read/parse ok for file=%s" % file_path)

        # One-time read: we're all done
        packet.set_end_of_doc()
        if not len(self.file_list):
            log.info("all files done")
            packet.set_end_of_stream()

        self.file_list_done.append(file_path)
        return packet

    def read_file(self, file_path):
        """
        Override in subclass.
        """
        pass


class StringFileInput(FileInput):
    """
    Reads and produces file as String.

    produces=FORMAT.string
    """

    # Start attribute config meta
    @Config(ptype=str, default=None, required=False)
    def format_args(self):
        """
        Formatting of content according to Python String.format()
        Input file should have substitutable values like {schema} {foo}
        format_args should be of the form ``format_args = schema:test foo:bar``

        Required: False

        Default: None
        """
        pass

    # End attribute config meta

    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.string)
        self.file = None

        # Optional formatting of content according to Python String.format()
        # Input file should have substitutable values like {schema} {foo}
        # format_args should be of the form format_args = schema:test foo:bar

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

    def read_file(self, file_path):
        # One-time read/parse only
        data = None
        try:
            data = etree.parse(file_path)
        except Exception, e:
            log.info("file read and parsed NOT OK : %s" % file_path)

        return data



class XmlElementStreamerFileInput(FileInput):
    """
    Extracts XML elements from a file, outputs each feature element in Packet.
    Parsing is streaming (no internal DOM buildup) so any file size can be handled.
    Use this class for your big GML files!

    produces=FORMAT.etree_element
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
        FileInput.__init__(self, configdict, section, produces=FORMAT.etree_element)
        self.file_list_done = []
        self.context = None
        self.root = None
        self.cur_file_path = None
        self.elem_count = 0
        log.info("Element tags to be matched: %s" % self.element_tags)

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


class CsvFileInput(FileInput):
    """
    Parse CSV file into stream of records (dict structures) or a one-time record array.
    NB raw version: CSV needs to have first line with fieldnames.

    produces=FORMAT.record or FORMAT.record_array
    """

    @Config(ptype=str, default=',', required=False)
    def delimiter(self):
        """
        A one-character string used to separate fields. It defaults to ','.

        Required: False

        Default: ',' (comma)
        """
        pass


    @Config(ptype=str, default='"', required=False)
    def quote_char(self):
        """
        A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters. It defaults to '"'

        Required: False

        Default: "
        """
        pass

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=[FORMAT.record_array, FORMAT.record])
        self.file = None

    def init(self):
        # Init CSV reader
        log.info('Open CSV file: %s', self.file_path)
        self.file = open(self.file_path)

        self.csv_reader = csv.DictReader(self.file, delimiter=self.delimiter, quotechar=self.quote_char)

        if self._output_format == FORMAT.record_array:
            self.arr = list()

    def read(self, packet):
        try:
            packet.data = self.csv_reader.next()
            if self._output_format == FORMAT.record_array:
                while True:
                    self.arr.append(packet.data)
                    packet.data = self.csv_reader.next()

            log.info("CSV row nr %d read: %s" % (self.csv_reader.line_num - 1, packet.data))
        except Exception, e:
            if self._output_format == FORMAT.record_array:
                packet.data = self.arr

            packet.set_end_of_stream()
            self.file.close()

        return packet


class JsonFileInput(FileInput):
    """
    Parse JSON file from file system or URL into hierarchical data struct.
    The struct format may also be a GeoJSON structure. In that case the
    output_format needs to be explicitly set to geojson_collection in the component
    config.

    produces=FORMAT.struct or FORMAT.geojson_collection
    """

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=[FORMAT.struct, FORMAT.geojson_collection])

    def read_file(self, file_path):
        # One-time read/parse only
        try:
            import json
            # may read/parse JSON from file or URL
            if file_path.startswith('http'):
                import urllib2

                fp = urllib2.urlopen(file_path)
                file_data = json.loads(fp.read())
            else:
                with open(file_path) as data_file:
                    file_data = json.load(data_file)

        except Exception, e:
            log.error('Cannot read JSON from %s, err= %s' % (file_path, str(e)))
            raise e

        return file_data
