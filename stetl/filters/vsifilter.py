# -*- coding: utf-8 -*-
#
# Applies a GDAL/OGR virtual file system (VSI) filter to the input source.
# See for more information: https://www.gdal.org/gdal_virtual_file_systems.html
#
# Author: Frank Steggink
#
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('vsifilter')


class VsiFilter(Filter):
    """
    Abstract base class for applying a GDAL/OGR virtual file system (VSI) filter.
    """

    # Start attribute config meta

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section, vsiname):
        Filter.__init__(self, configdict, section, consumes=FORMAT.record, produces=FORMAT.string)
        self.vsiname = vsiname

    def invoke(self, packet):

        if packet.data is None:
            log.info("No file name given")
            return packet

        file_path = packet.data['file_path'].replace('\\', '/')
        packet.data = '/%s/%s/%s' % (self.vsiname, file_path, packet.data['name'])
        return packet


class VsiZipFilter(VsiFilter):
    """
    Applies a VSIZIP filter to the input record.

    consumes=FORMAT.record, produces=FORMAT.string
    """

    # Start attribute config meta

    # End attribute config meta

    # Constructor
    def __init__(self, configdict, section):
        VsiFilter.__init__(self, configdict, section, 'vsizip')
