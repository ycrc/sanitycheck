#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
import getpass
import os
import stat
import subprocess
import unittest
from . import utils

__unittest = True

class SSH(unittest.TestCase):
    '''
    Checks to make sure ssh works. 
    '''

    def setUp(self):
        self.user_name = getpass.getuser()
        self.home = os.path.expanduser('~')
        self.dot_ssh = os.path.join(self.home, '.ssh')
        self.auth_keys_file = os.path.join(self.dot_ssh, 'authorized_keys')
        self.dot_ssh_list = [os.path.join(self.dot_ssh, x) for x in os.listdir(self.dot_ssh)]

    def test_dir_permissions(self):
        home_stat = os.stat(self.home)
        dot_ssh_stat = os.stat(self.dot_ssh)
        self.assertFalse(home_stat.st_mode & (stat.S_IWGRP | stat.S_IWOTH), 
            'Your home directory should not be writable by anyone but you. To fix run:\nchmod go-w ~')
        self.assertFalse(dot_ssh_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP|
                                                 stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH), 
            'Your ~/.ssh directory should not be accessable to anyone but you. To fix run:\nchmod 700 ~/.ssh')

    def test_file_permissions_and_keys(self):
        self.assertTrue(os.path.isfile(self.auth_keys_file), "No authorized_keys file found.")
        all_files = [f for f in self.dot_ssh_list if os.path.isfile(f)]
        pub_keys = [x for x in glob(os.path.join(self.dot_ssh, '*.pub'))]
        private_keys = []
        read_only_files = [os.path.join(self.dot_ssh,f)for f in ['known_hosts', 'config'] if os.path.isfile(f)] + [self.auth_keys_file]

        for ro_file in read_only_files + pub_keys:
            file_stat = os.stat(ro_file)
            self.assertFalse(file_stat.st_mode & (stat.S_IXUSR |
                              stat.S_IWGRP | stat.S_IXGRP |
                              stat.S_IWOTH | stat.S_IXOTH ),
                              '{0} might have incorrect permissions. To fix run:\nchmod 644 {0}'.format(ro_file))
        
        for other_file in set(all_files) - set(pub_keys) - set(read_only_files):
            with open(other_file) as possible_key:
                if 'PRIVATE KEY' in possible_key.readline():
                    private_keys.append(other_file)

        for priv_key in private_keys:
            key_stat = os.stat(priv_key)
            self.assertFalse(key_stat.st_mode & (stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH ),
                              '{0} is a private key with incorrect permissions. To fix run: chmod 600 {0}'.format(ro_file))

        keygen_cmd = "Run ssh-keygen to create a keypair using defaults and no password, then authorize the public key with:\ncat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"
        # get pubkeys for all passwordless keys
        self.assertGreater(len(private_keys), 0, 'No private key found, but you need one. ' +keygen_cmd)
        pub_keys_from_private = []
        for pv_key in private_keys:
            returncode, stdout = utils.get_stdout('ssh-keygen -y -P "" -f {}'.format(pv_key))
            if returncode == 0:
                pub_keys_from_private.append(stdout.rstrip())
        self.assertGreater(len(pub_keys_from_private), 0, 'No paswordless private key found, but you need one. ' +keygen_cmd)
        auth_keys = []
        with open(self.auth_keys_file) as auth_keys_file:
            for key_line in auth_keys_file:
                if key_line.startswith('ssh'):
                    auth_key = ' '.join(key_line.split()[:2])
                    auth_keys.append(any( [pubkey == auth_key for pubkey in pub_keys_from_private]))
        self.assertTrue(any(auth_keys), 'No authorized paswordless public key found. ' +keygen_cmd)
        
    def test_ssh(self):
        returncode = utils.get_return_code('ssh {}@localhost "echo success"'.format(self.user_name))
        self.assertEqual(returncode, 0, "Can't log you in with ssh, something is wrong.")

if __name__ == '__main__':
    unittest.main(failfast=True)
