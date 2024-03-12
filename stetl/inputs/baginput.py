import os
import pprint
import re

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

    @Config(ptype=bool, required=False, default=False)
    def multiprocessing(self):
        """
        Process multiple files in parallel
        """
        pass

    def exit(self):
        log.info('Exit: removing temp files')

        for entry in self.extracted:
            if os.path.exists(entry):
                BAGUtil.remove_temp_file(entry)

    def process_zip_file(self, zip_file, initial=True):
        zip_content = BAGUtil.zip_file_content(zip_file)

        if(
            initial is True or  # noqa: W504
            re.search(
                r'^\d{4}(?:Inactief|InOnderzoek|NietBag)\d{8}\.zip$',
                os.path.basename(zip_file),
            )
        ):
            extract_zip_file = True
        else:
            extract_zip_file = False

        if extract_zip_file:
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

        if self.multiprocessing:
            if initial is True:
                leverings_xml = 'Leveringsdocument-BAG-Extract.xml'

                if leverings_xml in zip_content:
                    self.file_list.append(
                        os.path.join(
                            self.temp_dir,
                            leverings_xml,
                        )
                    )

                for entry in sorted(zip_content):
                    if(
                        re.search(
                            r'^\d{4}(MUT)\d{8}-\d{8}\.zip$|^\d{4}(?:LIG|NUM|OPR|PND|STA|VBO|WPL)\d{8}\.zip$',
                            entry,
                        ) or  # noqa: W504
                        re.search(
                            r'^GEM\-WPL\-RELATIE\-\d{8}\.zip$',
                            entry,
                        )
                    ):
                        self.file_list.append(
                            os.path.join(
                                self.temp_dir,
                                entry,
                            )
                        )

                for entry in sorted(zip_content):
                    if re.search(
                        r'^\d{4}(?:Inactief|InOnderzoek|NietBag)\d{8}\.zip$',
                        entry,
                    ):
                        self.process_zip_file(
                            os.path.join(
                                self.temp_dir,
                                entry,
                            ),
                            initial=False,
                        )
            else:
                for entry in sorted(zip_content):
                    if re.search(
                        r'^\d{4}(?:IO|)(MUT)\d{8}-\d{8}\.zip$|^\d{4}(?:IA|IO|NB)(?:LIG|NUM|OPR|PND|STA|VBO|WPL)\d{8}\.zip$',
                        entry,
                    ):
                        self.file_list.append(
                            os.path.join(
                                self.temp_dir,
                                entry,
                            )
                        )
        else:
            for entry in zip_content:
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
                        ),
                        initial=False,
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

            log.info("Empty file list")

            return packet

        if self.multiprocessing:
            file_list = self.file_list

            log.info("Read: file list")

            packet.data = {
                'file_list': file_list,
            }

            self.file_list = []
        else:
            entry = self.file_list.pop(0)

            log.info("Read entry: %s" % entry)

            packet.data = entry

        return packet
