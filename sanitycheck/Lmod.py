#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import unittest
from . import utils

__unittest = True

class Lmod(unittest.TestCase):
    '''
    Checks to make sure Lmod is available and configured properly.
    '''

    def setUp(self):
        self.home = os.path.expanduser('~')

    def test_module_cmd(self):
        returncode = utils.get_return_code('type module')
        self.assertEqual(returncode, 0, "The module command is not defined")

    def test_stdenv_loaded(self):
        lmod_cmd = os.environ.get('LMOD_CMD')
        self.assertIsNotNone(lmod_cmd, "LMOD_CMD undefined, Lmod isn't available?")
        returncode, mod_list = utils.get_stderr('{} python list'.format(lmod_cmd))
        self.assertEquals(returncode, 0, "Couldn't list modules")
        self.assertTrue(') StdEnv' in mod_list, "No StdEnv found, are you running module purge --force somewhere? (You probably shouldn't)")
    
    def test_rc_files(self):
    # check for module loads in .rc files
        rc_files = [os.path.join(self.home, rc) for rc in ['.bashrc', '.bash_profile', '.bash_login', '.profile']]
        no_module_load = "Best practice to not load modules in your {} file. Consider using an alias or module collection."
        for rc_file in rc_files:
            if os.path.isfile(rc_file):
                with open(rc_file) as rc_lines:
                    for rc_line in rc_lines:
                        line = rc_line.lstrip()
                        self.assertFalse(line.startswith('module load'), no_module_load.format(rc_file))
                        self.assertFalse(line.startswith('ml load'), no_module_load.format(rc_file))

if __name__ == '__main__':
    unittest.main(failfast=True)
