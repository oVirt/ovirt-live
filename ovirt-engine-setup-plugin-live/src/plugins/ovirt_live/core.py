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


"""
oVirt Live plugin.
"""

import glob
import os
import shutil
import time

from otopi import plugin
from otopi import util

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup import util as osetuputil
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcon

from ovirt_engine_setup.ovirt_live import constants as oliveconst


@util.export
class Plugin(plugin.PluginBase):
    """
    oVirt Live plugin.
    """

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._enabled = True

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            oliveconst.CoreEnv.ENABLE
        )
        self.environment.setdefault(
            oliveconst.IsoEnv.ISO_NAME,
            oliveconst.Defaults.DEFAULT_ISO_NAME
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.ENABLE
        ],
    )
    def _setup(self):
        self._enabled = True

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
    )
    def _validation(self):
        import ovirtsdk.api
        import ovirtsdk.xml
        self._ovirtsdk_api = ovirtsdk.api
        self._ovirtsdk_xml = ovirtsdk.xml

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.INIT,
        before=(
            oliveconst.Stages.CONFIG_STORAGE,
        ),
        after=(
            oenginecons.Stages.AIO_CONFIG_VDSM,
        ),
    )
    def _initapi(self):
        self._engine_api = self._ovirtsdk_api.API(
            url='https://{fqdn}:{port}/api'.format(
                fqdn=self.environment[osetupcons.ConfigEnv.FQDN],
                port=self.environment[oengcommcon.ConfigEnv.PUBLIC_HTTPS_PORT],
            ),
            username='{user}'.format(
                user=self.environment[oenginecons.ConfigEnv.ADMIN_USER],
            ),
            password=self.environment[oenginecons.ConfigEnv.ADMIN_PASSWORD],
            ca_file=oenginecons.FileLocations.OVIRT_ENGINE_PKI_ENGINE_CA_CERT,
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.CONFIG_STORAGE,
        after=(
            oliveconst.Stages.INIT,
        ),
    )
    def _createstorage(self):
        self.logger.debug('Attaching iso domain')
        time.sleep(10)
        self._engine_api.datacenters.get(
            self.environment[
                oliveconst.CoreEnv.LOCAL_DATA_CENTER
            ]
        ).storagedomains.add(
            self._engine_api.storagedomains.get(
                self.environment[
                    oliveconst.IsoEnv.ISO_NAME
                ]
            )
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            self._enabled and
            self.environment[oenginecons.ConfigEnv.ISO_DOMAIN_EXISTS]
        ),
        name=oliveconst.Stages.COPY_ISO,
        before=(
            oliveconst.Stages.CREATE_VM,
        ),
        after=(
            oenginecons.Stages.CONFIG_ISO_DOMAIN_AVAILABLE,
        ),
    )
    def _copyiso(self):
        self.logger.debug('Copying Iso Files')
        targetPath = os.path.join(
            self.environment[
                oenginecons.ConfigEnv.ISO_DOMAIN_NFS_MOUNT_POINT
            ],
            self.environment[
                oenginecons.ConfigEnv.ISO_DOMAIN_SD_UUID
            ],
            'images',
            oenginecons.Const.ISO_DOMAIN_IMAGE_UID
        )
        self.logger.debug('target path' + targetPath)
        # FIXME don't hardcode paths
        for filename in glob.glob('/home/liveuser/oVirtLiveFiles/iso/*.iso'):
            self.logger.debug(filename)
            shutil.move(filename, targetPath)
            os.chown(
                os.path.join(targetPath, os.path.basename(filename)),
                osetuputil.getUid(
                    oengcommcon.Defaults.DEFAULT_SYSTEM_USER_VDSM
                ),
                osetuputil.getGid(
                    oengcommcon.Defaults.DEFAULT_SYSTEM_GROUP_KVM
                )
            )

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.CREATE_VM,
        after=(
            oliveconst.Stages.INIT,
        ),
    )
    def _createvm(self):
        params = self._ovirtsdk_xml.params
        MB = 1024 * 1024
        GB = 1024 * MB

        vm = self._engine_api.vms.add(
            params.VM(
                name='local_vm',
                memory=1 * GB,
                os=params.OperatingSystem(
                    type_='unassigned',
                    boot=(
                        params.Boot(dev='cdrom'),
                        params.Boot(dev='hd'),
                    ),
                ),
                cluster=self._engine_api.clusters.get('local_cluster'),
                template=self._engine_api.templates.get('Blank'),
            ),
        )

        vm.nics.add(
            params.NIC(
                name='eth0',
                network=params.Network(name='ovirtmgmt'),
                interface='virtio',
            ),
        )

        vm.disks.add(
            params.Disk(
                storage_domains=params.StorageDomains(
                    storage_domain=(
                        self._engine_api.storagedomains.get('local_storage'),
                    ),
                ),
                size=6 * GB,
                type_='data',
                interface='virtio',
                format='cow',
                bootable=True,
            ),
        )


# vim: expandtab tabstop=4 shiftwidth=4
