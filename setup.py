#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

"""
Setup for pyutilib.virtualenv package
"""

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name="pyutilib.virtualenv",
    version=1.0,
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://software.sandia.gov/trac/pyutilib',
    license = 'BSD',
    platforms = ["any"],
    description = 'Utilities for building custom virtualenv bootstrap scripts.',
    long_description = read('README.txt'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Unix Shell',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      packages=['pyutilib', 'pyutilib.virtualenv', 'pyutilib.virtualenv.scripts'],
      keywords=['utility'],
      namespace_packages=['pyutilib'],
      entry_points = """
        [console_scripts]
        virtualenv_installer = pyutilib.virtualenv.scripts.create_installer:main
      """
      )

