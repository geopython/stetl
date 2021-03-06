# Expands an archive file into a collection of files.
#
# Author: Just van den Broecke 2021
#
import os.path
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('archiveexpander')


class ArchiveExpander(Filter):
    """
    Abstract Base Class.
    Expands an archive file into a collection of files.

    consumes=FORMAT.string, produces=FORMAT.string
    """

    # Start attribute config meta

    @Config(ptype=str, default='temp_dir', required=True)
    def target_dir(self):
        """
        Target directory to write the extracted files to.
        """
        pass

    @Config(ptype=bool, default=False, required=False)
    def remove_input_file(self):
        """
        Delete input archive file when the chain has been completed?
        """
        pass

    @Config(ptype=bool, default=True, required=False)
    def clear_target_dir(self):
        """
        Delete the files from the target directory  when the chain has been completed?
        """
        pass

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section, consumes, produces):
        Filter.__init__(self, configdict, section, consumes=consumes, produces=produces)
        self.input_archive_file = None
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)

    def remove_file(self, file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)

    def wipe_dir(self, dir_path):
        if os.path.isdir(dir_path):
            for file_object in os.listdir(dir_path):
                file_object_path = os.path.join(dir_path, file_object)
                if os.path.isdir(file_object_path):
                    self.wipe_dir(file_object_path)
                    os.rmdir(file_object_path)
                    return

                os.remove(file_object_path)

    def expand_archive(self, packet):
        log.error('Only classes derived from ArchiveExpander can be used!')

    def invoke(self, packet):

        if packet.data is None:
            log.info("Input data is empty")
            return packet

        # Optionally clear target dir
        self.wipe_dir(self.target_dir)

        self.input_archive_file = packet.data

        # Let derived class provide archive expansion (.zip, .tar etc)
        self.expand_archive(self.input_archive_file)
        if not os.listdir(self.target_dir):
            log.warn('No expanded files in {}'.format(self.target_dir))
            packet.data = None
            return packet

        # ASSERT: expanded files in target dir
        file_count = len(os.listdir(self.target_dir))
        log.info('Expanded {} into {} OK - filecount={}'.format(
            self.input_archive_file, self.target_dir, file_count))

        # Output the target dir path where expanded files are found
        packet.data = self.target_dir

        return packet

    def after_chain_invoke(self, packet):
        if self.remove_input_file:
            self.remove_file(self.input_archive_file)

        if self.clear_target_dir:
            self.wipe_dir(self.target_dir)

        return True


class ZipArchiveExpander(ArchiveExpander):
    """
    Extracts all files from a ZIP file into the configured  target directory.

    consumes=FORMAT.string, produces=FORMAT.string
    """

    def __init__(self, configdict, section):
        ArchiveExpander.__init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.string)

    def expand_archive(self, file_path):

        import zipfile
        if not file_path.lower().endswith('zip'):
            log.warn('No zipfile passed: {}'.format(file_path))
            return

        zipfile.ZipFile(file_path).extractall(path=self.target_dir)
