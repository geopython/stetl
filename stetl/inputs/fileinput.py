# Input classes for ETL, Files.
#
# Author: Just van den Broecke
#
import csv
import re
import fnmatch
import io

from deprecated.sphinx import deprecated

from stetl.component import Config
from stetl.input import Input
from stetl.util import Util, etree
from stetl.utils.apachelog import formats, parser
from stetl.packet import FORMAT

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
        """
        pass

    @Config(ptype=str, default='*.[gxGX][mM][lL]', required=False)
    def filename_pattern(self):
        """
        Filename pattern according to Python ``glob.glob`` for example:
        '\\*.[gxGX][mM][lL]'
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def depth_search(self):
        """
        Should we recurse into sub-directories to find files?
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

        self.cur_file_path = None
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

    def read_file(self, file_path):
        """
        Overridden from base class.
        """

        file_content = None
        with open(file_path, 'r') as f:
            file_content = f.read()
            # Optional: string substitution based on Python String.format()
            # But you can also use StringSubstitutionFilter from filters.
            if self.format_args:
                file_content = file_content.format(**self.format_args)

        return file_content


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
        except Exception as e:
            log.info('file read and parsed NOT OK : %s, err=%s' % (file_path, str(e)))

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
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def strip_namespaces(self):
        """
        should namespaces be removed from the input document and thus not be present in the output element stream?
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.etree_element)
        self.file_list_done = []
        self.context = None
        self.root = None
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
            fd = open(self.cur_file_path, 'rb')
            self.elem_count = 0
            log.info("file opened : %s" % self.cur_file_path)
            self.context = etree.iterparse(fd, events=("start", "end"))
            self.context = iter(self.context)
            event, self.root = next(self.context)

        try:
            event, elem = next(self.context)
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


class LineStreamerFileInput(FileInput):
    """
    Reads text-files, producing a stream of lines, one line per Packet.
    NB assumed is that lines in the file have newlines !!
    """

    def __init__(self, configdict, section, produces=FORMAT.line_stream):
        FileInput.__init__(self, configdict, section, produces)
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

        try:
            line = line.decode('utf-8')
        except AttributeError:
            # no need to decode
            pass
        packet.data = self.process_line(line)

        return packet

    def process_line(self, line):
        """
        Override in subclass.
        """
        return line


