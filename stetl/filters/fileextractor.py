# Extracts a file from and archive file like a .zip,
# and saves it as the given file name.
#
# Author: Just van den Broecke (generic and VsiFileExtractor)
# Author: Frank Steggink (ZipFileExtractor)
#
import os.path
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('fileextractor')

DEFAULT_BUFFER_SIZE = 1024 * 1024 * 1024


class FileExtractor(Filter):
    """
    Abstract Base Class.
    Extracts a file an archive and saves as the configured file name.

    consumes=FORMAT.any, produces=FORMAT.string
    """

    # Start attribute config meta

    @Config(ptype=str, default=None, required=True)
    def file_path(self):
        """
        File name to write the extracted file to.
        """
        pass

    @Config(ptype=bool, default=True, required=False)
    def delete_file(self):
        """
        Delete the file when the chain has been completed?
        """
        pass

    @Config(ptype=int, default=DEFAULT_BUFFER_SIZE, required=False)
    def buffer_size(self):
        """
        Buffer size for read buffer during extraction.
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section, consumes=FORMAT.any, produces=FORMAT.string):
        Filter.__init__(self, configdict, section, consumes=consumes, produces=produces)

    def delete_target_file(self):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    def extract_file(self, packet):
        log.error('Only classes derived from FileExtractor can be used!')

    def invoke(self, packet):

        if packet.data is None:
            log.info("Input data is empty")
            return packet

        # Optionally remove old file
        self.delete_target_file()
        self.extract_file(packet)
        packet.data = self.file_path

        if not os.path.isfile(self.file_path):
            log.warn('Extracted file {} does not exist'.format(self.file_path))
            packet.data = None

        return packet

    def after_chain_invoke(self, packet):
        if not self.delete_file:
            return

        self.delete_target_file()

        return True


class ZipFileExtractor(FileExtractor):
    """
    Extracts a file from a ZIP file, and saves it as the given file name.
    Author: Frank Steggink

    consumes=FORMAT.record, produces=FORMAT.string
    """

    def __init__(self, configdict, section):
        FileExtractor.__init__(self, configdict, section, consumes=FORMAT.record)

    def extract_file(self, packet):

        import zipfile

        with zipfile.ZipFile(packet.data['file_path']) as z:
            with open(self.file_path, 'wb') as f:
                with z.open(packet.data['name']) as zf:
                    while True:
                        buffer = zf.read(self.buffer_size)
                        if not buffer:
                            break
                        f.write(buffer)


class VsiFileExtractor(FileExtractor):
    """
    Extracts a file from a GDAL /vsi path spec, and saves it as the given file name.

    Example paths:
    /vsizip/{/project/nlextract/data/BAG-2.0/BAGNLDL-08112020.zip}/9999STA08112020.zip'
    /vsizip/{/vsizip/{BAGGEM0221L-15022021.zip}/GEM-WPL-RELATIE-15022021.zip}/GEM-WPL-RELATIE-15022021-000001.xml

    See also stetl.inputs.fileinput.VsiZipFileInput that generates these paths.

    Author: Just van den Broecke

    consumes=FORMAT.gdal_vsi_path, produces=FORMAT.string
    """

    def __init__(self, configdict, section):
        FileExtractor.__init__(self, configdict, section, consumes=FORMAT.gdal_vsi_path)

    def extract_file(self, packet):
        from stetl.util import gdal

        # Example input path can be as complex as this:
        #
        vsi_file_path = packet.data
        vsi = None
        vsi_len = 0
        try:
            # gdal.VSIF does not support 'with' so old-school open/close.
            log.info('Extracting {}'.format(vsi_file_path))
            vsi = gdal.VSIFOpenL(vsi_file_path, 'rb')
            with open(self.file_path, 'wb') as f:
                gdal.VSIFSeekL(vsi, 0, 2)
                vsi_len = gdal.VSIFTellL(vsi)
                gdal.VSIFSeekL(vsi, 0, 0)
                read_size = self.buffer_size
                if vsi_len < read_size:
                    read_size = vsi_len

                while True:
                    buffer = gdal.VSIFReadL(1, read_size, vsi)
                    if not buffer or len(buffer) == 0:
                        break
                    f.write(buffer)

        except Exception as e:
            log.error('Cannot extract {} err={}'.format(vsi_file_path, str(e)))
            raise e
        finally:
            if vsi:
                log.info('Extracted {} ok len={} bytes'.format(vsi_file_path, vsi_len))
                gdal.VSIFCloseL(vsi)
