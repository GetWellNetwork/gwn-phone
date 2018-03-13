
import dbus
import os
import pwd
import pytest
import time



@pytest.fixture( scope = 'session' )
def foo_service():
    obj = dbus.SessionBus().get_object( 'com.getwellnetwork.plc.gwnsip1', '/com/getwellnetwork/plc/gwnsip1/GwnSip' )
    iface = dbus.Interface( obj, dbus_interface = 'com.getwellnetwork.plc.gwnsip1.GwnSip1' )
    return iface



def test_foo( foo_service ):
    assert foo_service.Foo() == 42



def test_runs_as_patient():
    assert pwd.getpwuid( os.getuid() ).pw_name == 'patient'

