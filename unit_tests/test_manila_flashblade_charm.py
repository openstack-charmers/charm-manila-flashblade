# Copyright 2016 Canonical Ltd
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

import unittest
from src.charm import ManilaFlashBladePluginCharm
from ops.testing import Harness

from unittest import mock

from charmhelpers.core.host_factory.ubuntu import UBUNTU_RELEASES


class TestManilaFlashBladeCharm(unittest.TestCase):

    def setUp(self):
        self.harness = Harness(ManilaFlashBladePluginCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.harness.set_leader(True)
        backend = self.harness.add_relation('manila-plugin', 'manila')
        self.harness.add_relation_unit(backend, 'manila/0')

    def _get_partial_config_sample(self):
        """
        A config with all mandatory params set
        """
        return {
            'flashblade-mgmt-vip': '12.12.12.12',
            'flashblade-data-vip': '13.13.13.13',
            'flashblade-api': 'T-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        }

    def _get_valid_config_sample(self):
        """
        A minimal config that would transition the charm to ActiveState
        """
        partial_config = self._get_partial_config_sample()
        return partial_config

    def _get_source(self, codename, pocket, baseurl=None):
        if baseurl is None:
            baseurl = self.harness.charm.DEFAULT_REPO_BASEURL
        return ' '.join((
            'deb',
            baseurl,
            codename,
            pocket))

    def test_update_config(self):
        self.harness.update_config({
            "flashblade-api": "T-2345-dfea3-23109-ccffa1",
            "flashblade-mgmt-vip": "10.21.200.5",
            "flashblade-data-vip": "10.21.200.160",
            "package_status": "install",
            "share-backend-name": "__app__",
            "verbose": False,
        })

    @mock.patch('src.charm.add_source')
    @mock.patch('src.charm.apt_update')
    @mock.patch('src.charm.apt_install')
    @mock.patch('src.charm.lsb_release')
    def test_repo_management(self, lsb_release,
                             apt_install, apt_update, add_source):

        add_source.return_value = None
        apt_install.return_value = None
        apt_update.return_value = None

        # we'll need the config the charm considers valid
        # in order to test repo management:
        cfg = self._get_valid_config_sample()

        dynamic_source = self._get_source('{distrib_codename}', 'main')

        # generate test data for both 'source' values that need substituion
        # and for the static ones

        test_data = []

        for release in UBUNTU_RELEASES:
            static_source = self._get_source(release, 'main')
            test_data.append(
                (dynamic_source, release,
                    self._get_source(release, 'main')),
            )
            test_data.append(
                (static_source, release, static_source),
            )

        for i in test_data:
            # distro codename the charm runs on
            lsb_release.return_value = {'DISTRIB_CODENAME': i[1]}

            # configure to use specific repo version
            cfg['install_sources'] = i[0]
            cfg['install_keys'] = KEY

            # on_config calls package installation
            self.harness.update_config(cfg)
            self.harness.charm.on.install.emit()

            # make sure the repo management calls were correct
            add_source.assert_called_with(i[2], KEY)
            apt_install.assert_called_with(self.harness.charm.PACKAGES,
                                           fatal=True)
