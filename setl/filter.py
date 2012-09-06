from component import Component

# Base class: Filter
class Filter(Component):
    # Constructor
    def __init__(self, configdict, section):
        Component.__init__(self, configdict, section)

    def invoke(self, packet):
        return packet

