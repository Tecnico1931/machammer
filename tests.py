#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import subprocess
from unittest import main, skip, TestCase

from machammer import (functions, system_profiler,
                       network, hooks, users,
                       screensaver, defaults,)


class SystemProfilerTestCase(TestCase):
    def testSerialNumber(self):
        sn = system_profiler.get('Hardware', 'serial_number')
        self.assertTrue(len(sn) > 8)

    def testInvalidType(self):
        with self.assertRaises(Exception):
            system_profiler.SystemProfile('Whatever')

    def testKeys(self):
        self.assertTrue(len(system_profiler.keys()) > 3)

    def testTypes(self):
        self.assertIn('Hardware', system_profiler.types())

    def testOsVersion(self):
        """
        Check that the OS version we get from SP is contained
        in the output of sw_vers
        """
        build = subprocess.check_output(['sw_vers', '-buildVersion']).strip()
        software = system_profiler.SystemProfile('Software')
        self.assertIn(build, software.os_version)

    def testOsVersionShortcut(self):
        build = subprocess.check_output(['sw_vers', '-buildVersion']).strip()
        self.assertTrue(build in system_profiler.get('Software', 'os_version'))


class NetworkTestCase(TestCase):
    def test_wifi_enable(self):
        """Turn wifi power on, check that it's on"""
        network.set_wifi_power(True)
        time.sleep(3)
        self.assertTrue(network.get_wifi_power())

    def test_wired(self):
        self.assertTrue(network.is_wired())

    @skip('blaa')
    def test_wifi_disable(self):
        network.set_wifi_power(False)
        time.sleep(3)
        self.assertTrue(not network.get_wifi_power())

    def test_primary(self):
        self.assertEqual(network.get_primary(), 'en4')

    def test_primary_wired(self):
        self.assertTrue(network.is_wired(True))


class AppsTestCase(TestCase):
    def setUp(self):
        self.profile = system_profiler.SystemProfile('Applications')

    def testFindStickes(self):
        results = self.profile.find('_name', 'Stickies')
        self.assertTrue(len(results) > 0)

    def testStickiesVersion(self):
        results = self.profile.find('_name', 'Stickies')
        self.assertEquals(results[0]['version'], '10.0')

    def testFindApplications(self):
        results = self.profile.find('path', '/Applications')
        self.assertTrue(len(results) > 10)


class FunctionsTestCase(TestCase):
    def setUp(self):
        self.stickes = '/Applications/Stickies.app'

    def test_notification(self):
        functions.display_notification('blaaa "lalala"')

    def test_add_login_item(self):
        users.add_login_item(self.stickes)

    def test_remove_login_item(self):
        users.remove_login_item(path=self.stickes)

    def test_mount_image(self):
        p = functions.mount_image('/Users/filipp/Downloads/AdobeFlashPlayer_22au_a_install.dmg')
        self.assertEquals(p, '/Volumes/Adobe Flash Player Installer')

    @skip('This works, trust me.')
    def test_create_media(self):
        functions.create_os_media('/Applications/Install macOS Sierra.app',
                                  '/Volumes/Untitled')

    @skip('This works, trust me.')
    def test_sleep(self):
        functions.sleep()


class ScreenSaverTestCase(TestCase):
    def test_set_invalid(self):
        with self.assertRaises(Exception):
            screensaver.set('Blalala')

    def test_set_flurry(self):
        self.assertEquals(screensaver.set('Flurry'), None)

    def test_get(self):
        self.assertEquals(screensaver.get(), 'Flurry')


class HooksTestCase(TestCase):
    def gethook(self):
        return defaults.get(hooks.PREF_DOMAIN, 'LoginHook')

    def test_set_login_path(self):
        hooks.login('/lalala')
        self.assertEquals(self.gethook(), '/lalala')

    def test_set_login_decorator(self):
        from machammer.decorators import login

        @login
        def blaa():
            import sys
            import subprocess
            subprocess.call(['/usr/bin/say', 'Hello ' + sys.argv[1]])

        blaa()
        self.assertEquals(self.gethook(), '/var/root/Library/mh_loginhook.py')

    def test_unset_login(self):
        hooks.login()
        with self.assertRaises(Exception):
            self.assertEquals(self.gethook(), '')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
