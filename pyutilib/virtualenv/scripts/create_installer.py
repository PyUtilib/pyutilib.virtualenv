#! /usr/bin/env python
#  _________________________________________________________________________
#
#  TEVA-SPOT Toolkit: Tools for Designing Contaminant Warning Systems
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the LGPL License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the README.txt file in the top SPOT directory.
#  _________________________________________________________________________
#
# This script creates the spot_install script.  Note that this script assumes that 
# 'virtualenv' is installed in Python.
#

import os
import os.path
import virtualenv
import sys

def main():
    if len(sys.argv) == 1:
        print "virtualenv_installer <config-file> <name>"
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    print "HERE",here
    sys.exit(1)
    script_name = os.path.join(here, sys.argv[1])

    INPUT = open('header.py','r')
    new_text = "".join( INPUT.readlines() )
    INPUT.close()
    INPUT = open('config.py','r')
    new_text += "".join( INPUT.readlines() )
    INPUT.close()
    INPUT = open('venv.py','r')
    new_text += "".join( INPUT.readlines() )
    INPUT.close()

    new_text = virtualenv.create_bootstrap_script(new_text)
    tmp = []
    for line in new_text.split('\n'):
        if not 'win32api' in line:
            tmp.append(line)
    new_text = "\n".join(tmp)
    if os.path.exists(script_name):
        f = open(script_name)
        cur_text = f.read()
        f.close()
    else:
        cur_text = ''
    print 'Updating %s' % script_name,
    if cur_text == new_text:
        print '... no changes.'
    else:
        print '... script changed.'
        f = open(script_name, 'w')
        f.write(new_text)
        f.close()

if __name__ == '__main__':
    main()

