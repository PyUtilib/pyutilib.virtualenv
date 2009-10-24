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
#
# This script was created with the virtualenv_install script.
#

import re
import urllib2
import zipfile
import shutil
import string
import textwrap
import sys
import glob


#
# The following taken from PyUtilib
#
if (sys.platform[0:3] == "win"): #pragma:nocover
   executable_extension=".exe"
else:                            #pragma:nocover
   executable_extension=""


def search_file(filename, search_path=None, implicitExt=executable_extension, executable=False,         isfile=True):
    if search_path is None:
        #
        # Use the PATH environment if it is defined and not empty
        #
        if "PATH" in os.environ and os.environ["PATH"] != "":
            search_path = string.split(os.environ["PATH"], os.pathsep)
        else:
            search_path = os.defpath.split(os.pathsep)
    for path in search_path:
      if os.path.exists(os.path.join(path, filename)) and \
         (not isfile or os.path.isfile(os.path.join(path, filename))):
         if not executable or os.access(os.path.join(path,filename),os.X_OK):
            return os.path.abspath(os.path.join(path, filename))
      if os.path.exists(os.path.join(path, filename+implicitExt)) and \
         (not isfile or os.path.isfile(os.path.join(path, filename+implicitExt))):
         if not executable or os.access(os.path.join(path,filename+implicitExt),os.X_OK):
            return os.path.abspath(os.path.join(path, filename+implicitExt))
    return None

#
# PyUtilib Ends
#


#
# The following taken from pkg_resources
#
component_re = re.compile(r'(\d+ | [a-z]+ | \.| -)', re.VERBOSE)
replace = {'pre':'c', 'preview':'c','-':'final-','rc':'c','dev':'@'}.get

def _parse_version_parts(s):
    for part in component_re.split(s):
        part = replace(part,part)
        if not part or part=='.':
            continue
        if part[:1] in '0123456789':
            yield part.zfill(8)    # pad for numeric comparison
        else:
            yield '*'+part

    yield '*final'  # ensure that alpha/beta/candidate are before final

def parse_version(s):
    parts = []
    for part in _parse_version_parts(s.lower()):
        if part.startswith('*'):
            if part<'*final':   # remove '-' before a prerelease tag
                while parts and parts[-1]=='*final-': parts.pop()
            # remove trailing zeros from each series of numeric parts
            while parts and parts[-1]=='00000000':
                parts.pop()
        parts.append(part)
    return tuple(parts)
#
# pkg_resources Ends
#

#
# Use pkg_resources to guess version.
# This allows for parsing version with the syntax:
#   9.3.2
#   8.28.rc1
#
def guess_release(svndir):
    output = urllib2.urlopen(svndir).read()
    if output=="":
       return None
    links = re.findall('\<li>\<a href[^>]+>[^\<]+\</a>',output)
    versions = []
    for link in links:
        versions.append( re.split('>', link[:-5])[-1] )
    latest = None
    latest_str = None
    for version in versions:
        if version is '.':
            continue
        v = parse_version(version)
        if latest is None or latest < v:
            latest = v
            latest_str = version
    return svndir+"/"+latest_str



def zip_file(filename,fdlist):
    zf = zipfile.ZipFile(filename, 'w')
    for file in fdlist:
        if os.path.isdir(file):
            for root, dirs, files in os.walk(file):
                for fname in files:
                    if fname.endswith('exe'):
                        zf.external_attr = (0777 << 16L) | (010 << 28L)
                    else:
                        zf.external_attr = (0660 << 16L) | (010 << 28L)
                    zf.write(join(root,fname))
        else:
            zf.write(file)
    zf.close()


def unzip_file(filename, dir=None):
    fname = os.path.abspath(filename)
    zf = zipfile.ZipFile(fname, 'r')
    if dir is None:
        dir = os.getcwd()
    for file in zf.infolist():
        name = file.filename
        if name.endswith('/') or name.endswith('\\'):
            outfile = os.path.join(dir, name)
            if not os.path.exists(outfile):
                os.makedirs(outfile)
        else:
            outfile = os.path.join(dir, name)
            parent = os.path.dirname(outfile)
            if not os.path.exists(parent):
                os.makedirs(parent)
            OUTPUT = open(outfile, 'wb')
            OUTPUT.write(zf.read(name))
            OUTPUT.close()
    zf.close()



