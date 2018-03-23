from dbus.mainloop.glib import DBusGMainLoop
from gi.repository.GObject import MainLoop
from systemd.journal import JournalHandler
import subprocess
import logging
import dbus



class PhoneConfWatcher( object ):

    def __init__( self ):
        self.logger = logging.getLogger()
        handler = JournalHandler( SYSLOG_IDENTIFIER = 'gwn-phone-conf-watch' )
        self.logger.addHandler( handler )
        self.logger.setLevel( logging.INFO )
        self.confs = [
                'config.phone',
                'location.phone_number',
                'location_attributes.password',
                'location_attributes.username'
        ]
        self.settings_service = dbus.SystemBus().get_object(
            'com.getwellnetwork.plc.clerk1',
            '/com/getwellnetwork/plc/clerk1/Settings'
        )
        dbus.SystemBus().add_signal_receiver(
                self._on_settings_changed,
                signal_name = 'Changed',
                dbus_interface = 'com.getwellnetwork.plc.clerk1.Settings1'
        )
        self.logger.info( 'watching for changes to phone config' )


    def _on_settings_changed( self, reason, entries ):
        try:
            if len( entries ):
                for entry in entries:
                    for conf in self.confs:
                        if conf in entry:
                            self.logger.info( 'phone config {} updated: {}'.format( entry, entries[entry] ) )
                            proc_args = ['systemctl', '--user', 'restart', 'gwn-phone.service']
                            try:
                                subprocess.check_call( proc_args )
                            except subprocess.CalledProcessError as e:
                                self.logger.error( 'exception: subprocess error: {}'.format( e ) )
                            return
        except TypeError as e:
            pass
        except Exception as e:
            self.logger.error( 'exception _on_settings_changed: {}'.format( e ) )



def main():
    DBusGMainLoop( set_as_default = True )
    service = PhoneConfWatcher()
    try:
        MainLoop().run()
    except KeyboardInterrupt:
        pass
