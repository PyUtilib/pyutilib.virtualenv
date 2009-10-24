#! /usr/bin/env python
#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________
#
# This script creates a Python installer script.  Note that this script assumes that 
# 'virtualenv' is installed in Python.
#

import os
import os.path
import virtualenv
import sys
import stat

def main():
    if len(sys.argv) != 3:
        print "virtualenv_installer <config-file> <name>"
        sys.exit(1)

    script_name = sys.argv[2]

    here = os.path.dirname(os.path.abspath(__file__))
    INPUT = open(os.path.join(here,'header.py'),'r')
    new_text = "".join( INPUT.readlines() )
    INPUT.close()
    INPUT = open(sys.argv[1],'r')
    new_text += "".join( INPUT.readlines() )
    INPUT.close()
    #new_text += "\n"
    #new_text += "Repository.easy_install_path='"+sys.prefix+os.sep+'bin'+os.sep+'easy_install'+"'"

    new_text = virtualenv.create_bootstrap_script(new_text)
    tmp = []
    for line in new_text.split('\n'):
        if not 'win32api' in line:
            tmp.append(line)
        else:
            tmp.append( line[:line.index(line.strip())] + 'pass')
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
        os.chmod(script_name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

if __name__ == '__main__':
    main()

