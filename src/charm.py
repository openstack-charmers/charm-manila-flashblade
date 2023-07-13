#! /usr/bin/env python3

# Copyright 2021 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict
from ops_openstack.core import OSBaseCharm
from ops.main import main

from ops.model import (
    ActiveStatus,
    BlockedStatus,
)

from charmhelpers.core.host import (
    lsb_release,
)

from charmhelpers.fetch import (
    apt_install,
    apt_update,
    add_source,
)

import charmhelpers.contrib.openstack.templating as os_templating

from charmhelpers.core.templating import render

import json

import logging

RELATION_NAME = 'manila-plugin'


class ManilaFlashBladePluginCharm(OSBaseCharm):

    PACKAGES = ['purity_fb']

    REQUIRED_RELATIONS = [RELATION_NAME]

    SHARE_DRIVER = \
        'manila.share.drivers.purestorage.flashblade.FlashBladeShareDriver'

    MANDATORY_CONFIG = ['flashblade-mgmt-vip', 'flashblade-data-vip',
                        'flashblade-api']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.framework.observe(
            self.on.config_changed,
            self.on_config)

        self.framework.observe(
            self.on.manila_plugin_relation_changed,
            self.on_manila_plugin)

    def on_config(self, event):
        self.on_manila_plugin(event)
        self._stored.is_started = True
        if self.framework.model.relations.get(RELATION_NAME):
            self.send_backend_config()
        self.unit.status = ActiveStatus('Unit is ready')

    def send_backend_config(self):
        config = dict(self.framework.model.config)
        manila_backends = self.manila_configuration(config)
        for relation in self.framework.model.relations.get(RELATION_NAME):
            relation.data[self.unit]['_name'] = \
                ','.join(manila_backends.keys())
            rendered_config = render(
                source="parts/backends",
                template_loader=os_templating.get_loader(
                    'templates/', "focal"),
                target=None,
                context={'backends': manila_backends})

            relation.data[self.unit]['_configuration_data'] = json.dumps({
                'data': {
                    '/etc/manila/manila.conf': rendered_config
                }
            })

    def on_manila_plugin(self, event):
        self.send_backend_config()

    def manila_configuration(self, config):
        """
        See https://docs.openstack.org/manila/latest/configuration/shared-file-systems/drivers/purestorage-flashblade-driver.html # noqa: E501
        """
        # Return the configuration to be set by the principal.

        backends = OrderedDict()

        backend_names = [config.get('share-backend-name')]

        for backend_name in backend_names:

            backends[backend_name] = [
                ('share_driver', self.SHARE_DRIVER),
                ('share_backend_name', backend_name),

                ('driver_handles_share_servers', 'false'),
            ]

            if config.get('flashblade-mgmt-vip') and config.get('flashblade-data-vip') \
                    and config.get('flashblade-api'):

                backends[backend_name].extend([
                    ('flashblade_api', config.get('flashblade-api')),
                    ('flashblade_mgmt_vip', config.get('flashblade-mgmt-vip')),
                    ('flashblade_data_vip', config.get('flashblade-data-vip')),
                ])

        if not backends:
            self.unit.status = BlockedStatus("No backends configured")

        return backends

    def install_pkgs(self):
        logging.info("Installing packages")

        # we implement $codename expansion here
        # see the default value for 'source' in config.yaml
        if self.model.config.get('install_sources'):
            distrib_codename = lsb_release()['DISTRIB_CODENAME'].lower()
            add_source(
                self.model.config['install_sources']
                    .format(distrib_codename=distrib_codename),
                self.model.config.get('install_keys'))
        apt_update(fatal=True)
        apt_install(self.PACKAGES, fatal=True)
        self.update_status()

    def on_install(self, event):
        self.install_pkgs()
        self.update_status()


if __name__ == '__main__':
    main(ManilaFlashBladePluginCharm)
