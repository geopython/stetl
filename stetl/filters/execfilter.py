#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Executes the given command and returns the captured output.
#
# Author: Frank Steggink
#
import subprocess
import os
from stetl.component import Config
from stetl.filter import Filter
from stetl.util import Util
from stetl.packet import FORMAT

log = Util.get_log('execfilter')


class ExecFilter(Filter):
    """
    Executes any command (abstract base class).
    """

    @Config(ptype=str, default='', required=False)
    def env_args(self):
        """
        Provides of list of environment variables which will be used when executing the given command.

        Example: env_args = pgpassword=postgres othersetting=value~with~spaces
        """
        pass

    @Config(ptype=str, default='=', required=False)
    def env_separator(self):
        """
        Provides the separator to split the environment variable names from their values.
        """
        pass

    def __init__(self, configdict, section, consumes, produces):
        Filter.__init__(self, configdict, section, consumes, produces)

    def invoke(self, packet):
        return packet

    def execute_cmd(self, cmd):
        env_vars = Util.string_to_dict(self.env_args, self.env_separator)
        old_environ = os.environ.copy()

        try:
            os.environ.update(env_vars)
            log.info("executing cmd=%s" % cmd)
            result = subprocess.check_output(cmd, shell=True)
            log.info("execute done")
            return result
        finally:
            os.environ = old_environ


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
