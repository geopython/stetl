#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Executes the given command and returns the captured output.
#
# Author: Frank Steggink
#
import subprocess
import os
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('execfilter')


class ExecFilter(Filter):
    """
    Executes any command (abstract base class).
    """

    def __init__(self, configdict, section, consumes, produces):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        return packet

    def execute_cmd(self, cmd):
        use_shell = True
        if os.name == 'nt':
            use_shell = False

        log.info("executing cmd=%s" % cmd)
        result = subprocess.check_output(cmd, shell=use_shell)
        log.info("execute done")
        return result


class CommandExecFilter(ExecFilter):
    """
    Executes an arbitrary command and captures the output

    consumes=FORMAT.string, produces=FORMAT.string
    """

    def __init__(self, configdict, section):
        ExecFilter.__init__(self, configdict, section, consumes=FORMAT.string, produces=FORMAT.string)

    def invoke(self, packet):
        if packet.data is not None:
            packet.data = self.execute_cmd(packet.data)

        return packet
