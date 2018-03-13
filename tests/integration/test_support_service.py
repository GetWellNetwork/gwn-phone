
import dbus
import pytest



@pytest.fixture( scope = 'session' )
def support_service():
    obj = dbus.SystemBus().get_object( 'com.getwellnetwork.plc.gwnsip1', '/com/getwellnetwork/plc/gwnsip1/Support' )
    iface = dbus.Interface( obj, dbus_interface = 'com.getwellnetwork.plc.Support1' )
    return iface



def test_log_level( support_service ):
    support_service.SetLogLevel( 'debug' )

    support_service.SetLogLevel( 'info' )
    assert 'info' == support_service.GetLogLevel()

    support_service.SetLogLevel( 'debug' )
    assert 'debug' == support_service.GetLogLevel()

    support_service.SetLogLevel( 'warning' )
    assert 'warning' == support_service.GetLogLevel()

