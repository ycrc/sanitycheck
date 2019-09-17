#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

def get_return_code(cmd):
    '''
    get the return code from running cmd, suppress any stderr output
    return returncode
    '''
    DEVNULL = open(os.devnull, 'wb')
    returncode = subprocess.call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)
    DEVNULL.close()
    return returncode

def get_stdout(cmd):
    '''
    get the stdout from running cmd, suppress any stderr output
    return returncode, stdout
    '''
    DEVNULL = open(os.devnull, 'w')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=DEVNULL, shell=True)
    proc_out = proc.communicate()
    DEVNULL.close()
    return proc.returncode, proc_out[0].decode('utf8')

def get_stderr(cmd):
    '''
    get the stdout from running cmd, suppress any stderr output
    return returncode, stdout
    '''
    DEVNULL = open(os.devnull, 'w')
    proc = subprocess.Popen(cmd, stdout=DEVNULL, stderr=subprocess.PIPE, shell=True)
    proc_out = proc.communicate()
    DEVNULL.close()
    return proc.returncode, proc_out[1].decode('utf8')


