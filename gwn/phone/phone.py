"""
liblinphone based sip phone service

:Bus:
    ``session``
:Busname:
    ``com.getwellnetwork.plc.gwnphone1``
:ObjectPath:
    ``/com/getwellnetwork/plc/gwnphone1/GwnPhone``
:Interface:
    ``com.getwellnetwork.plc.gwnphone1.GwnPhone1``

Examples:

    ::

        from gwn.helpers.dbus import find_gwn_service

        gwnphone_service = find_gwn_service(
            bus = 'session',
            bus_name = 'gwnphone1',
            object_path = 'gwnphone1/GwnPhone',
            interface = 'gwnphone1.GwnPhone1'
        )
"""



from . import BUSNAME, OBJECTPATH, INTERFACE
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject as gobject
from gi.repository.GObject import MainLoop
from systemd.journal import JournalHandler
import dbus.service
import linphone
import logging
import sys



def log_handler( level, msg ):
    method = getattr( logging, 'debug' )
    method( msg )



def add_non_none_to_dict( dct, key, value ):
    if value != None:
        dct[key] = value
    return dct



class GwnPhone( dbus.service.Object ):

    def __init__( self ):
        bus_name = dbus.service.BusName( BUSNAME, bus = dbus.SessionBus() )
        dbus.service.Object.__init__( self, bus_name = bus_name, object_path = OBJECTPATH )
        self.logger = logging.getLogger()
        handler = JournalHandler( SYSLOG_IDENTIFIER = 'gwnphone' )
        self.logger.addHandler( handler )
        self.logger.setLevel( logging.INFO )
        self.logger.info( 'connected to session bus' )
        self.settings_service = dbus.SystemBus().get_object(
            'com.getwellnetwork.plc.clerk1',
            '/com/getwellnetwork/plc/clerk1/Settings'
        )
        try:
            self.rdp_service = dbus.SessionBus().get_object(
                'com.getwellnetwork.plc.rdp1',
                '/com/getwellnetwork/plc/rdp1/Rdp'
            )
            dbus.SessionBus().add_signal_receiver(
                self._ext_dnd,
                signal_name = 'Launched',
                member_keyword = 'sig_name',
                dbus_interface = 'com.getwellnetwork.plc.rdp1.Rdp1'
            )
            dbus.SessionBus().add_signal_receiver(
                self._ext_dnd,
                signal_name = 'Destroyed',
                member_keyword = 'sig_name',
                dbus_interface = 'com.getwellnetwork.plc.rdp1.Rdp1'
            )
        except Exception as e:
            self.rdp_service = None
            self.logger.error( 'no rdp service available' )
        self.conf_path = {}
        self.conf_path['port'] = 'config.phone.port'
        self.conf_path['server'] = 'config.phone.server'
        self.conf_path['phone_number'] = 'config.location.phone_number'
        self.conf_path['username'] = 'config.location.location_attributes.username'
        self.conf_path['password'] = 'config.location.location_attributes.password'
        try:
            phone_conf = self.settings_service.get_dbus_method(
                'ReadAll',
                'com.getwellnetwork.plc.clerk1.Settings1'
            )( 'config.phone' )
            location_conf = self.settings_service.get_dbus_method(
                'ReadAll',
                'com.getwellnetwork.plc.clerk1.Settings1'
            )( 'config.location' )
            self.port = phone_conf[self.conf_path['port']]
            self.server = phone_conf[self.conf_path['server']]
            self.phone_number = location_conf[self.conf_path['phone_number']]
            self.username = location_conf.get( self.conf_path['username'] )
            if not self.username:
                self.username = self.phone_number[-4:]
            self.password = location_conf.get( self.conf_path['password'] )
            if not self.password:
                self.password = '1234'
        except Exception as e:
            self.logger.error( 'bad config, bailing out now: {}'.format( e ) )
            sys.exit( 0 )
        dbus.SessionBus().add_signal_receiver(
                self._on_settings_changed,
                signal_name = 'Changed',
                member_keyword = 'sig_name',
                dbus_interface = 'com.getwellnetwork.plc.clerk1.Settings1'
        )
        self.dial_tone_timer = None
        self.factory = linphone.Factory.get()
        linphone.set_log_handler( log_handler )
        self.core = self.factory.create_core( None, None, None )
        self.callbacks = self.factory.create_core_cbs()
        self.callbacks.call_state_changed = self._call_state_changed
        self.callbacks.global_state_changed = self._global_state_changed
        self.callbacks.registration_state_changed = self._registration_state_changed
        self.core.add_callbacks( self.callbacks )
        auth_info = self.core.create_auth_info(
            self.username, None, self.password, None, None, self.server )
        self.core.add_auth_info( auth_info )
        self.proxy_cfg = self.core.create_proxy_config()
        self.proxy_cfg.identity_address = linphone.Address.new(
            'sip:{}@{}'.format( self.username, self.server ) )
        self.proxy_cfg.identity_address.port = int( self.port )
        self.proxy_cfg.server_addr = 'sip:{}:{}'.format( self.server, self.port )
        self.sip_proxy = '{}:{}'.format( self.server, self.port )
        self.proxy_cfg.register_enabled = True
        self.core.add_proxy_config( self.proxy_cfg )
        self.core.ring_during_incoming_early_media = False
        self.core.remote_ringback_tone = None
        self.core.ringback = '/usr/share/gwn-phone/sound/ringback.wav'
        self.dial_tone = '/usr/share/gwn-phone/sound/dial_tone.wav'
        self.registration_state = linphone.RegistrationState.None
        self.core.ring = None
        self.core.terminate_all_calls()
        self.current_call = None
        self.core.max_calls = 1
        self.dnd = False
        self.dnd_ext = False
        self.core.use_info_for_dtmf = False
        self.core.use_rfc2833_for_dtmf = False
        sound_dev = self.core.sound_devices[0]
        self.core.playback_device = sound_dev
        self.core.capture_device  = sound_dev
        self.core.ringer_device   = sound_dev
        self.core.mic_enabled     = True
        self.iterate_timer = gobject.timeout_add( 100, self._iterate )


    def _iterate( self ):
        self.core.iterate()
        return True


    def _on_settings_changed( self, reason, entries ):
        try:
            if len( entries ) and reason == 'write':
                for entry in entries:
                    for path in self.conf_path:
                        if self.conf_path[path] == entry:
                            if path == 'port':
                                self.port = entries[entry]
                            elif path == 'server':
                                self.server = entries[entry]
                            elif path == 'phone_number':
                                self.phone_number = entries[entry]
                            elif path == 'username':
                                self.username = entries[entry]
                            elif path == 'password':
                                self.password = entries[entry]
                            self.logger.info( '{} updated: {}'.format( path, entries[entry] ) )
        except TypeError as e:
            pass
        except Exception as e:
            self.logger.error( 'exception in _on_settings_changed: {}'.format( e ) )


    def _global_state_changed( self, *args, **kwargs ):
        self.logger.debug( 'global_state_changed: {} {}'.format( args, kwargs ) )


    def _registration_state_changed( self, core, call, state, message ):
        self.logger.debug( 'registration_state_changed: {} {}'.format( state, message ) )
        self.registration_state = state
        if state == linphone.RegistrationState.Cleared:
            gobject.source_remove( self.iterate_timer )
            self.logger.info( 'unregistered, exiting' )
            sys.exit( 0 )


    def _call_state_changed( self, core, call, state, message ):
        call_info = {}
        add_non_none_to_dict( call_info, 'state', state )
        add_non_none_to_dict( call_info, 'message', message )
        add_non_none_to_dict( call_info, 'duration', call.duration )
        add_non_none_to_dict( call_info, 'term_reason', call.reason )
        add_non_none_to_dict( call_info, 'remote_address', call.remote_address_as_string )
        add_non_none_to_dict( call_info, 'remote_contact', call.remote_contact )
        add_non_none_to_dict( call_info, 'remote_user_agent', call.remote_user_agent )
        add_non_none_to_dict( call_info, 'error_reason', call.error_info.reason )
        add_non_none_to_dict( call_info, 'error_phrase', call.error_info.phrase )
        self.logger.debug( 'call state changed : {}'.format( call_info ) )
        if state == linphone.CallState.IncomingReceived:
            if self.dnd or self.dnd_ext:
                self.core.decline_call( call, linphone.Reason.DoNotDisturb )
                if self.dial_tone_timer:
                    self._restart_dial_tone()
                return
        elif state == linphone.CallState.Connected:
            self.current_call = call
        elif state == linphone.CallState.End:
            self.current_call = None
        if self.dial_tone_timer:
            self._restart_dial_tone()
        self.CallStateChange( call_info )


    def _ext_dnd( self, *args, **kwargs ):
        if kwargs:
            sig = kwargs.get( 'sig_name' )
            if sig == 'Launched':
                self.dnd_ext = True
                if not self.dnd:
                    self.DndStateChange( True )
            elif sig == 'Destroyed':
                self.dnd_ext = False
                if not self.dnd:
                    self.DndStateChange( False )


    def _restart_dial_tone( self ):
        self.core.play_local( self.dial_tone )
        return True


    def _stop_dial_tone( self ):
        if self.dial_tone_timer:
            gobject.source_remove( self.dial_tone_timer )
            self.dial_tone_timer = None
        # attempting to play an invalid file appears to be the fastest way to stop
        # the currently playing file
        self.core.play_local( '' )


    def _dump_state( self ):
        state = {}
        state['port'] = self.port
        state['server'] = self.server
        state['username'] = self.username
        state['password'] = self.password
        state['phone_number'] = self.phone_number
        state['in_call'] = False
        if self.current_call != None:
            state['in_call'] = True
        state['registration'] = 'none'
        if self.registration_state == linphone.RegistrationState.Progress:
            state['registration'] = 'in_progress'
        elif self.registration_state == linphone.RegistrationState.Ok:
            state['registration'] = 'successful'
        elif self.registration_state == linphone.RegistrationState.Cleared:
            state['registration'] = 'unregistered'
        elif self.registration_state == linphone.RegistrationState.Failed:
            state['registration'] = 'failed'
        return state


    @dbus.service.signal( INTERFACE, signature = 'a{sv}' )
    def CallStateChange( self, call_info ):
        self.logger.debug( 'emitting signal: CallStateChange' )


    @dbus.service.signal( INTERFACE, signature = 'b' )
    def DndStateChange( self, dnd_state ):
        self.logger.debug( 'emitting signal: DndStateChange {}'.format( dnd_state ) )


    @dbus.service.method( INTERFACE, out_signature = 'b' )
    def GetDndState( self ):
        return self.dnd or self.dnd_ext


    @dbus.service.method( INTERFACE, in_signature = 'b' )
    def SetDndState( self, dnd_state ):
        if self.dnd != dnd_state:
            self.dnd = dnd_state
            self.DndStateChange( self.dnd )


    @dbus.service.method( INTERFACE, in_signature = 's' )
    def PlayDtmf( self, dtmf ):
        if self.dial_tone_timer:
            self._stop_dial_tone()
        call = self.core.current_call
        if call:
            ret = call.send_dtmf( ord( dtmf ) )
        self.core.play_dtmf( ord( dtmf ), -1 )


    @dbus.service.method( INTERFACE )
    def StopDtmf( self ):
        self.core.stop_dtmf()


    @dbus.service.method( INTERFACE )
    def PlayDialTone( self ):
        if self.dial_tone_timer:
            self._stop_dial_tone()
        self.core.play_local( self.dial_tone )
        self.dial_tone_timer = gobject.timeout_add( 20000, self._restart_dial_tone )


    @dbus.service.method( INTERFACE )
    def StopDialTone( self ):
        self._stop_dial_tone()


    @dbus.service.method( INTERFACE )
    def AnswerCall( self ):
        if self.dial_tone_timer:
            self._stop_dial_tone()
        calls = self.core.calls
        if calls:
            call = calls[0]
            self.logger.debug( 'answering call from: {}'.format( call.remote_address_as_string ) )
            self.core.accept_call( call )
            self.current_call = call


    @dbus.service.method( INTERFACE, in_signature = 'i' )
    def EndCall( self, reason ):
        call = self.core.current_call
        if call and reason != linphone.Reason._None and call.state == linphone.CallState.IncomingReceived:
            self.logger.debug( 'declining incoming call' )
            self.core.decline_call( call, reason )
            return
        self.logger.debug( 'terminating any current call' )
        self.core.terminate_all_calls()


    @dbus.service.method( INTERFACE, in_signature = 's' )
    def PlaceCall( self, out_number ):
        if self.dial_tone_timer:
            self._stop_dial_tone()
        call_string = ( 'sip:{}@{}'.format( out_number, self.sip_proxy ) )
        self.logger.debug( 'placing call to: {}'.format( call_string ) )
        self.core.invite( call_string )
