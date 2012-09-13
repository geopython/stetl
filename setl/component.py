#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Component base class for ETL.
#
# Author: Just van den Broecke
#
from setl.util import Util
from setl.util import ConfigSection

log = Util.get_log('component')


# Base class for all Input, Transformer, Outputs
class Component:
    def __init__(self, configdict, section):
        self.configdict = configdict
        self.cfg = ConfigSection(configdict.items(section))
        self.next = None

    def process(self, packet):
        # Do something with the data
        packet = self.invoke(packet)

        # If there is a next component, let it process
        if self.next:
            # Hand-over data (line, doc whatever) to the next component
            packet = self.next.process(packet)

        return packet

    def do_init(self):
        # Some components may do one-time init
        self.init()

        # If there is a next component, let it do its init()
        if self.next:
            self.next.do_init()

    def do_exit(self):
        # Notify all comps that we exit
        self.exit()

        # If there is a next component, let it do its exit()
        if self.next:
            self.next.do_exit()

    def invoke(self, packet):
        return packet

    def init(self):
        pass

    def exit(self):
        pass
