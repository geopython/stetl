#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Component base class for ETL.
#
# Author: Just van den Broecke
#
from util import ConfigSection


# Base class for all Input, Transformer, Outputs
class Component:
    def __init__(self, configdict, section):
        self.configdict = configdict
        self.cfg = ConfigSection(configdict.items(section))

    def invoke(self, doc=None):
        return None

