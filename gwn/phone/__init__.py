"""
liblinphone based sip phone service with python-tk front end.

DBus Service
------------

:Bus:
    ``session``
:Busname:
    ``com.getwellnetwork.plc.gwnsip1``
"""

__title__ = 'gwn.phone'
__version__ = '0.0.1'
__author__ = 'GetWellNetwork'
__author_email__ = 'plc-dev@getwellnetwork.com'
__copyright__ = 'Copyright 2017 GetWellNetwork, Inc., BSD copyright and disclaimer apply'
__description__ = 'liblinphone based sip phone service with python-tk front end'
__namespace__ = 'gwn'

BUSNAME = 'com.getwellnetwork.plc.gwnsip1'
OBJECTPATH = '/com/getwellnetwork/plc/gwnsip1/GwnSip'
INTERFACE = 'com.getwellnetwork.plc.gwnsip1.GwnSip1'
SUPPORT_OBJECTPATH = '/com/getwellnetwork/plc/gwnsip1/Support'
SUPPORT_INTERFACE = 'com.getwellnetwork.plc.Support1'