class Repository(object):

    easy_install_path = "easy_install"
    python = "python"
    svn = "svn"
    dev = []

    def __init__(self, name, root=None, trunk=None, stable=None, release=None, tag=None, pyname=None, pypi=None, dev=False):
        self.name = name
        if not root is None:
            try:
                self.trunk = root+'/trunk'
                self.trunk_root = self.trunk
            except urllib2.HTTPError:
                self.trunk = None
                self.trunk_root = None
            try:
                self.stable = guess_release(root+'/stable')
                self.stable_root = self.stable
            except urllib2.HTTPError:
                self.stable = None
                self.stable_root = None
            try:
                self.release = guess_release(root+'/releases')
                self.release_root = self.release
            except urllib2.HTTPError:
                self.release = None
                self.release_root = None
        else:
            self.trunk = None
            self.trunk_root = None
            self.stable = None
            self.stable_root = None
            self.release = None
            self.release_root = None
        if not trunk is None:
            if self.trunk is None:
                self.trunk = trunk
            else:
                self.trunk += trunk
        if not stable is None:
            if self.stable is None:
                self.stable = stable
            else:
                self.stable += stable
        if not release is None:
            if self.release is None:
                self.release = release
            else:
                self.release += release
        if not tag is None:
            if self.release is None:
                self.release = tag
            else:
                self.release += tag
        self.pypi = pypi
        if not pypi is None:
            self.pyname=pypi
        else:
            self.pyname=pyname
        self.dev = dev
        if dev:
            Repository.dev.append(name)
        self.pkgdir = None
        self.pkgroot = None

    def install_trunk(self, dir=None, setup=True):
        if self.trunk is None:
            if not self.stable is None:
                self.install_stable(dir=dir, setup=setup)
            elif self.pypi is None:
                self.install_release(dir=dir, setup=setup)
            else:
                self.easy_install(setup, dir)
        else:
            self.pkgdir=self.trunk
            self.pkgroot=self.trunk_root
            print "-----------------------------------------------------------------"
            print "  Checking out source for package",self.name
            print "     Subversion dir: "+self.trunk
            if os.path.exists(dir):
                print "     No checkout required"
                print "-----------------------------------------------------------------"
            else:
                print "-----------------------------------------------------------------"
                self.run([self.svn,'checkout','-q',self.trunk, dir])
            if setup:
                self.run([self.python, 'setup.py', 'develop'], dir=dir)

    def install_stable(self, dir=None, setup=True):
        if self.stable is None: 
            if not self.release is None:
                self.install_release(dir=dir, setup=setup)
            elif self.pypi is None:
                self.install_trunk(dir=dir, setup=setup)
            else:
                self.easy_install(setup, dir)
        else:
            self.pkgdir=self.stable
            self.pkgroot=self.stable_root
            print "-----------------------------------------------------------------"
            print "  Checking out source for package",self.name
            print "     Subversion dir: "+self.stable
            print "     Source dir:     "+dir
            if os.path.exists(dir):
                print "     No checkout required"
                print "-----------------------------------------------------------------"
            else:
                print "-----------------------------------------------------------------"
                self.run([self.svn,'checkout','-q',self.stable, dir])
            if setup:
                self.run([self.python, 'setup.py', 'develop'], dir=dir)

    def install_release(self, dir=None, setup=True):
        if self.release is None:
            if not self.stable is None:
                self.install_stable(dir=dir, setup=setup)
            elif self.pypi is None:
                self.install_trunk(dir=dir, setup=setup)
            else:
                self.easy_install(setup, dir)
        else:
            self.pkgdir=self.release
            self.pkgroot=self.release_root
            print "-----------------------------------------------------------------"
            print "  Checking out source for package",self.name
            print "     Subversion dir: "+self.release
            print "     Source dir:     "+dir
            if os.path.exists(dir):
                print "     No checkout required"
                print "-----------------------------------------------------------------"
            else:
                print "-----------------------------------------------------------------"
                self.run([self.svn,'checkout','-q',self.release, dir])
            if setup:
                self.run([self.python, 'setup.py', 'install'], dir=dir)

    def update_trunk(self, dir=None):
        if self.trunk is None:
            if not self.pypi is None:
                self.easy_upgrade()
            elif not self.stable is None:
                self.update_stable()
            else:
                self.update_release()
        else:
            self.pkgdir=self.trunk
            self.pkgroot=self.trunk_root
            print "-----------------------------------------------------------------"
            print "  Updating source for package",self.name
            print "     Subversion dir: "+self.trunk
            print "     Source dir:     "+dir
            print "-----------------------------------------------------------------"
            self.run([self.svn,'update','-q',dir])
            self.run([self.python, 'setup.py', 'develop'], dir=dir)

    def update_stable(self, dir=None):
        if self.stable is None:
            if not self.pypi is None:
                self.easy_upgrade()
            elif not self.release is None:
                self.update_release()
            elif not self.trunk is None:
                self.update_trunk()
        else:
            self.pkgdir=self.stable
            self.pkgroot=self.stable_root
            print "-----------------------------------------------------------------"
            print "  Updating source for package",self.name
            print "     Subversion dir: "+self.stable
            print "     Source dir:     "+dir
            print "-----------------------------------------------------------------"
            self.run([self.svn,'update','-q',dir])
            self.run([self.python, 'setup.py', 'develop'], dir=dir)

    def update_release(self, dir=None):
        if self.release is None:
            if not self.pypi is None:
                self.easy_upgrade()
            elif not self.stable is None:
                self.update_stable()
            elif not self.trunk is None:
                self.update_trunk()
        else:
            self.pkgdir=self.release
            self.pkgroot=self.release_root
            print "-----------------------------------------------------------------"
            print "  Updating source for package",self.name
            print "     Subversion dir: "+self.release
            print "     Source dir:     "+dir
            print "-----------------------------------------------------------------"
            self.run([self.svn,'update','-q',dir])
            self.run([self.python, 'setup.py', 'install'], dir=dir)

    def Xsdist_trunk(self, format='zip'):
        if self.trunk is None:
            if not self.pypi is None:
                self.easy_install()
            elif not self.stable is None:
                self.sdist_stable(format=format)
            else:
                self.sdist_release(format=format)
        else:
            self.pkgdir=self.trunk
            self.pkgroot=self.trunk_root
            print "-----------------------------------------------------------------"
            print "  Checking out source for package",self.name
            print "     Subversion dir: "+self.trunk
            print "-----------------------------------------------------------------"
            self.run([self.svn,'export','-q',self.trunk, 'pkg'+self.name])
            self.run([self.python, 'setup.py', 'sdist','-q','--dist-dir=..', '--formats='+format], dir='pkg'+self.name)
            os.chdir('..')
            rmtree('pkg'+self.name)

    def Xsdist_stable(self, format='zip'):
        if self.stable is None:
            if not self.pypi is None:
                self.easy_install()
            elif not self.release is None:
                self.install_release()
            elif not self.trunk is None:
                self.install_trunk()
        else:
            self.pkgdir=self.stable
            self.pkgroot=self.stable_root
            print "-----------------------------------------------------------------"
            print "  Checking out source for package",self.name
            print "     Subversion dir: "+self.stable
            print "     Source dir:     "+dir
            print "-----------------------------------------------------------------"
            self.run([self.svn,'checkout','-q',self.stable, dir])
            self.run([self.python, 'setup.py', 'develop'], dir=dir)

    def Xsdist_release(self, dir=None):
        if self.release is None:
            if not self.pypi is None:
                self.easy_install()
            elif not self.stable is None:
                self.install_stable()
            elif not self.trunk is None:
                self.install_trunk()
        else:
            self.pkgdir=self.release
            self.pkgroot=self.release_root
            print "-----------------------------------------------------------------"
            print "  Checking out source for package",self.name
            print "     Subversion dir: "+self.release
            print "     Source dir:     "+dir
            print "-----------------------------------------------------------------"
            self.run([self.svn,'checkout','-q',self.release, dir])
            self.run([self.python, 'setup.py', 'install'], dir=dir)

    def easy_install(self, setup, dir):
        if setup:
            if not os.path.exists(dir):
                self.run([self.easy_install_path, '-q', self.pypi])
            else:
                self.run([self.python, 'setup.py', 'install'], dir=dir)
        else: 
            if not os.path.exists(dir):
                self.run([self.easy_install_path, '-q', '--editable', '--build-directory', '.', self.pypi], dir=os.path.dirname(dir))

    def easy_upgrade(self):
        self.run([self.easy_install_path, '-q', '--upgrade', self.pypi])

    def run(self, cmd, dir=None):
        if not dir is None:
            cwd=os.getcwd()
            os.chdir(dir)
        print "Running command '%s'" % " ".join(cmd)
        call_subprocess(cmd, filter_stdout=filter_python_develop, show_stdout=True)
        if not dir is None:
            os.chdir(cwd)


