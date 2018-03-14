from dbus.mainloop.glib import DBusGMainLoop
from .support_service import SupportService
from gi.repository.GObject import MainLoop
from .sip_service import GwnPhone



def main():
    DBusGMainLoop( set_as_default = True )
    service = GwnPhone()
    support_service = SupportService( service )

    try:
        MainLoop().run()
    except KeyboardInterrupt:
        pass
