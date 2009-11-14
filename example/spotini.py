#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

def configure(installer):
    installer.config="""
; This INI file can be used by vpy_install to create a virtual
; Python installation that is equivalent to the virtual 
; Python installation that is created by spot_install .
;
[installer]
description=This script manages the installation of SPOT.
default_dirname=tevaspot
default_windir=C:\\tevaspot
default_unixdir=./tevaspot
README=#
 # Installation generated by the spot_install script.
 #
 # This directory is managed with virtualenv, which creates a
 # virtual Python installation.  If the 'bin' directory is put in
 # user's PATH environment, then the bin/python command can be used to
 # employ SPOT without further installation.
 #
 # Directories:
 #   admin      Administrative data for maintaining this distribution
 #   bin        Scripts and executables
 #   data       Test data
 #   dist       Python packages that are not intended for development
 #   doc        SPOT documentation and tutorials
 #   examples   SPOT examples
 #   include    Python header files
 #   lib        Python libraries and installed packages
 #   etc        Math programming model files used for optimization
 #   src        Python packages whose source files can be
 #              modified and used directly within this virtual Python
 #              installation.
 #   Scripts    Python bin directory (used on MS Windows)
 #   test       Test directory
 #   util       Utility scripts (including spot_install)
 #

[nose]
pypi=nose

[pyutilib]
pyname=PyUtilib
root=https://software.sandia.gov/svn/public/pyutilib
dev=True

[coopr]
root=https://software.sandia.gov/svn/public/coopr/coopr
dev=True

[tevaspot]
pyname=TevaSpot
root=https://software.sandia.gov/svn/teva/spot/spot
trunk=/packages/tevaspot
tag=/packages/tevaspot
dev=True

[dos_cmd]
sp.cmd=
teva-spot.cmd=

[tevaspot:auxdir]
etc/mod=/etc/mod
examples/simple=/examples/simple
data/Net3=/packages/test/data/Net3
data/test1=/packages/test/data/test1
util=/packages/tevaspot/util
doc=/doc/pub
test=/packages/test/pyunit
"""

    #
    # Return the modified installer
    #
    return installer

