#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2013 Red Hat, Inc.
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

import gettext
_ = lambda m: gettext.dgettext(message=m, domain='ovirt-engine-setup')

from otopi import util
from ovirt_engine_setup import constants as osetupcons


@util.export
class Stages(object):
    CONFIG_STORAGE = 'ovirtlivesetup.core.core.configstorage'
    COPY_ISO = 'ovirtlivesetup.core.copy.iso'
    CREATE_VM = 'ovirtlivesetup.core.create.vm'
    INIT = 'ovirtlivesetup.core.init'


@util.export
@util.codegen
@osetupcons.osetupattrsclass
class CoreEnv(object):
    ENABLE = 'OVESETUP_OVIRTLIVE/enable'

    CONFIGURE = 'OVESETUP_OL/configure'
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

    STORAGE_DOMAIN_NAME = 'OVESETUP_AIO/storageDomainName'


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
