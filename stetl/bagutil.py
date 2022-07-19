import os
import shutil
import zipfile

from stetl.util import Util


log = Util.get_log('bagutil')


class BAGUtil:
    """
    Helper functions for BAG 2.0 Extract processing
    """

    @staticmethod
    def zip_file_content(zip_file):
        log.info("Retrieving content from: %s" % zip_file)

        zip_content = []

        with zipfile.ZipFile(zip_file) as z:
            for name in z.namelist():
                zip_content.append(name)

        return zip_content

    @staticmethod
    def extract_zip_file(zip_file, temp_dir):
        extracted = []

        with zipfile.ZipFile(zip_file) as z:
            for name in z.namelist():
                temp_file = os.path.join(temp_dir, name)

                log.info(
                    "Extracting %s from %s to %s" % (
                        name,
                        zip_file,
                        temp_file,
                    )
                )

                z.extract(name, path=temp_dir)

                extracted.append(temp_file)

        return extracted

    @staticmethod
    def extract_from_zip_file(name, zip_file, temp_dir):
        with zipfile.ZipFile(zip_file) as z:
            if name not in z.namelist():
                raise Exception("Cannot extract file: %s" % name)

            return z.extract(name, path=temp_dir)

    @staticmethod
    def remove_temp_file(temp_file):
        log.info("Removing temp file: %s" % temp_file)
        os.unlink(temp_file)

        return True

    @staticmethod
    def remove_temp_dir(temp_dir):
        log.info("Removing temp dir: %s" % temp_dir)
        shutil.rmtree(temp_dir)

        return True
