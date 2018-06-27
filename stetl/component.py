# -*- coding: utf-8 -*-
#
# Component base class for ETL.
#
# Author: Just van den Broecke
#
import os
import sys
from time import time
from util import Util, ConfigSection
from packet import FORMAT

log = Util.get_log('component')


class Config(object):
    """
    Decorator class to tie config values from the .ini file to object instance
    property values. Somewhat like the Python standard @property but with
    the possibility to define default values, typing and making properties required.

    Each property is defined by @Config(type, default, required).
    Basic idea comes from:  https://wiki.python.org/moin/PythonDecoratorLibrary#Cached_Properties
    """

    def __init__(self, ptype=str, default=None, required=False):
        """
        If there are no decorator arguments, the function
        to be decorated is passed to the constructor.
        """
        # print "Inside __init__()"
        self.ptype = ptype
        self.default = default
        self.required = required

    def __call__(self, fget, doc=''):
        """
        The __call__ method is not called until the
        decorated function is called. self is returned such that __get__ below is called
        with the Component instance. That allows us to cache the actual property value
        in the Component itself.
        """
        # Save the property name (is the name of the function calling us).
        self.property_name = fget.__name__
        # print "Inside __call__() name=%s" % self.property_name

        # For Spinx documentation build we need the original function with docstring.
        IS_SPHINX_BUILD = bool(os.getenv('SPHINX_BUILD'))
        if IS_SPHINX_BUILD:
            doc = doc.strip()
            # TODO more detail, example below
            # doc = '``Parameter`` - %s\n\n' % doc
            doc += '* type: %s\n' % str(self.ptype).split("'")[1]
            doc += '* required: %s\n' % self.required
            doc += '* default: %s\n' % self.default

            # if self.value:
            #     doc += '* value: %s\n' % self.value
            # else:
            #     doc += '* required: %s\n' % self.required
            #     doc += '* default: %s\n' % self.default
            #     doc += '* value_range: %s\n' % self.value_range

            fget.__doc__ = '``CONFIG`` %s\n%s' % (fget.__doc__, doc)
            return fget
        else:
            return self

    def __get__(self, comp_inst, owner):
        # print "Inside __get__() owner=%s" % owner
        """ descr.__get__(obj[, type]) -> value """
        if self.property_name not in comp_inst.cfg_vals:
            cfg, name, default_value = comp_inst.cfg, self.property_name, self.default

            # Do type conversion where needed from the string values
            if self.ptype is str:
                value = cfg.get(name, default=default_value)
            elif self.ptype is bool:
                value = cfg.get_bool(name, default=default_value)
            elif self.ptype is list:
                value = cfg.get_list(name, default=default_value)
            elif self.ptype is dict:
                value = cfg.get_dict(name, default=default_value)
            elif self.ptype is int:
                value = cfg.get_int(name, default=default_value)
            elif self.ptype is tuple:
                value = cfg.get_tuple(name, default=default_value)
            else:
                value = cfg.get(name, default=default_value)

            if self.required is True and value is None:
                raise Exception('Config property: %s is required in config for %s' % (name, str(comp_inst)))

            comp_inst.cfg_vals[self.property_name] = value

        return comp_inst.cfg_vals[self.property_name]


class Component(object):
    """
    Abstract Base class for all Input, Filter and Output Components.

    """

    @Config(ptype=str, default=None, required=False)
    def input_format(self):
        """
        The specific input format if the consumes parameter is a list or the format to be converted to the output_format.
        """
        pass

    @Config(ptype=str, default=None, required=False)
    def output_format(self):
        """
        The specific output format if the produces parameter is a list or the format to which the input format is converted.
        """
        pass

    def __init__(self, configdict, section, consumes=FORMAT.none, produces=FORMAT.none):
        # The raw config values from the cfg file
        self.cfg = ConfigSection(configdict.items(section))

        # The actual typed values as populated within Config Decorator
        self.cfg_vals = dict()
        self.next = None
        self.section = section
        self._max_time = -1
        self._min_time = sys.maxint
        self._total_time = 0
        self._invoke_count = 0

        # First assume single output provided by derived class
        self._output_format = produces

        # We may have a configured output_format: use that value, when multiple formats it should be in that list
        if self.output_format is not None:
            self._output_format = self.output_format
            if type(produces) is list and self._output_format not in produces:
                raise ValueError('Configured output_format %s not in list: %s' % (self._output_format, str(produces)))
        elif type(produces) is list:
            # No output_format configured and a list: use the first as default
            self._output_format = produces[0]

        # First assume single input provided by derived class
        self._input_format = consumes

        # We may have a configured input_format: use that value, when multiple formats it should be in that list
        if self.input_format is not None:
            self._input_format = self.input_format
            if type(consumes) is list and self._input_format not in consumes:
                raise ValueError('Configured input_format %s not in list: %s' % (self._input_format, str(consumes)))
        elif type(consumes) is list:
            # No input_format configured and a list: use the first as default
            self._input_format = consumes[0]

    def add_next(self, next_component):
        self.next = next_component

        if not self.is_compatible():
            raise ValueError(
                'Incompatible components are linked: %s and %s' % (str(self), str(self.next)))

    # Get our id: currently the [section] name
    def get_id(self):
        return self.section

    # Get last Component in Chain
    def get_last(self):
        last = self
        while last.next:
            last = last.next
            if isinstance(last, list):
                last = last[0]
        return last

    # Check our compatibility with the next Component in the Chain
    def is_compatible(self):

        # Ok, nothing next in Chain
        if self.next is None or self._output_format is FORMAT.none or self.next._input_format == FORMAT.any:
            return True

        # return if our Output is compatible with the next Component's Input
        return self._output_format == self.next._input_format

    def __str__(self):
        return "%s: in=%s out=%s" % (str(self.__class__), self._input_format, self._output_format)

    def process(self, packet):
        # Current processor of packet
        packet.component = self

        start_time = self.timer_start()
        self._invoke_count += 1

        # Do something with the data
        result = self.before_invoke(packet)
        if result is False:
            # Component indicates it does not want the chain to proceed
            self.timer_stop(start_time)
            return packet

        # Do component-specific processing, e.g. read or write or filter
        packet = self.invoke(packet)

        result = self.after_invoke(packet)
        if result is False:
            # Component indicates it does not want the chain to proceed
            self.timer_stop(start_time)
            return packet

        self.timer_stop(start_time)

        # If there is a next component, let it process
        if self.next:
            # Hand-over data (line, doc whatever) to the next component
            packet.format = self._output_format
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

        # Simple performance stats in one line (issue #77)
        # Calc average processing time, watch for 0 invoke-case
        avg_time = 0.0
        if self._invoke_count > 0:
            avg_time = self._total_time / self._invoke_count

        log.info("%s invokes=%d time(total, min, max, avg) = %.3f %.3f %.3f %.3f" %
                 (self.__class__.__name__, self._invoke_count,
                  self._total_time, self._min_time, self._max_time,
                  avg_time))

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

    def timer_start(self):
        return time()

    def timer_stop(self, start_time):
        """
        Collect and calculate per-Component performance timing stats.
        :param start_time:
        :return:
        """
        delta_time = time() - start_time

        # Calc timing stats for Component invocation
        self._total_time += delta_time

        if delta_time > self._max_time:
            self._max_time = delta_time

        if delta_time < self._min_time and '%.3f' % delta_time != '0.000':
            self._min_time = delta_time
