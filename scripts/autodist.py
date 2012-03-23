#!/usr/bin/env python

import site
from sys import version_info as py_ver, path as sys_path
from os import environ, pathsep
from os.path import join, abspath, dirname, split, \
     exists as path_exists, sep as path_sep
from inspect import getfile, currentframe

#baseDir = abspath(join(dirname(__file__),".."))
# DO NOT USE __file__ !!!
# __file__ fails if script is called in different ways on Windows
# __file__ fails if someone does os.chdir() before
# sys.argv[0] also fails because it doesn't not always contains the path
baseDir = abspath(join(split(getfile( currentframe() ))[0], '..'))
targetDir = join(baseDir, 'lib', 'python%i.%i' % py_ver[:2], 'site-packages')
scriptDir = 'local-py%d%d' % py_ver[:2]

def configure_packages(verbose=True):
    import os
    import sys
    from subprocess import Popen, PIPE

    if verbose:
        OUT = sys.stdout
    else:
        sys.stdout.write("Configuring Python packages for first use")
        OUT = open(join(baseDir, 'dist', 'autodist.log'), 'w')
    def Write(*args):
        OUT.flush()
        OUT.write(*args)
        OUT.flush()
    def Log(*args):
        Write(*args)
        if not verbose:
            sys.stdout.write(".")
            sys.stdout.flush()

    originalDir = os.getcwd()
    srcDir = join(baseDir, 'dist', 'python')
    localBinDir = join(baseDir,'bin',scriptDir)
    prefix  = '--prefix=%s' % (targetDir,)
    libs    = '--install-lib=%s' % (targetDir,)
    scripts = '--install-scripts=%s' % (localBinDir,)
    stars = "\n"+"*"*72+"\n"

    if not path_exists(targetDir):
        os.makedirs(targetDir)

    Write("PYTHONPATH = '%s'\n" % (os.environ['PYTHONPATH'],))

    # Set up the setuptools (if needed)
    try:
        from setuptools import setup
    except ImportError:
        Write(stars+"Installing setuptools"+stars)
        # We cannot install setuptools from within this interpreter
        # because this would result in importing setuptools from the
        # install source (and not the final installation directory)
        CMD = "import sys; sys.path.insert(0, '%s'); "\
              "from setuptools.command.easy_install import bootstrap; "\
              "sys.argv = sys.argv[:1] + ['%s','--script-dir=%s']; "\
              "sys.exit(bootstrap())" % \
              (abspath(join(srcDir,'dist','setuptools')), prefix, localBinDir)
        Write("Command: %s\n" % CMD)
        proc = Popen([sys.executable, "-c", CMD], stdout=OUT, stderr=OUT)
        proc.communicate()
        if proc.returncode:
            raise Exception("ERROR installing setuptools")

    # Install all packages
    Write(stars+"Installing all packages"+stars)
    packages = [
        join(srcDir,'dist',x)
        for x in sorted(os.listdir(join(srcDir,'dist'))) if x != 'setuptools' ]
    packages.extend(
        join(srcDir,'src',x) for x in sorted(os.listdir(join(srcDir,'src'))) )
    for package in packages:
        setupFile = join(srcDir,package,'setup.py')
        Log("\n(INFO) installing %s\n" % (package,))
        if not os.stat(setupFile):
            Write("WARNING: %s not found.  Cannot install the package\n"
                  % (setupFile,) )
            continue
        os.chdir(join(srcDir,package))
        CMD = [sys.executable, setupFile, 'install', libs, scripts]
        Write("Command: %s\n" % CMD)
        proc = Popen(CMD, stdout=OUT, stderr=OUT)
        proc.communicate()
        if proc.returncode:
            OUT.flush()
            raise Exception("ERROR: %s did not install correctly\n"
                            % (package,))
        os.chdir(originalDir)

    # localize all scripts
    Write(stars+"Localizing all package scripts"+stars)
    for script in os.listdir(localBinDir):
        if script.endswith('.pyc'):
            continue
        if script.startswith('_'):
            continue
        if script.endswith('-script.py'):
            continue
        absName = join(localBinDir,script)
        if not path_exists(absName+'-script.py'):
            Write("(INFO) Localizing %s -> %s-script.py\n" % (script,script))
            os.rename(absName, absName+'-script.py')
    open(join(localBinDir,'__init__.py'), "w").close()

    if not verbose:
        sys.stdout.write("\n")
        sys.stdout.flush()
        OUT.close()


def run_script(name):
    # This is a trick to import the original localized script generated
    # by configure_packages()
    __import__('%s.%s-script' % (scriptDir, name))


# Set up our local site-packages
pythonpath = environ.get('PYTHONPATH',None)
if pythonpath:
    environ['PYTHONPATH'] = pathsep.join((targetDir,pythonpath))
else:
    environ['PYTHONPATH'] = targetDir
sys_path.insert(1,targetDir)

# If the site-packages is not present, install it
if not path_exists(targetDir):
    configure_packages(__name__ == '__main__')

# Now we need to configure our site-packages (i.e., process the *.pth files)
site.addsitedir(targetDir, site._init_pathinfo())
