#!/usr/bin/env python

import site
from sys import argv, version_info as py_ver, path as sys_path
from os import environ, pathsep
from os.path import join, abspath, dirname, split, \
     exists as path_exists, sep as path_sep
from inspect import getfile, currentframe


#baseDir = abspath(join(dirname(__file__),".."))
# DO NOT USE __file__ !!!
# __file__ fails if script is called in different ways on Windows
# __file__ fails if someone does os.chdir() before
# sys.argv[0] also fails because it doesn't not always contains the path
just_installed = False
baseDir = abspath(join(split(getfile( currentframe() ))[0], '..'))
targetDir = join(baseDir, 'lib', 'python%i.%i' % py_ver[:2], 'site-packages')
scriptDir = 'local-py%d%d' % py_ver[:2]

setup_override = """
AUTODIST_SETUP_DATA={}
def setup(*args, **kwargs):
  global AUTODIST_SETUP_DATA
  AUTODIST_SETUP_DATA.update(kwargs)
  AUTODIST_SETUP_DATA['*args'] = args

"""
setup_reporter = """
import pickle
import sys
for key in list(AUTODIST_SETUP_DATA.keys()):
    if 'require' not in key:
        del AUTODIST_SETUP_DATA[key]
sys.stdout.write( "START_AUTODIST_SETUP" +
                  pickle.dumps(AUTODIST_SETUP_DATA) +
                  "END_AUTODIST_SETUP" )
"""

def configure_packages(verbose=True):
    import os
    import sys
    import re
    import pickle
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
    def interrogate_dependencies(package):
        setup_re = re.compile('setup\\(')
        CMD=open(os.path.join(package,'setup.py'),'r').readlines()
        i = 0;
        while i < len(CMD):
            if setup_re.search(CMD[i]):
                break
            i += 1
        if i == len(CMD):
            return ""
        if CMD[i].lstrip() != CMD[i]:
            while i > 0 and not CMD[i][0].strip():
                i -= 1
        CMD.insert(i, setup_override)
        tmp = join(package,'setup_autodist.py')
        FILE = open(tmp, 'w')
        FILE.write("".join(CMD))
        FILE.write(setup_reporter)
        FILE.close()
        proc = Popen( [ sys.executable, tmp ],
                      stdout=PIPE, stderr=PIPE, cwd=package )
        ANS = proc.communicate()
        if ANS[1]:
            Write(ANS[1])
        OUT.flush()
        os.remove(tmp)
        if proc.returncode:
            raise Exception("ERROR interrogating %s" % (p,))
        if ANS[0]:
            pickleStr = ANS[0] \
                        .split('START_AUTODIST_SETUP',1)[-1] \
                        .split('END_AUTODIST_SETUP')[0] \
                        .replace('\r\n','\n')
            return pickle.loads(pickleStr)
        else:
            return {}
    def sort_packages(pkg, unsorted, sorted, all_deps, base2pkg):
        prereqs = all_deps.get(os.path.basename(pkg), [])
        for prereq in prereqs:
            prereq = prereq.split('>',1)[0].split('=',1)[0].split('<',1)[0]
            p_pkg = base2pkg.get(prereq, None)
            if p_pkg and p_pkg in unsorted:
                unsorted.remove(p_pkg)
                sort_packages(p_pkg, unsorted, sorted, all_deps, base2pkg)
        sorted.append(pkg)

    originalDir = os.getcwd()
    srcDir = join(baseDir, 'dist', 'python')
    localBinDir = join(baseDir,'bin',scriptDir)
    libs    = ['--install-lib=%s' % (targetDir,),
               '--install-purelib=%s' % (targetDir,),
               '--install-platlib=%s' % (targetDir,),
               '--install-data=%s' % (targetDir,),
               ]
    scripts = ['--install-scripts=%s' % (localBinDir,)]
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
              "sys.argv=sys.argv[:1]+['--install-dir=%s','--script-dir=%s']; "\
              "sys.exit(bootstrap())" % \
              ( abspath(join(srcDir,'dist','setuptools')), 
                targetDir.replace('\\','\\\\'),
                localBinDir.replace('\\','\\\\') )
        Write("Command: %s\n" % CMD)
        proc = Popen([sys.executable, "-c", CMD], stdout=OUT, stderr=OUT)
        proc.communicate()
        OUT.flush()
        if proc.returncode:
            raise Exception("ERROR installing setuptools")

    packages = [
        join(srcDir,'dist',x)
        for x in sorted(os.listdir(join(srcDir,'dist'))) if x != 'setuptools' ]
    packages.extend(
        join(srcDir,'src',x) for x in sorted(os.listdir(join(srcDir,'src'))) )

    Write(stars+"Interrogating package dependencies"+stars)
    deps={}
    base2pkg = {}
    for p in packages:
        Write("Interrogating %s\n" % p)
        _deps = interrogate_dependencies(p)
        deps[os.path.basename(p)] = _deps.get('install_requires',[])
        base2pkg[os.path.basename(p)] = p
    pkg_order = []
    while packages:
        sort_packages(packages.pop(0), packages, pkg_order, deps, base2pkg)
    packages = pkg_order
    Write("Package install sequence:\n\t"+"\n\t".join(packages))

    # Install all packages
    Write(stars+"Installing all packages"+stars)
    for package in packages:
        setupFile = join(srcDir,package,'setup.py')
        Log("\n(INFO) installing %s\n" % (package,))
        if not os.stat(setupFile):
            Write("WARNING: %s not found.  Cannot install the package\n"
                  % (setupFile,) )
            continue
        CMD = [sys.executable, setupFile, 'install'] + libs + scripts
        Write("Command: %s\n" % CMD)
        proc = Popen(CMD, stdout=OUT, stderr=OUT, cwd=join(srcDir,package))
        proc.communicate()
        OUT.flush()
        if proc.returncode:
            raise Exception("ERROR: %s did not install correctly\n"
                            % (package,))

    # localize all scripts
    Write(stars+"Localizing all package scripts"+stars)
    for script in os.listdir(localBinDir):
        if script.endswith('.pyc'):
            continue
        if script.startswith('_'):
            continue
        if script.endswith('-script.py'):
            continue
        if script.endswith('.exe'):
            continue
        if script.endswith('.py'):
            base = script[:3]
        else:
            base = script
        absName = join(localBinDir,base)
        if not path_exists(absName+'-script.py'):
            Write("(INFO) Localizing %s -> %s-script.py\n" % (script,base))
            os.rename(join(localBinDir,script), absName+'-script.py')
    open(join(localBinDir,'__init__.py'), "w").close()

    if not verbose:
        sys.stdout.write("\n")
        sys.stdout.flush()
        OUT.close()