@deprecated(version='1.0.9', reason='Better to use XmlElementStreamerFileInput for GML features')
class XmlLineStreamerFileInput(LineStreamerFileInput):
    """
    DEPRECATED Streams lines from an XML file(s)
    NB assumed is that lines in the file have newlines !!

    produces=FORMAT.xml_line_stream
    """

    # Constructor
    def __init__(self, configdict, section):
        LineStreamerFileInput.__init__(self, configdict, section, produces=FORMAT.xml_line_stream)


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
        """
        pass

    @Config(ptype=str, default='"', required=False)
    def quote_char(self):
        """
        A one-character string used to quote fields containing special characters, such as the delimiter or quotechar,
        or which contain new-line characters. It defaults to '"'.
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def empty_string_is_none(self):
        """
        Should we use None instead of '' for empty fields
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
            # To comply with Stetl record type: force ordinary/base dict-type.
            # Python 3.6+ returns OrderedDict which may not play nice up the Chain
            record = dict(next(self.csv_reader))

            if self.empty_string_is_none:
                for field in record:
                    if record[field] == '':
                        record[field] = None

            packet.data = record
            if self._output_format == FORMAT.record_array:
                while True:
                    self.arr.append(packet.data)

                    record = dict(next(self.csv_reader))

                    if self.empty_string_is_none:
                        for field in record:
                            if record[field] == '':
                                record[field] = None

                    packet.data = record

            log.info("CSV row nr %d read: %s" % (self.csv_reader.line_num - 1, packet.data))
        except Exception:
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
                from urllib.request import urlopen

                fp = urlopen(file_path)
                file_data = json.loads(fp.read().decode('utf-8'))
            else:
                with open(file_path) as data_file:
                    file_data = json.load(data_file)

        except Exception as e:
            log.error('Cannot read JSON from %s, err= %s' % (file_path, str(e)))
            raise e

        return file_data


class ApacheLogFileInput(FileInput):
    """
    Parses Apache log files. Lines are converted into records based on the log format.
    Log format should follow Apache Log Format. See ApacheLogParser for details.

    produces=FORMAT.record

    """

    @Config(ptype=dict, default={'%l': 'logname', '%>s': 'status', '%D': 'deltat',
                                 '%{User-agent}i': 'agent', '%b': 'bytes', '%{Referer}i': 'referer',
                                 '%u': 'user', '%t': 'time', "'%h": 'host', '%r': 'request'}, required=False)
    def key_map(self):
        """
        Map of cryptic %-field names to readable keys in record.

        """
        pass

    @Config(ptype=str, default=formats['extended'], required=False)
    def log_format(self):
        """
        Log format according to Apache CLF
        """
        pass

    # Constructor
    def __init__(self, configdict, section):
        FileInput.__init__(self, configdict, section, produces=FORMAT.record)
        self.file_list_done = []
        self.file = None
        self.parser = parser(self.log_format, self.key_map, options={'methods': ['GET', 'POST'],
                                                                     'use_native_types': True,
                                                                     'request_path_only': True,
                                                                     'gen_key': True})

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

        # Parse logfile line into record (dict)
        packet.data = None
        try:
            packet.data = self.parser.parse(line)
        except Exception as e:
            log.warn("Cannot parse e=%s" % str(e))

        return packet


class ZipFileInput(FileInput):
    """
    Parse ZIP file from file system or URL into a stream of records containing zipfile-path and file names.

    produces=FORMAT.record
    """

    @Config(ptype=str, default='*', required=False)
    def name_filter(self):
        """
        Regular "glob.glob" expression for filtering out filenames from the ZIP archive.
        """
        pass

    def __init__(self, configdict, section, produces=FORMAT.record):
        FileInput.__init__(self, configdict, section, produces)
        self.file_content = None

        # Pre-compile name filter into regex object to match filenames in zip-archive(s) later
        # See default (*) above, so we alo have a name_filter.
        self.fname_matcher = re.compile(fnmatch.translate(self.name_filter))

    def create_file_content(self, file_path):
        # Subclasses to override
        # Assemble list of file names in archive
        import zipfile
        zip_file = zipfile.ZipFile(file_path, 'r')
        file_name_list = [{'file_path': file_path, 'name': name} for name in zip_file.namelist()]

        # Apply filename filter to namelist (TODO could be done in single step with previous step)
        return [item for item in file_name_list if self.fname_matcher.match(item["name"])]

    def read(self, packet):
        # No more files left and done with current file ?
        if not self.file_content and not len(self.file_list):
            packet.set_end_of_stream()
            log.info("EOF file list, all files done")
            return packet

        # Done with current file or first file ?
        if self.file_content is None:
            cur_file_path = self.file_list.pop(0)

            self.file_content = self.create_file_content(cur_file_path)

            log.info("zip file read : %s filecount=%d" % (cur_file_path, len(self.file_content)))

        if len(self.file_content):
            packet.data = self.file_content.pop(0)
            log.info("Pop file record: %s" % str(packet.data))

        if not len(self.file_content):
            self.file_content = None

        return packet


class VsiZipFileInput(ZipFileInput):
    """
    Parse ZIP file from file system into a stream of strings containing GDAL/OGR /vsizip paths.
    Also handles cases for embedded zips (zips within zips within zips etc).
    It outputs strings, where each string is a 'vsizip' path that can be input to mainly
    OGR-components.

    produces=FORMAT.gdal_vsi_path
    """

    def __init__(self, configdict, section):
        ZipFileInput.__init__(self, configdict, section, produces=FORMAT.gdal_vsi_path)

    def list_zips(self, f, parent=[]):
        # https://unix.stackexchange.com/questions/239898/listing-files-from-nested-zip-files-without-extracting
        import zipfile
        result = []
        try:
            # Example outputs (BAG) zip files:
            # /vsizip/{test/data/0221PND15092020.zip}/0221PND15092020-000001.xml
            # /vsizip/{/vsizip/{/Users/just/project/nlextract/data/BAG-2.0/BAGNLDL-08112020.zip}/9999OPR08112020.zip}
            # /vsizip/{/vsizip/{/vsizip/{test/BAGGEM0221L-15022021.zip}/0221GEM15022021.zip}/0221PND15022021.zip}/0221PND15022021-000001.xml
            # Handle /vsizip prefixing and embedding.
            par_last = len(parent) - 1
            if type(f) is str:
                # First: f is a filepath, embed path in /vsizip/{path}
                parent = ['/vsizip/{{{}}}'.format(f)]
            elif parent[par_last].lower().endswith('.zip'):
                # Nested .zip: embed in /vsizip/{parent}
                parent[0] = '/vsizip/{{{}'.format(parent[0])
                parent[par_last] = '{}}}'.format(parent[par_last])

            # Fetch names from zipfile archive
            zip_file = zipfile.ZipFile(f)
            for fname in zip_file.namelist():

                path = parent + [fname]

                if fname.lower().endswith('.zip'):
                    # .zip in .zip: recurse to handle
                    result += self.list_zips(io.BytesIO(zip_file.open(fname).read()), path)

                # Filter-in matching filenames from archive
                if self.fname_matcher.match(fname):
                    log.debug('MATCH: ' + str(path))
                    entry = '/'.join(path)

                    # Matched entries for .zip within .zip do not play nice with
                    # VSI GDAL file handling.
                    # Example: /vsizip/{/vsizip/{/data/BAG-2.0/BAGNLDL-08112020.zip}/9999OPR08112020.zip}
                    # Becomes: /vsizip/{/data/BAG-2.0/BAGNLDL-08112020.zip}/9999OPR08112020.zip
                    if entry.endswith('.zip}') and entry.startswith('/vsizip/{/vsizip'):
                        log.debug('ZIP ENTRY: ' + entry)
                        entry = entry.replace('/vsizip/{', '', 1)
                        entry = entry.rstrip('}')

                    log.debug('ADD ENTRY: ' + entry)
                    result.append(entry)

        except Exception as ex:
            log.warn('Exception during vsizip processing: {}'.format(str(ex)))
            return []

        return result

    def create_file_content(self, file_path):
        return self.list_zips(file_path)


class GlobFileInput(FileInput):
    """
    Returns file names based on the glob.glob pattern given as filename_filter.

    produces=FORMAT.string or FORMAT.line_stream
    """

    def __init__(self, configdict, section, produces=[FORMAT.string, FORMAT.line_stream]):
        FileInput.__init__(self, configdict, section, produces)

    def read(self, packet):
        if not len(self.file_list):
            return packet

        file_path = self.file_list.pop(0)

        # TODO: os.path.join?
        packet.data = file_path

        # One-time read: we're all done
        packet.set_end_of_doc()
        if not len(self.file_list):
            log.info("all files done")
            packet.set_end_of_stream()

        self.file_list_done.append(file_path)
        return packet
