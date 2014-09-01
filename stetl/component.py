# -*- coding: utf-8 -*-
#
# Component base class for ETL.
#
# Author: Just van den Broecke
#
from util import Util, ConfigSection
from packet import FORMAT

log = Util.get_log('component')

class Attr():
    """
    Util class to privide metadata for per component config attr options.
    Each component should document its configuration metadata using the following
    conventions, for say a config attr 'my_attr':

    - name a component class attribute cfg_<my_attr>
    - assign an instance of this class with type, mandatory, default value and documentation

    For example:

      class FileInput(Input):

        cfg_file_path = Attr(str, True, None,
        "path to file or files: can be a dir or files or even multiple, comma separated")

    Via the Stetl command 'stetl --doc <Component>' the documentation can be viewed.

    NB this convention came out of struggling with autodoc and class attribute __doc__
    strings tried first. Somehow that did not work.
    """
    def __init__(self, typ=str, mandatory=False, default=None, doc="No doc"):
        self.type = typ
        self.mandatory = mandatory
        self.default = default
        self.doc = doc

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
        result = self.before_invoke(packet)
        if result is False:
            # Component indicates it does not want the chain to proceed
            return packet

        # Do component-specific processing, e.g. read or write or filter
        packet = self.invoke(packet)

        result = self.after_invoke(packet)
        if result is False:
            # Component indicates it does not want the chain to proceed
            return packet

        # If there is a next component, let it process
        if self.next:
            # Hand-over data (line, doc whatever) to the next component
            packet.format = self.output_format
            packet = self.next.process(packet)

        result = self.after_chain_invoke(packet)
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

    def before_invoke(self, packet):
        """
        Called just before Component invoke.
        """
        return True

    def after_invoke(self, packet):
        """
        Called right after Component invoke.
        """
        return True

    def after_chain_invoke(self, packet):
        """
        Called right after entire Component Chain invoke.
        """
        return True

    def invoke(self, packet):
        """
        Components override for Component-specific behaviour, typically read, filter or write actions.
        """
        return packet

    def init(self):
        """
        Allows derived Components to perform a one-time init.
        """
        pass

    def exit(self):
        """
        Allows derived Components to perform a one-time exit/cleanup.
        """
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