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
VDSM configuration plugin.
"""

import distutils.version
import gettext
import time

from otopi import plugin, util

from vdsm import dsaversion

from ovirt_engine_setup import config as osetupconfig
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine import vdcoption
from ovirt_engine_setup.engine_common import constants as oengcommcons

from ovirt_engine_setup.ovirt_live import constants as oliveconst


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-live')


@util.export
class Plugin(plugin.PluginBase):
    """
    VDSM configuration plugin.
    """

    ENGINE_RETRIES = 60
    ENGINE_DELAY = 5
    VDSM_RETRIES = 600
    VDSM_DELAY = 1

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._enabled = False

    def _waitVDSMHostUp(self, engine_api, host):
        self.logger.info(_(
            'Waiting for VDSM host to become operational. '
            'This may take several minutes...'
        ))
        tries = self.VDSM_RETRIES
        isUp = False
        while not isUp and tries > 0:
            tries -= 1
            try:
                state = engine_api.hosts.get(host).status.state
            except Exception as exc:
                # sadly all ovirtsdk errors inherit only from Exception
                self.logger.debug(
                    'Error fetching host state: {error}'.format(
                        error=str(exc),
                    )
                )
                state = ''
            if 'failed' in state:
                self.logger.error(_(
                    'The VDSM host was found in a failed state. '
                    'Please check engine and bootstrap installation logs.'
                ))
                tries = -1  # Error state
            elif state == 'up':
                isUp = True
                self.logger.info(_('The VDSM Host is now operational'))
            else:
                self.logger.debug(
                    'VDSM host in {state} state'.format(
                        state=state,
                    )
                )
                if tries % 30 == 0:
                    self.logger.info(_(
                        'Still waiting for VDSM host to become operational...'
                    ))
                time.sleep(self.VDSM_DELAY)
        if not isUp and tries == 0:
            self.logger.error(_(
                'Timed out while waiting for host to start. '
                'Please check the logs.'
            ))
        return isUp

    def _waitEngineUp(self):
        self.logger.debug('Waiting Engine API response')

        tries = self.ENGINE_RETRIES
        isUp = False
        sdk = None
        while not isUp and tries > 0:
            tries -= 1
            try:
                # Now we are using the SDK to authenticate vs the API
                # to check if the engine is up.
                # Maybe in the future we can just rely on a
                # not authenticated health API URL
                sdk = self._ovirtsdk_api.API(
                    url='https://localhost:{port}/ovirt-engine/api'.format(
                        port=self.environment[
                            oengcommcons.ConfigEnv.PUBLIC_HTTPS_PORT
                        ],
                    ),
                    username=self.environment[
                        oenginecons.ConfigEnv.ADMIN_USER
                    ],
                    password=self.environment[
                        oenginecons.ConfigEnv.ADMIN_PASSWORD
                    ],
                    insecure=True,
                )
                isUp = True
            except self._ovirtsdk_errors.RequestError:
                self.logger.debug(
                    'Cannot connect to engine',
                    exc_info=True,
                )
                time.sleep(self.ENGINE_DELAY)
        if not isUp:
            raise RuntimeError(_('Engine unreachable'))
        return sdk

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            oliveconst.CoreEnv.LOCAL_DATA_CENTER,
            oliveconst.Defaults.DEFAULT_LOCAL_DATA_CENTER
        )
        self.environment.setdefault(
            oliveconst.CoreEnv.LOCAL_CLUSTER,
            oliveconst.Defaults.DEFAULT_LOCAL_CLUSTER
        )
        self.environment.setdefault(
            oliveconst.CoreEnv.LOCAL_HOST,
            oliveconst.Defaults.DEFAULT_LOCAL_HOST
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.CONFIGURE
        ],
    )
    def _validation(self):
        import ovirtsdk.api
        import ovirtsdk.xml
        import ovirtsdk.infrastructure.errors
        self._ovirtsdk_api = ovirtsdk.api
        self._ovirtsdk_xml = ovirtsdk.xml
        self._ovirtsdk_errors = ovirtsdk.infrastructure.errors

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.CONFIGURE
        ],
    )
    def _misc(self):
        self.environment[oengcommcons.ApacheEnv.NEED_RESTART] = True

    def _getSupportedClusterLevels(self):
        vSupportedClusterLevels = []
        raw_version_revision = ''
        vSupportedClusterLevels = dsaversion.version_info['clusterLevels']
        raw_version_revision = dsaversion.raw_version_revision
        return vSupportedClusterLevels, raw_version_revision

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        name=oliveconst.Stages.AIO_CONFIG_VDSM,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.CONFIGURE
        ],
        after=(
            oliveconst.Stages.AIO_CONFIG_STORAGE,
            oliveconst.Stages.AIO_CONFIG_SSH,
            oengcommcons.Stages.CORE_ENGINE_START,
            oengcommcons.Stages.APACHE_RESTART,
        ),
    )
    def _closeup(self):
        self.logger.debug('Connecting to the Engine')
        engine_api = self._waitEngineUp()

        eSupportedClusterLevels = vdcoption.VdcOption(
            statement=self.environment[
                oenginecons.EngineDBEnv.STATEMENT
            ]
        ).getVdcOption(
            name='SupportedClusterLevels'
        )
        self.logger.debug(
            'engine SupportedClusterLevels [{levels}], '
            'PACKAGE_VERSION [{pv}],'.format(
                levels=eSupportedClusterLevels,
                pv=osetupconfig.PACKAGE_VERSION,
            )
        )

        vSupportedClusterLevels, raw_version_revision = \
            self._getSupportedClusterLevels()

        self.logger.debug(
            'VDSM SupportedClusterLevels [{levels}], '
            'VDSM VERSION [{rv}],'.format(
                levels=vSupportedClusterLevels,
                rv=raw_version_revision,
            )
        )

        try:
            v = max(
                distutils.version.LooseVersion(vs).version
                for vs in (
                    set(eSupportedClusterLevels.split(',')) &
                    set(vSupportedClusterLevels)
                )
            )
        except ValueError:
            self.logger.debug('exception', exc_info=True)
            raise RuntimeError(_(
                'Failed to find a ClusterLevel supported '
                'by both engine and VDSM'
            ))
        engine_version = self._ovirtsdk_xml.params.Version(
            major=v[0],
            minor=v[1],
        )

        self.logger.debug('Creating the local data center')
        engine_api.datacenters.add(
            self._ovirtsdk_xml.params.DataCenter(
                name=self.environment[oliveconst.CoreEnv.LOCAL_DATA_CENTER],
                local=True,
                version=engine_version,
            )
        )

        self.logger.debug(
            'Creating the local cluster into the local data center'
        )
        engine_api.clusters.add(
            self._ovirtsdk_xml.params.Cluster(
                name=self.environment[oliveconst.CoreEnv.LOCAL_CLUSTER],
                cpu=self._ovirtsdk_xml.params.CPU(
                    id=self.environment[oliveconst.CoreEnv.VDSM_CPU]
                ),
                data_center=self._ovirtsdk_xml.params.DataCenter(
                    name=self.environment[oliveconst.CoreEnv.LOCAL_DATA_CENTER]
                ),
                version=engine_version
            )
        )

        self.logger.debug('Adding the local host to the local cluster')
        # At this stage sshd is already running
        engine_api.hosts.add(
            self._ovirtsdk_xml.params.Host(
                name=self.environment[oliveconst.CoreEnv.LOCAL_HOST],
                address=self.environment[osetupcons.ConfigEnv.FQDN],
                reboot_after_installation=False,
                override_iptables=False,
                cluster=self._ovirtsdk_xml.params.Cluster(
                    name=self.environment[oliveconst.CoreEnv.LOCAL_CLUSTER]
                ),
                ssh=self._ovirtsdk_xml.params.SSH(
                    authentication_method='publickey',
                    port=self.environment[oliveconst.CoreEnv.SSHD_PORT],
                ),
            )
        )
        if not self._waitVDSMHostUp(
            engine_api=engine_api,
            host=self.environment[oliveconst.CoreEnv.LOCAL_HOST],
        ):
            self.logger.warning(_(
                'Local storage domain not added because '
                'the VDSM host was not up. Please add it manually.'
            ))
        else:
            self.logger.debug('Adding local storage domain')
            storage = self._ovirtsdk_xml.params.Storage(
                path=self.environment[
                    oliveconst.CoreEnv.STORAGE_DOMAIN_DIR
                ].rstrip('/'),
            )
            storage.set_type('localfs')

            storage_domain = self._ovirtsdk_xml.params.StorageDomain(
                name=self.environment[oliveconst.CoreEnv.STORAGE_DOMAIN_NAME],
                storage_format='v3',
                host=self._ovirtsdk_xml.params.Host(
                    name=self.environment[oliveconst.CoreEnv.LOCAL_HOST],
                ),
                storage=storage
            )
            storage_domain.set_type('data')
            engine_api.storagedomains.add(storage_domain)


# vim: expandtab tabstop=4 shiftwidth=4
