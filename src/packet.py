#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Unit of data streamed through ETL chain.
#
# Author: Just van den Broecke
#

# Represents units of (any) data and status passed along Chain of Components
class Packet:
    def __init__(self, data=None):
        self.data = data
        self.end_of_stream = False
        self.end_of_doc = False

    def consume(self):
        data = self.data
        self.data = None
        return data

    def is_end_of_stream(self):
        return self.end_of_stream

    def is_end_of_doc(self):
        return self.end_of_doc

    def set_end_of_stream(self, val=True):
        self.end_of_stream = val

    def set_end_of_doc(self, val=True):
        self.end_of_doc = val

