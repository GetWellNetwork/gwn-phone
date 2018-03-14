"""
Provides DBus services for Support and Health monitoring.

:Bus:
    ``system``
:Busname:
    ``com.getwellnetwork.plc.gwnphone1``
:ObjectPath:
    ``/com/getwellnetwork/plc/gwnphone1/Support``
:Interface:
    ``com.getwellnetwork.plc.Support1``
"""

import dbus
import json
import logging
import dbus.service
from . import BUSNAME, SUPPORT_OBJECTPATH, SUPPORT_INTERFACE



class SupportService( dbus.service.Object ):

    def __init__( self, phone_service ):
        bus_name = dbus.service.BusName( BUSNAME, bus = dbus.SystemBus() )
        super().__init__( bus_name = bus_name, object_path = SUPPORT_OBJECTPATH )
        self.phone_service = phone_service


    @dbus.service.method( SUPPORT_INTERFACE, out_signature = 's' )
    def GetState( self ):
        """
        Return the current runtime state of the service.

        Returns:
            str: json encoded, free-form-ish dictionary of runtime state information
        """
        return json.dumps( self.phone_service._dump_state() )


    @dbus.service.method( SUPPORT_INTERFACE, out_signature = 's' )
    def GetLogLevel( self ):
        """
        Return the current log level.

        Returns:
            str: a logging level, e.g. ``"debug"``, ``"info"``, ``"warning"``, etc.
        """
        ret = 'notset'
        lvl = self.phone_service.logger.level
        if lvl == logging.DEBUG:
            ret = 'debug'
        elif lvl == logging.INFO:
            ret = 'info'
        elif lvl == logging.WARNING:
            ret = 'warning'
        elif lvl == logging.ERROR:
            ret = 'error'
        elif lvl == logging.CRITICAL:
            ret = 'critical'
        return ret


    @dbus.service.method( SUPPORT_INTERFACE, in_signature = 's' )
    def SetLogLevel( self, level ):
        """
        Set the effective log level.

        Args:
            level (str): the desired log level, e.g. ``"debug"``, ``"warning"``

        Raises:
            ValueError: if ``level`` is not a valid log level name

        Notes:

            * This method changes the log level for the duration of this runtime. The log level will
              return to the default if this process is restarted.
        """
        val = None
        level = str( level )
        if lvl == 'debug':
            val = logging.DEBUG
        elif lvl == 'info':
            val = logging.INFO
        elif lvl == 'warning':
            val = logging.WARNING
        elif lvl == 'error':
            val = logging.ERROR
        elif lvl == 'critical':
            val = logger.CRITICAL
        else:
            raise ValueError( 'unknown log level: {!r}'.format( level ) )
        if val:
            self.phone_service.logger.setLevel( val )
