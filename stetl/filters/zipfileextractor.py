# Deprecated use from module fileextractor.
#
# Author: Just van den Broecke
#

from stetl.filters.fileextractor import ZipFileExtractor as NewZipFileExtractor


def ZipFileExtractor(*args, **kwargs):
    from warnings import warn
    warn("Use the new stetl.filter.fileextractor.ZipFileExtractor!")
    return NewZipFileExtractor(*args, **kwargs)
