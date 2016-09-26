#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import subprocess
from unittest import main, skip, TestCase

import machammer.functions as mh
from machammer import system_profiler


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
        mh.display_notification('blaaa "lalala"')

    def test_add_login_item(self):
        mh.add_login_item(self.stickes)

    def test_remove_login_item(self):
        mh.remove_login_item(path=self.stickes)

    def test_mount_image(self):
        p = mh.mount_image('/Users/filipp/Downloads/AdobeFlashPlayer_22au_a_install.dmg')
        self.assertEquals(p, '/Volumes/Adobe Flash Player Installer')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
