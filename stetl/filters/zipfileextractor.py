# -*- coding: utf-8 -*-
#
# Extracts a file from a ZIP file, and saves it as the given file name.
#
# Author: Frank Steggink
#
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('zipfileextractor')

BUFFER_SIZE = 1024 * 1024 * 1024


class ZipFileExtractor(Filter):
    """
    Extracts a file from a ZIP file, and saves it as the given file name.

    consumes=FORMAT.record, produces=FORMAT.string
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

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.record, produces=FORMAT.string)
        self.cur_file_path = self.cfg.get('file_path')

    def invoke(self, packet):

        if packet.data is None:
            log.info("No file name given")
            return packet

        import zipfile

        with zipfile.ZipFile(packet.data['file_path']) as z:
            with open(self.cur_file_path, 'wb') as f:
                with z.open(packet.data['name']) as zf:
                    while True:
                        buffer = zf.read(BUFFER_SIZE)
                        if not buffer:
                            break
                        f.write(buffer)

        packet.data = self.cur_file_path
        return packet

    def after_chain_invoke(self, packet):
        import os.path
        if os.path.isfile(self.cur_file_path) and self.delete_file:
            os.remove(self.cur_file_path)

        return True
