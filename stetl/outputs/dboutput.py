# -*- coding: utf-8 -*-
#
# Output classes for ETL, databases.
#
# Author: Just van den Broecke
#
from stetl.output import Output
from stetl.util import Util
from stetl.packet import FORMAT
from stetl.postgis import PostGIS

log = Util.get_log('dboutput')


class DbOutput(Output):
    """
    Output to any database (abstract base class).
    """

    def __init__(self, configdict, section, consumes):
        Output.__init__(self, configdict, section, consumes)

    def write(self, packet):
        return packet

class PostgresDbOutput(DbOutput):
    """
    Output to PostgreSQL database.
    Input is an SQL string.
    Output by executing input SQL string.

    consumes=FORMAT.string
    """

    def __init__(self, configdict, section):
        DbOutput.__init__(self, configdict, section, consumes=FORMAT.string)

    def write(self, packet):
        if packet.data is None:
            return packet

        log.info('executing SQL')
        db = PostGIS(self.cfg.get_dict())
        rowcount = db.tx_execute(packet.data)
        log.info('executed SQL, rowcount=%d' % rowcount)
        return packet

