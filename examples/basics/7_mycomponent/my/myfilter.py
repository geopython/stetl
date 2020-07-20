# -*- coding: utf-8 -*-
#
# Example of user-defined component.
#
# Author:Just van den Broecke

from stetl.util import Util
from stetl.filter import Filter
from stetl.packet import FORMAT

log = Util.get_log("myfilter")


class MyFilter(Filter):
    # Constructor
    def __init__(self, configdict, section):
        Filter.__init__(self, configdict, section, consumes=FORMAT.etree_doc, produces=FORMAT.etree_doc)

    def invoke(self, packet):
        if packet.data is None:
            return packet
        return self.do_something(packet)

    def do_something(self, packet):
        log.info("CALLING MyFilter OK!!!!")
        data = packet.data
        self.show_data(data)

        return packet

    def show_data(self, data):
        try:
            from lxml import etree
        except ImportError:
            # No lxml, so just print data
            print(data)
        else:
            root = data.getroot()
            for city in root.iterchildren():
                city_name = city.find('name').text
                print('Welcome to {c} !'.format(c=city_name))

