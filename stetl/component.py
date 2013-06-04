# -*- coding: utf-8 -*-
#
# Component base class for ETL.
#
# Author: Just van den Broecke
#
from util import Util, ConfigSection
from packet import FORMAT

log = Util.get_log('component')


class Component:
    """
    Abstract Base class for all Input, Filter and Output Components.

    """

    def __init__(self, configdict, section, consumes=None, produces=None):
        self.configdict = configdict
        self.cfg = ConfigSection(configdict.items(section))
        self.next = None
        self.output_format = produces
        self.input_format = consumes

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

    # Check our compatibility with the next Component in the Chain
    def is_compatible(self):
        # Ok, nothing next in Chain
        if self.next is None:
            return True

        # return if our Output is compatible with the next Component's Input
        return self.output_format is not None \
                   and self.next.input_format is not None \
            and (self.output_format == self.next.input_format or self.next.input_format == FORMAT.any)

        #    def __str__(self):
        #        return "foo"