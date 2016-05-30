#!/usr/bin/python

import sys
sys.path.append('/usr/share/vdsm/')
from vdsm.network import api
import logging

FORMAT = '%(asctime)-15s::%(message)s'
logging.basicConfig(
    filename='/var/log/vdsm/setup-vdsm-net.log',
    format=FORMAT,
    level=logging.DEBUG
)

NOCHK = {'connectivityCheck': False}
NET = 'ovirtmgmt'
NIC = 'dummy0'

res = api.setupNetworks(
    {
        NET: {
            'nic': NIC,
            'ipaddr': '10.0.0.1',
            'netmask': '255.255.255.0',
            'gateway': '10.0.0.1'
        }
    },
    {},
    NOCHK
)
logging.debug('setupNetworks: %s', res)

res = api.setSafeNetworkConfig()
logging.debug('setSafeNetworkConfig: %s', res)