if sys.platform.startswith('win'):
   Repository.python += '.exe'
   Repository.svn += '.exe'


def filter_python_develop(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.NOTIFY



wrapper = textwrap.TextWrapper(subsequent_indent="    ")


class Installer(object):

    def __init__(self):
        self.description="This script manages the installation of packages into a virtual Python installation."
        self.home_dir = None
        self.default_dirname='python'
        self.abshome_dir = None
        self.sw_packages = []
        self.sw_dict = {}
        self.cmd_files = []
        self.auxdir = []
        self.README="""
#
# Virtual Python installation generated by the %s script.
#
# This directory is managed with virtualenv, which creates a
# virtual Python installation.  If the 'bin' directory is put in
# user's PATH environment, then the bin/python command can be used
# without further installation.
#
# Directories:
#   admin      Administrative data for maintaining this distribution
#   bin        Scripts and executables
#   dist       Python packages that are not intended for development
#   include    Python header files
#   lib        Python libraries and installed packages
#   src        Python packages whose source files can be
#              modified and used directly within this virtual Python
#              installation.
#   Scripts    Python bin directory (used on MS Windows)
#
""" % sys.argv[0]

    def add_repository(self, *args, **kwds):
        repos = Repository( *args, **kwds)
        self.sw_dict[repos.name] = repos
        self.sw_packages.append( repos )

    def add_dos_cmd(self, file):
        self.cmd_files.append( file )

    def add_auxdir(self, package, todir, fromdir):
        self.auxdir.append( (todir, package, fromdir) )

    def modify_parser(self, parser):
        self.default_windir = 'C:\\'+self.default_dirname
        self.default_unixdir = './'+self.default_dirname
        #
        parser.add_option('--trunk',
            help='Install trunk branches of Python software.',
            action='store_true',
            dest='trunk',
            default=False)

        parser.add_option('--stable',
            help='Install stable branches of Python software.',
            action='store_true',
            dest='stable',
            default=False)

        parser.add_option('--update',
            help='Update all Python packages.',
            action='store_true',
            dest='update',
            default=False)

        parser.add_option('--proxy',
            help='Set the HTTP_PROXY environment with this option.',
            action='store',
            dest='proxy',
            default=None)

        parser.add_option('--preinstall',
            help='Prepare an installation that will be used to build a MS Windows installer.',
            action='store_true',
            dest='preinstall',
            default=False)

        parser.add_option('--offline',
            help='Perform installation offline, using source extracted from ZIP files.',
            action='store_true',
            dest='offline',
            default=False)

        parser.add_option('--zip',
            help='Add ZIP files that are use define this installation.',
            action='append',
            dest='zip',
            default=[])

        parser.add_option('--forum-pkg',
            help='Use one or more packages from the Coopr Forum.  Multiple packages are specified with a comma-separated list.',
            action='store',
            dest='forum',
            default='')

        parser.add_option('--forum-dev',
            help="Explicitly indicate which of the Coopr Forum packages are treated as development packages.  By default, no Coopr Forum packages are treated this way; packages omited from this list are installed from their latest 'tags' branch.  Multiple packages are specified with a comma-separated list.",
            action='store',
            dest='forumdev',
            default='')

        parser.add_option('--use-pythonpath',
            help="By default, the PYTHONPATH is ignored when installing.  This option allows the 'easy_install' tool to search this path for related Python packages, which are then installed.",
            action='store_true',
            dest='use_pythonpath',
            default=False)

        parser.add_option(
            '--site-packages',
            dest='no_site_packages',
            action='store_false',
            help="Setup the virtual environment to use the global site-packages",
            default=True)

        #
        # Change the virtualenv options
        #
        parser.get_option("--python").help = "Specify the Python interpreter to use, e.g., --python=python2.5 will install with the python2.5 interpreter."
        parser.get_option("--clear").help = "Remove the existing installation and reinstall from scratch."
        parser.remove_option("--relocatable")
        parser.remove_option("--version")
        parser.remove_option("--unzip-setuptools")
        parser.remove_option("--no-site-packages")
        #
        # Add description 
        #
        parser.description=self.description
        parser.epilog="If DEST_DIR is not specified, then a default installation path is used:  "+self.default_windir+" on Windows and "+self.default_unixdir+" on Linux.  This command uses the Python 'setuptools' package to install Python packages.  This package installs packages by downloading files from the internet.  If you are running this from within a firewall, you may need to set the HTTP_PROXY environment variable to a value like 'http://<proxyhost>:<port>'."
        

    def adjust_options(self, options, args):
        #
        global logger
        verbosity = options.verbose - options.quiet
        self.logger = Logger([(Logger.level_for_integer(2-verbosity), sys.stdout)])
        logger = self.logger
        #
        if options.update and (options.stable or options.trunk):
            self.logger.fatal("ERROR: cannot specify --stable or --trunk when specifying the --update option.")
            sys.exit(1000)
        if len(args) > 1:
            self.logger.fatal("ERROR: "+self.installer.name+" can only have one argument")
            sys.exit(1000)
        #
        # Error checking
        #
        if not options.preinstall and (os.path.exists(self.abshome_dir) ^ options.update):
            if options.update:
                self.logger.fatal(wrapper.fill("ERROR: The 'update' option is specified, but the installation path '%s' does not exist!" % self.home_dir))
                sys.exit(1000)
            elif not options.clear and os.path.exists(join(self.abshome_dir,'bin')):
                    self.logger.fatal(wrapper.fill("ERROR: The installation path '%s' already exists!  Use the --update option if you wish to update, or use --clear to create a fresh installation." % self.home_dir))
                    sys.exit(1000)
        if len(args) == 0:
            args.append(self.abshome_dir)

    def get_homedir(self, options, args):
        #
        # Figure out the installation directory
        #
        if len(args) == 0:
            path = self.guess_path()
            if path is None or options.preinstall:
                # Install in a default location.
                if sys.platform == 'win32':
                    home_dir = self.default_windir
                else:
                    home_dir = self.default_unixdir
            else:
                home_dir = os.path.dirname(os.path.dirname(path))
        else:
            home_dir = args[0]
        self.home_dir = home_dir
        self.abshome_dir = os.path.abspath(home_dir)

    def guess_path(self):
        return None

    def setup_installer(self, options):
        if options.preinstall:
            print "Creating preinstall zip file in '%s'" % self.home_dir
        elif options.update:
            print "Updating existing installation in '%s'" % self.home_dir
        else:
            print "Starting fresh installation in '%s'" % self.home_dir
        #
        # Setup HTTP proxy
        #
        if not options.preinstall:
            if not options.proxy is None:
                os.environ['HTTP_PROXY'] = options.proxy
            print "  using the HTTP_PROXY environment: %s" % os.environ.get('HTTP_PROXY',"''")
            print ""
        #
        # Disable the PYTHONPATH, to isolate this installation from 
        # other Python installations that a user may be working with.
        #
        if not options.use_pythonpath:
            try:
                del os.environ["PYTHONPATH"]
            except:
                pass
        #
        # If --preinstall is declared, then we remove the directory, and prepare a ZIP file
        # that contains the full installation.
        #
        if options.preinstall:
            print "-----------------------------------------------------------------"
            print " STARTING preinstall in directory %s" % self.home_dir
            print "-----------------------------------------------------------------"
            rmtree(self.abshome_dir)
            os.mkdir(self.abshome_dir)
        #
        # If we're clearing the current installation, then remove a bunch of
        # directories
        #
        elif options.clear:
            path = join(self.abshome_dir,'src')
            if os.path.exists(path):
                rmtree(path)
        #
        # Open up zip files
        #
        for file in options.zip:
            unzip_file(file, dir=self.abshome_dir)

        if options.preinstall or not options.offline:
            self.get_packages(options)

    def get_packages(self, options):
        #
        # Setup the 'admin' directory
        #
        if not os.path.exists(self.abshome_dir):
            os.mkdir(self.abshome_dir)
        if not os.path.exists(join(self.abshome_dir,'admin')):
            os.mkdir(join(self.abshome_dir,'admin'))
        if options.update:
            INPUT=open(join(self.abshome_dir,'admin',"virtualenv.cfg"),'r')
            options.trunk = INPUT.readline().strip() != 'False'
            options.stable = INPUT.readline().strip() != 'False'
            INPUT.close()
        else:
            OUTPUT=open(join(self.abshome_dir,'admin',"virtualenv.cfg"),'w')
            print >>OUTPUT, options.trunk
            print >>OUTPUT, options.stable
            OUTPUT.close()
        #
        # Setup package directories
        #
        if not os.path.exists(join(self.abshome_dir,'dist')):
            os.mkdir(join(self.abshome_dir,'dist'))
        if not os.path.exists(self.abshome_dir+os.sep+"src"):
            os.mkdir(self.abshome_dir+os.sep+"src")
        if not os.path.exists(self.abshome_dir+os.sep+"bin"):
            os.mkdir(self.abshome_dir+os.sep+"bin")
        #
        # Get source packages
        #
        if options.preinstall:
            #
            # When preinstalling, disable the default install_setuptools() function,
            # and add the setuptools package to the installation list
            #
            install_setuptools.use_default=False
            self.sw_packages.insert( 0, Repository('setuptools', pypi='setuptools') )
        #
        # Add Coopr Forum packages
        #
        dev = options.forumdev.split(',')
        for pkg in options.forum.split(','):
            if pkg is '':
                continue
            if pkg in dev:
                if (options.trunk or options.stable):
                    self.sw_packages[pkg] = 'http://coopr-forum.googlecode.com/svn/'+pkg
                else:
                    self.sw_packages[pkg] = '-f http://coopr-forum.googlecode.com/svn/'+pkg+'/trunk '+pkg
                dev_packages.append(pkg)
            else:
                try:
                    self.sw_packages[pkg] = guess_release('http://coopr-forum.googlecode.com/svn/'+pkg+'/dev/')
                except Exception, err:
                    print "-----------------------------------------------------------------"
                    print "ERROR Finding 'tags' branch for Coopr Forum Package %s: %s" % (pkg,str(err))
                    print "-----------------------------------------------------------------"
        #
        # Get package source
        #
        for pkg in self.sw_packages:
            if pkg.dev:
                tmp = join(self.abshome_dir,'src',pkg.name)
            else:
                tmp = join(self.abshome_dir,'dist',pkg.name)
            if options.trunk:
                if not options.update:
                    pkg.install_trunk(dir=tmp, setup=False)
            elif options.stable:
                if not options.update:
                    pkg.install_stable(dir=tmp, setup=False)
            else:
                if not options.update:
                    pkg.install_release(dir=tmp, setup=False)
        if options.update or not os.path.exists(join(self.abshome_dir,'doc')):
            self.install_auxdirs(options)
        #
        # Create a README.txt file
        #
        OUTPUT=open(join(self.abshome_dir,"README.txt"),"w")
        print >>OUTPUT, self.README.strip()
        OUTPUT.close()
        #
        # Finalize preinstall
        #
        if options.preinstall:
            print "-----------------------------------------------------------------"
            print " FINISHED preinstall in directory %s" % self.home_dir
            print "-----------------------------------------------------------------"
            os.chdir(self.abshome_dir)
            zip_file(self.default_dirname+'.zip', ['.'])
            sys.exit(0)

        
    def install_packages(self, options):
        #
        # Set the bin directory
        #
        if os.path.exists(self.abshome_dir+os.sep+"Scripts"):
            bindir = join(self.abshome_dir,"Scripts")
        else:
            bindir = join(self.abshome_dir,"bin")
        Repository.easy_install_path = os.path.abspath(join(bindir, 'easy_install'))
        Repository.python = os.path.abspath(join(bindir, 'python'))
        #
        # Install the related packages
        #
        for pkg in self.sw_packages:
            if pkg.dev:
                srcdir = join(self.abshome_dir,'src',pkg.name)
            else:
                srcdir = join(self.abshome_dir,'dist',pkg.name)
            if options.trunk:
                if options.update:
                    pkg.update_trunk(dir=srcdir)
                else:
                    pkg.install_trunk(dir=srcdir)
            elif options.stable:
                if options.update:
                    pkg.update_stable(dir=srcdir)
                else:
                    pkg.install_stable(dir=srcdir)
            else:
                if options.update:
                    pkg.update_release(dir=srcdir)
                else:
                    pkg.install_release(dir=srcdir)
        #
        # Copy the <env>/Scripts/* files into <env>/bin
        #
        if os.path.exists(self.abshome_dir+os.sep+"Scripts"):
            for file in glob.glob(self.abshome_dir+os.sep+"Scripts"+os.sep+"*"):
                shutil.copy(file, self.abshome_dir+os.sep+"bin")
        #
        # Localize DOS cmd files
        #
        self.localize_cmd_files(self.abshome_dir)
        #
        # Misc notifications
        #
        if not options.update:
            print ""
            print "-----------------------------------------------------------------"
            print "  Add %s to the PATH environment variable" % (self.home_dir+os.sep+"bin")
            print "-----------------------------------------------------------------"
        print ""
        print "Finished installation in '%s'" % self.home_dir

    def localize_cmd_files(self, dir):
        """
        Hard-code the path to Python that is used in the Python CMD files that
        are installed.
        """
        if not sys.platform.startswith('win'):
            return
        for file in self.cmd_files:
            INPUT = open(join(dir,'bin',file), 'r')
            content = "".join(INPUT.readlines())
            INPUT.close()
            content = content.replace('__VIRTUAL_ENV__',dir)
            OUTPUT = open(join(dir,'bin',file), 'w')
            OUTPUT.write(content)
            OUTPUT.close()

    def svnjoin(*args):
        return '/'.join(args[1:])

    def install_auxdirs(self, options):
        for todir,pkg,fromdir in self.auxdir:
            pkgroot = self.sw_dict[pkg].pkgroot
            if options.update:
                cmd = [Repository.svn,'update','-q',self.svnjoin(self.abshome_dir, todir)]
            else:
                if options.clear:
                    rmtree( join(self.abshome_dir,todir) )
                cmd = [Repository.svn,'checkout','-q',self.svnjoin(pkgroot,fromdir),join(self.abshome_dir,todir)]
            print "Running command '%s'" % " ".join(cmd)
            call_subprocess(cmd, filter_stdout=filter_python_develop,show_stdout=True)


def configure(installer):
    """
    A dummy configuration function.
    """
    return installer

def create_installer():
    return Installer()

def get_installer():
    """
    Return an instance of the installer object.  If this object
    does not already exist, then create the object and use the
    configure() function to customize it based on the end-user's
    needs.

    The argument to this function is the class type that will be
    constructed if needed.
    """
    try:
        return get_installer.installer
    except:
        get_installer.installer = configure( create_installer() )
        return get_installer.installer
    

#
# This is a monkey patch, to control the execution of the install_setuptools()
# function that is defined by virtualenv.
#
default_install_setuptools = install_setuptools

def install_setuptools(py_executable, unzip=False):
    if install_setuptools.use_default:
        default_install_setuptools(py_executable, unzip)

install_setuptools.use_default=True


#
# The following methods will be called by virtualenv
#
def extend_parser(parser):
    installer = get_installer()
    installer.modify_parser(parser)

def adjust_options(options, args):
    installer = get_installer()
    installer.get_homedir(options, args)
    installer.adjust_options(options, args)
    installer.setup_installer(options)
    
def after_install(options, home_dir):
    installer = get_installer()
    installer.install_packages(options)