def run_script(name):
    # Unfortunately, try as I might, the auto-install process messes
    # with the Python environment *just enough* that key applications
    # (mostly those that rely on component / plugin systems) fail to run
    # properly.  As a workaround, we will just re-run the original
    # script that got us here.
    if just_installed:
        from sys import exit, executable
        from subprocess import call
        exit(call([executable] + argv))

    try:
        script = open(
            join(baseDir, 'bin', scriptDir, "%s-script.pyc" % (name,)), 'rb')
    except IOError:
        __import__('%s.%s-script' % (scriptDir, name))
        # we may not get here -- and that's OK (that means the original
        # script did not have a check to see if __name__=='__main__')
        script = open(
            join(baseDir, 'bin', scriptDir, "%s-script.pyc" % (name,)), 'rb')
    # This is a trick to directly execute the compiled script bytecode:
    # the first 8 bytes in a pyc are actually 2 longs: a version stamp
    # and a timestamp.  The rest of the file is straight bytecode.
    pyc = script.read()
    env = dict()
    env['__name__'] = '__main__'
    # Hide the fact that we are using a wrapper executable (on Windows)
    argv[0] = argv[0].replace('-script.py','')
    from marshal import loads
    exec(loads(pyc[8:]), env, env)


def localized_script(name):
    return join(baseDir, 'bin', scriptDir, '%s-script.py' % (name,))


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
    just_installed = True

# Now we need to configure our site-packages (i.e., process the *.pth files)
site.addsitedir(targetDir, site._init_pathinfo())
