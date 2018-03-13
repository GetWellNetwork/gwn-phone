
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository.GObject import MainLoop

from gwn.helpers.logger import logger

from .foo_service import FooService
from .support_service import SupportService



def main():
    """The main entry point for the systemd service."""
    DBusGMainLoop( set_as_default = True )

    service = FooService()
    support_service = SupportService()

    try:
        logger.debug( 'entering main loop' )
        MainLoop().run()
    except KeyboardInterrupt:
        pass

