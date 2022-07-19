import os
import pprint

from stetl.bagutil import BAGUtil
from stetl.component import Config
from stetl.input import Input
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('baginput')


class BAGInput(Input):
    """
    Parse BAG 2.0 Extract ZIP files into a stream of records containing zipfile path and file names.

    produces=FORMAT.record
    """

    @Config(ptype=str, required=True, default=None)
    def file_path(self):
        """
        Path to BAG 2.0 Extact ZIP file (lvbag-extract-nl.zip)
        """
        pass

    @Config(ptype=str, required=False, default='/tmp')
    def temp_dir(self):
        """
        Path for temporary directory
        """
        pass

    def exit(self):
        log.info('Exit: removing temp files')

        for entry in self.extracted:
            if os.path.exists(entry):
                BAGUtil.remove_temp_file(entry)

    def process_zip_file(self, zip_file):
        zip_content = BAGUtil.zip_file_content(zip_file)

        contains_zip_file = False

        for entry in zip_content:
            if entry.endswith('.zip'):
                contains_zip_file = True
                break

        if contains_zip_file:
            extracted = BAGUtil.extract_zip_file(zip_file, self.temp_dir)

            for entry in extracted:
                if(
                    os.path.isdir(entry) or                     # noqa: W504
                    os.path.basename(entry).startswith('.') or  # noqa: W504
                    not os.path.exists(entry)
                ):
                    log.info("Not processing: %s" % entry)

                    if os.path.isdir(entry) and os.path.exists(entry):
                        BAGUtil.remove_temp_dir(entry)
                    elif os.path.exists(entry):
                        BAGUtil.remove_temp_file(entry)

                    zip_content.remove(os.path.basename(entry))

                    continue

                if(
                    not entry.endswith('.xml') and  # noqa: W504
                    not entry.endswith('.zip')
                ):
                    log.warning("Skipping unsupported file: %s" % entry)

                    BAGUtil.remove_temp_file(entry)

                    zip_content.remove(os.path.basename(entry))

                self.extracted.append(entry)

        for entry in sorted(zip_content):
            if(
                entry.startswith('.') or  # noqa: W504
                entry.startswith('_')
            ):
                continue

            if entry.endswith('.zip'):
                self.process_zip_file(
                    os.path.join(
                        self.temp_dir,
                        entry,
                    )
                )
            elif entry.endswith('.xml'):
                item = {
                    'file_path': zip_file,
                    'name': entry,
                }

                self.file_list.append(item)
            else:
                log.warning("Ignoring entry: %s" % entry)

    def __init__(self, configdict, section, produces=FORMAT.record):
        Input.__init__(self, configdict, section, produces)

        self.file_list = []
        self.extracted = []

        self.process_zip_file(self.file_path)

        log.debug("file_list:\n%s" % pprint.pformat(self.file_list))

    def read(self, packet):
        if not len(self.file_list):
            packet.set_end_of_stream()

            log.info("End of file list")

            return packet

        entry = self.file_list.pop(0)

        log.info("Read entry: %s" % entry)

        packet.data = entry

        return packet
