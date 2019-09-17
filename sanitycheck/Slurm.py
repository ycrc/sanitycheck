#!/usr/bin/env python
# -*- coding: utf-8 -*-
import getpass
import os
import subprocess
import unittest
from . import utils

__unittest = True

class Slurm(unittest.TestCase):
    '''
    Checks to make sure Slurm is working and configured properly for user
    '''

    def setUp(self):
        self.user_name = getpass.getuser()
        returncode, grp_string = utils.get_stdout('groups')
        self.assertEqual(returncode, 0, "groups command failed.")
        self.groups = grp_string.split()

    def test_squeue(self):
        returncode = utils.get_return_code('squeue -u {}'.format(self.user_name))
        self.assertEqual(returncode, 0, "squeue failed, is slurm database down?")

    def test_accounts(self):
        returncode, acct_string = utils.get_stdout('sacctmgr -P show assoc user={}'.format(self.user_name))
        self.assertEqual(returncode, 0, "sacctmgr failed, is slurm database down?")
        acct_lines = acct_string.split('\n')[1:-1]
        self.assertGreater(len(acct_lines), 0, "You aren't a member of any slurm accounts, you should be in at least one.")
        slurm_accounts = [x.split('|', 2)[1] for x in acct_lines]
        self.assertIn(self.groups[0], slurm_accounts, "You can't submit jobs using your primary group, that should be fixed.")


if __name__ == '__main__':
    unittest.main(failfast=False)
