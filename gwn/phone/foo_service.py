"""
Provides DBus services for the ultimate question of life, the universe, and everything.

:Bus:
    ``session``
:Busname:
    ``com.getwellnetwork.plc.gwnsip1``
:ObjectPath:
    ``/com/getwellnetwork/plc/gwnsip1/GwnSip``
:Interface:
    ``com.getwellnetwork.plc.gwnsip1.GwnSip1``

Examples:

    ::

        from gwn.helpers.dbus import find_gwn_service

        gwnsip_service = find_gwn_service(
            bus = 'session',
            bus_name = 'gwnsip1',
            object_path = 'gwnsip1/GwnSip',
            interface = 'gwnsip1.GwnSip1'
        )
"""

import dbus.service

from gwn.helpers.logger import logger

from . import BUSNAME, OBJECTPATH, INTERFACE
from .foo import foo



class FooService( dbus.service.Object ):

    def __init__( self ):
        bus_name = dbus.service.BusName( BUSNAME, bus = dbus.SessionBus() )
        super().__init__( bus_name = bus_name, object_path = OBJECTPATH )
        logger.info( 'connected to session bus' )


    @dbus.service.method( INTERFACE, out_signature = 'i' )
    def Foo( self ):
        """
        Returns the answer to the ultimate question of life, the universe, and everything.

        :DBus Signature:
            ``i: outbound``

        Returns:
            int
        """
        return foo()

