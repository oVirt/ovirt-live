#
# ovirt-engine-setup -- oVirt Live
# Copyright (C) 2013-2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""oVirt Live Constants"""


import gettext
import os

from otopi import util
from ovirt_engine_setup import constants as osetupcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-live')


@util.export
class FileLocations(object):
    DATADIR = '/usr/share'
    LOCALSTATEDIR = '/var'

    AIO_VDSM_PATH = os.path.join(
        DATADIR,
        'vdsm',
    )
    AIO_STORAGE_DOMAIN_DEFAULT_DIR = os.path.join(
        LOCALSTATEDIR,
        'lib',
        'images',
    )
    AIO_POST_INSTALL_CONFIG = os.path.join(
        '%s.d' % osetupcons.FileLocations.OVIRT_OVIRT_SETUP_CONFIG_FILE,
        '20-setup-aio.conf'
    )


@util.export
class Stages(object):
    CONFIG_STORAGE = 'ovirtlivesetup.core.core.configstorage'
    COPY_ISO = 'ovirtlivesetup.core.copy.iso'
    CREATE_VM = 'ovirtlivesetup.core.create.vm'
    INIT = 'ovirtlivesetup.core.init'

    AIO_CONFIG_AVAILABLE = 'osetup.aio.config.available'
    AIO_CONFIG_NOT_AVAILABLE = 'osetup.aio.config.not.available'
    AIO_CONFIG_STORAGE = 'osetup.aio.config.storage'
    AIO_CONFIG_SSH = 'osetup.aio.config.ssh'
    AIO_CONFIG_VDSM = 'osetup.aio.config.vdsm'


@util.export
@util.codegen
@osetupcons.osetupattrsclass
class CoreEnv(object):
    ENABLE = 'OVESETUP_AIO/enable'

    @osetupcons.osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Configure VDSM on this host'),
    )
    def CONFIGURE(self):
        return 'OVESETUP_AIO/configure'

    CONTINUE_WITHOUT_AIO = 'OVESETUP_AIO/continueWithoutAIO'

    LOCAL_DATA_CENTER = 'OVESETUP_AIO/localDataCenter'
    LOCAL_CLUSTER = 'OVESETUP_AIO/localCluster'
    LOCAL_HOST = 'OVESETUP_AIO/localHost'
    VDSM_CPU = 'OVESETUP_AIO/vdsmCpu'

    STORAGE_DOMAIN_SD_UUID = 'OVESETUP_AIO/storageDomainSdUuid'
    STORAGE_DOMAIN_DEFAULT_DIR = 'OVESETUP_AIO/storageDomainDefaultDir'

    @osetupcons.osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Local storage domain directory'),
    )
    def STORAGE_DOMAIN_DIR(self):
        return 'OVESETUP_AIO/storageDomainDir'

    @osetupcons.osetupattrs(
        answerfile=True,
        summary=False,
        description=_('Local storage domain name'),
    )
    def STORAGE_DOMAIN_NAME(self):
        return 'OVESETUP_AIO/storageDomainName'

    SUPPORTED = 'OVESETUP_AIO/supported'
    SSHD_PORT = 'OVESETUP_AIO/sshdPort'
    DEFAULT_SSH_PORT = 22


@util.export
@osetupcons.osetupattrsclass
class Defaults(object):
    DEFAULT_LOCAL_DATA_CENTER = 'local_datacenter'
    DEFAULT_LOCAL_CLUSTER = 'local_cluster'
    DEFAULT_LOCAL_HOST = 'local_host'
    DEFAULT_STORAGE_DOMAIN_NAME = 'local_storage'
    DEFAULT_ISO_NAME = 'ISO_DOMAIN'


@util.export
@util.codegen
@osetupcons.osetupattrsclass
class IsoEnv(object):
    ISO_NAME = 'ISO_DOMAIN'


@util.export
@util.codegen
class Const(object):
    MINIMUM_SPACE_STORAGEDOMAIN_MB = 10240


# vim: expandtab tabstop=4 shiftwidth=4
