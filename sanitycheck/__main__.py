#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import argparse
from . import utils
from . import Lmod
from . import Quota
from . import Slurm
from . import SSH

__unittest = True


def main(verbosity=2, failfast=True):
    __unittest = True
    for test_mod in [Quota, SSH, Lmod, Slurm]:
        test_header_text = "# {} test #".format(test_mod.__name__)
        test_header_pad = "#" * (len(test_header_text))
        print("\n{0}\n{1}\n{0}\n".format(test_header_pad, test_header_text))
        suite = unittest.TestLoader().loadTestsFromModule(test_mod)
        unittest.TextTestRunner(verbosity=verbosity, failfast=failfast).run(suite)

