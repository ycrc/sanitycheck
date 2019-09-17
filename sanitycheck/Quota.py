#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
import getpass
import os
import sys
import stat
import subprocess
import unittest
from . import utils

__unittest = True
b_prefixes = ['Y', 'Z', 'E', 'P', 'T', 'G', 'M', 'K']
b_units = [i for i in zip(b_prefixes, [1024 ** i for i in range(len(b_prefixes)+1, 1, -1)])]

def get_gpfs_mounts():
    '''
    get all the mounted GPFS filesystems
    return return dictionary mapping device_name -> mount_point 
    '''
    mounts = {}
    returncode, mountlines = utils.get_stdout('mount -t gpfs')
    if returncode != 0:
        return None
    for mountline in mountlines.split('\n'):
        parts = mountline.split()
        if len(parts) == 6:
            mounts[parts[0]] = parts[2]
    return mounts

def table_to_list_dict(table, filesystem):
    header = []
    quotas = []
    sep = ':'
    for i, line in enumerate(table.split('\n')):
        if i == 0:
            header = line.split(sep)[:-1]
        else:
            zipped = dict(zip(header, line.split(sep)[:-1]))
            if len(zipped) > 0:
                if zipped['blockUsage']!='0':
                    zipped['filesystemName'] = filesystem
                    quotas.append(zipped)
    return quotas

def size_for_human(bytes_str):
    bytes_num = float(bytes_str)
    for prefix, scale_factor in b_units:
        if abs(bytes_num) >= .8 * scale_factor:
            return '{:0.2f}{}'.format(bytes_num/scale_factor, prefix)
    return(bytes_str+' ')

def make_quota_table(quotas, header):
    header = ['Quota>95%']+header
    widths = dict(zip(header,[len(h) for h in header]))
    warn = False
    warn_quotas_idx = []
    for i,quota in enumerate(quotas):
        warn_kinds = []
        for kind in ['block', 'files']:
            limit = max(int(quota[kind+'Quota']), int(quota[kind+'Limit']))
            if limit != 0 and int(quota[kind+'Usage']) >= .95 * limit:
                warn_kinds.append('{}'.format(kind))
                warn = True
        if len(warn_kinds)>0:
            warn_quotas_idx.append(i)
            quota['Quota>95%'] = ','.join(warn_kinds)
            for h in header:
                if h.startswith('block'):
                    quota[h] = size_for_human(quota[h])
                if widths[h] < len(quota[h]):
                    widths[h] = len(quota[h])

    lines = [" ".join(['{:>{width}s}'.format(h, width=widths[h]) for h in header])]
    for quota_idx in warn_quotas_idx:
        lines.append(" ".join(['{:>{width}s}'.format(quotas[quota_idx][h], width=widths[h]) for h in header]))
    return warn, lines

class Quota(unittest.TestCase):
    '''
    Check gpfs quotas
    '''

    def setUp(self):
        self.user_name = getpass.getuser()
        returncode, grp_string = utils.get_stdout('groups')
        self.assertEqual(returncode, 0, 'groups command failed.')
        self.groups = grp_string.split()

    def test_gpfs_mounts(self):
        mounts_dict = get_gpfs_mounts()
        self.assertIsNotNone(mounts_dict, 'Unable to run mount command.')
        self.assertGreater(len(mounts_dict), 0, 'No GPFS filesystems found.')

    def test_gpfs_quotas(self):
        mmlsquota = '/usr/lpp/mmfs/bin/mmlsquota -Y --block-size auto {} {} {}'
        mounts_dict = get_gpfs_mounts()
        quota_keys = (['filesystemName', 'filesetname', 'quotaType'] + 
                      [y+x for y in ['block', 'files'] for x in ['Usage', 'Quota', 'Limit']])
        quotas = []
        for filesystem in mounts_dict:
            user_cmd = mmlsquota.format('-u', self.user_name, filesystem)
            returncode, user_quota_lines = utils.get_stdout(user_cmd)
            self.assertEqual(returncode, 0, 'Running quota comand failed ({})'.format(user_cmd))
            quotas += table_to_list_dict(user_quota_lines, filesystem)
            for group in self.groups:
                group_cmd = mmlsquota.format('-g', group, filesystem)
                returncode, group_quota_lines = utils.get_stdout(group_cmd)
                self.assertEqual(returncode, 0, 'Running quota comand failed ({})'.format(group_cmd))
                quotas += table_to_list_dict(group_quota_lines, filesystem)
        warn, quota_lines = make_quota_table(quotas, quota_keys)
        self.assertFalse(warn, 'Quotas are dangerously high!\n'+'\n'.join(quota_lines))
        
if __name__ == '__main__':
    unittest.main(failfast=True)
