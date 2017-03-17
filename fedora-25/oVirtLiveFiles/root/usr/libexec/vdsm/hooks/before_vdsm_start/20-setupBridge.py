#!/usr/bin/python

import logging
import sys

from vdsm.network import api

sys.path.append('/usr/share/vdsm/')

FORMAT = '%(asctime)-15s::%(message)s'
logging.basicConfig(
    filename='/var/log/vdsm/setup-vdsm-net.log',
    format=FORMAT,
    level=logging.DEBUG
)

NOCHK = {'connectivityCheck': False}
NET = 'ovirtmgmt'
NIC = 'dummy_0'

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
