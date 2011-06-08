#!/usr/bin/env python
## WARNING: This file is generated
#!/usr/bin/env python
"""Create a "virtual" Python installation
"""

# If you change the version here, change it in setup.py 
# and docs/conf.py as well.
virtualenv_version = "1.6.1"

import base64
import sys
import os
import optparse
import re
import shutil
import logging
import tempfile
import zlib
import errno
import distutils.sysconfig
try:
    import subprocess
except ImportError:
    if sys.version_info <= (2, 3):
        print('ERROR: %s' % sys.exc_info()[1])
        print('ERROR: this script requires Python 2.4 or greater; or at least the subprocess module.')
        print('If you copy subprocess.py from a newer version of Python this script will probably work')
        sys.exit(101)
    else:
        raise
try:
    set
except NameError:
    from sets import Set as set
try:
    basestring
except NameError:
    basestring = str

join = os.path.join
py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])

is_jython = sys.platform.startswith('java')
is_pypy = hasattr(sys, 'pypy_version_info')
abiflags = getattr(sys, 'abiflags', '')

if is_pypy:
    expected_exe = 'pypy'
elif is_jython:
    expected_exe = 'jython'
else:
    expected_exe = 'python'


REQUIRED_MODULES = ['os', 'posix', 'posixpath', 'nt', 'ntpath', 'genericpath',
                    'fnmatch', 'locale', 'encodings', 'codecs',
                    'stat', 'UserDict', 'readline', 'copy_reg', 'types',
                    're', 'sre', 'sre_parse', 'sre_constants', 'sre_compile',
                    'zlib']

REQUIRED_FILES = ['lib-dynload', 'config']

majver, minver = sys.version_info[:2]
if majver == 2:
    if minver >= 6:
        REQUIRED_MODULES.extend(['warnings', 'linecache', '_abcoll', 'abc'])
    if minver >= 7:
        REQUIRED_MODULES.extend(['_weakrefset'])
    if minver <= 3:
        REQUIRED_MODULES.extend(['sets', '__future__'])
elif majver == 3:
    # Some extra modules are needed for Python 3, but different ones
    # for different versions.
    REQUIRED_MODULES.extend(['_abcoll', 'warnings', 'linecache', 'abc', 'io',
                             '_weakrefset', 'copyreg', 'tempfile', 'random',
                             '__future__', 'collections', 'keyword', 'tarfile',
                             'shutil', 'struct', 'copy'])
    if minver >= 2:
        REQUIRED_FILES[-1] = 'config-%s' % majver
    if minver == 3:
        # The whole list of 3.3 modules is reproduced below - the current
        # uncommented ones are required for 3.3 as of now, but more may be
        # added as 3.3 development continues.
        REQUIRED_MODULES.extend([
            #"aifc",
            #"antigravity",
            #"argparse",
            #"ast",
            #"asynchat",
            #"asyncore",
            "base64",
            #"bdb",
            #"binhex",
            "bisect",
            #"calendar",
            #"cgi",
            #"cgitb",
            #"chunk",
            #"cmd",
            #"codeop",
            #"code",
            #"colorsys",
            #"_compat_pickle",
            #"compileall",
            #"concurrent",
            #"configparser",
            #"contextlib",
            #"cProfile",
            #"crypt",
            #"csv",
            #"ctypes",
            #"curses",
            #"datetime",
            #"dbm",
            #"decimal",
            #"difflib",
            #"dis",
            #"doctest",
            #"dummy_threading",
            #"_dummy_thread",
            #"email",
            #"filecmp",
            #"fileinput",
            #"formatter",
            #"fractions",
            #"ftplib",
            #"functools",
            #"getopt",
            #"getpass",
            #"gettext",
            #"glob",
            #"gzip",
            "hashlib",
            "heapq",
            "hmac",
            #"html",
            #"http",
            #"idlelib",
            #"imaplib",
            #"imghdr",
            #"importlib",
            #"inspect",
            #"json",
            #"lib2to3",
            #"logging",
            #"macpath",
            #"macurl2path",
            #"mailbox",
            #"mailcap",
            #"_markupbase",
            #"mimetypes",
            #"modulefinder",
            #"multiprocessing",
            #"netrc",
            #"nntplib",
            #"nturl2path",
            #"numbers",
            #"opcode",
            #"optparse",
            #"os2emxpath",
            #"pdb",
            #"pickle",
            #"pickletools",
            #"pipes",
            #"pkgutil",
            #"platform",
            #"plat-linux2",
            #"plistlib",
            #"poplib",
            #"pprint",
            #"profile",
            #"pstats",
            #"pty",
            #"pyclbr",
            #"py_compile",
            #"pydoc_data",
            #"pydoc",
            #"_pyio",
            #"queue",
            #"quopri",
            "reprlib",
            "rlcompleter",
            #"runpy",
            #"sched",
            #"shelve",
            #"shlex",
            #"smtpd",
            #"smtplib",
            #"sndhdr",
            #"socket",
            #"socketserver",
            #"sqlite3",
            #"ssl",
            #"stringprep",
            #"string",
            #"_strptime",
            #"subprocess",
            #"sunau",
            #"symbol",
            #"symtable",
            #"sysconfig",
            #"tabnanny",
            #"telnetlib",
            #"test",
            #"textwrap",
            #"this",
            #"_threading_local",
            #"threading",
            #"timeit",
            #"tkinter",
            #"tokenize",
            #"token",
            #"traceback",
            #"trace",
            #"tty",
            #"turtledemo",
            #"turtle",
            #"unittest",
            #"urllib",
            #"uuid",
            #"uu",
            #"wave",
            "weakref",
            #"webbrowser",
            #"wsgiref",
            #"xdrlib",
            #"xml",
            #"xmlrpc",
            #"zipfile",
        ])

if is_pypy:
    # these are needed to correctly display the exceptions that may happen
    # during the bootstrap
    REQUIRED_MODULES.extend(['traceback', 'linecache'])

class Logger(object):

    """
    Logging object for use in command-line script.  Allows ranges of
    levels, to avoid some redundancy of displayed information.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    NOTIFY = (logging.INFO+logging.WARN)/2
    WARN = WARNING = logging.WARN
    ERROR = logging.ERROR
    FATAL = logging.FATAL

    LEVELS = [DEBUG, INFO, NOTIFY, WARN, ERROR, FATAL]

    def __init__(self, consumers):
        self.consumers = consumers
        self.indent = 0
        self.in_progress = None
        self.in_progress_hanging = False

    def debug(self, msg, *args, **kw):
        self.log(self.DEBUG, msg, *args, **kw)
    def info(self, msg, *args, **kw):
        self.log(self.INFO, msg, *args, **kw)
    def notify(self, msg, *args, **kw):
        self.log(self.NOTIFY, msg, *args, **kw)
    def warn(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def error(self, msg, *args, **kw):
        self.log(self.WARN, msg, *args, **kw)
    def fatal(self, msg, *args, **kw):
        self.log(self.FATAL, msg, *args, **kw)
    def log(self, level, msg, *args, **kw):
        if args:
            if kw:
                raise TypeError(
                    "You may give positional or keyword arguments, not both")
        args = args or kw
        rendered = None
        for consumer_level, consumer in self.consumers:
            if self.level_matches(level, consumer_level):
                if (self.in_progress_hanging
                    and consumer in (sys.stdout, sys.stderr)):
                    self.in_progress_hanging = False
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                if rendered is None:
                    if args:
                        rendered = msg % args
                    else:
                        rendered = msg
                    rendered = ' '*self.indent + rendered
                if hasattr(consumer, 'write'):
                    consumer.write(rendered+'\n')
                else:
                    consumer(rendered)

    def start_progress(self, msg):
        assert not self.in_progress, (
            "Tried to start_progress(%r) while in_progress %r"
            % (msg, self.in_progress))
        if self.level_matches(self.NOTIFY, self._stdout_level()):
            sys.stdout.write(msg)
            sys.stdout.flush()
            self.in_progress_hanging = True
        else:
            self.in_progress_hanging = False
        self.in_progress = msg

    def end_progress(self, msg='done.'):
        assert self.in_progress, (
            "Tried to end_progress without start_progress")
        if self.stdout_level_matches(self.NOTIFY):
            if not self.in_progress_hanging:
                # Some message has been printed out since start_progress
                sys.stdout.write('...' + self.in_progress + msg + '\n')
                sys.stdout.flush()
            else:
                sys.stdout.write(msg + '\n')
                sys.stdout.flush()
        self.in_progress = None
        self.in_progress_hanging = False

    def show_progress(self):
        """If we are in a progress scope, and no log messages have been
        shown, write out another '.'"""
        if self.in_progress_hanging:
            sys.stdout.write('.')
            sys.stdout.flush()

    def stdout_level_matches(self, level):
        """Returns true if a message at this level will go to stdout"""
        return self.level_matches(level, self._stdout_level())

    def _stdout_level(self):
        """Returns the level that stdout runs at"""
        for level, consumer in self.consumers:
            if consumer is sys.stdout:
                return level
        return self.FATAL

    def level_matches(self, level, consumer_level):
        """
        >>> l = Logger()
        >>> l.level_matches(3, 4)
        False
        >>> l.level_matches(3, 2)
        True
        >>> l.level_matches(slice(None, 3), 3)
        False
        >>> l.level_matches(slice(None, 3), 2)
        True
        >>> l.level_matches(slice(1, 3), 1)
        True
        >>> l.level_matches(slice(2, 3), 1)
        False
        """
        if isinstance(level, slice):
            start, stop = level.start, level.stop
            if start is not None and start > consumer_level:
                return False
            if stop is not None or stop <= consumer_level:
                return False
            return True
        else:
            return level >= consumer_level

    #@classmethod
    def level_for_integer(cls, level):
        levels = cls.LEVELS
        if level < 0:
            return levels[0]
        if level >= len(levels):
            return levels[-1]
        return levels[level]

    level_for_integer = classmethod(level_for_integer)

# create a silent logger just to prevent this from being undefined
# will be overridden with requested verbosity main() is called.
logger = Logger([(Logger.LEVELS[-1], sys.stdout)])

def mkdir(path):
    if not os.path.exists(path):
        logger.info('Creating %s', path)
        os.makedirs(path)
    else:
        logger.info('Directory %s already exists', path)

def copyfileordir(src, dest):
    if os.path.isdir(src):
        shutil.copytree(src, dest, True)
    else:
        shutil.copy2(src, dest)

def copyfile(src, dest, symlink=True):
    if not os.path.exists(src):
        # Some bad symlink in the src
        logger.warn('Cannot find file %s (bad symlink)', src)
        return
    if os.path.exists(dest):
        logger.debug('File %s already exists', dest)
        return
    if not os.path.exists(os.path.dirname(dest)):
        logger.info('Creating parent directories for %s' % os.path.dirname(dest))
        os.makedirs(os.path.dirname(dest))
    if not os.path.islink(src):
        srcpath = os.path.abspath(src)
    else:
        srcpath = os.readlink(src)
    if symlink and hasattr(os, 'symlink'):
        logger.info('Symlinking %s', dest)
        try:
            os.symlink(srcpath, dest)
        except (OSError, NotImplementedError):
            logger.info('Symlinking failed, copying to %s', dest)
            copyfileordir(src, dest)
    else:
        logger.info('Copying to %s', dest)
        copyfileordir(src, dest)

def writefile(dest, content, overwrite=True):
    if not os.path.exists(dest):
        logger.info('Writing %s', dest)
        f = open(dest, 'wb')
        f.write(content.encode('utf-8'))
        f.close()
        return
    else:
        f = open(dest, 'rb')
        c = f.read()
        f.close()
        if c != content:
            if not overwrite:
                logger.notify('File %s exists with different content; not overwriting', dest)
                return
            logger.notify('Overwriting %s with new content', dest)
            f = open(dest, 'wb')
            f.write(content.encode('utf-8'))
            f.close()
        else:
            logger.info('Content %s already in place', dest)

def rmtree(dir):
    if os.path.exists(dir):
        logger.notify('Deleting tree %s', dir)
        shutil.rmtree(dir)
    else:
        logger.info('Do not need to delete %s; already gone', dir)

def make_exe(fn):
    if hasattr(os, 'chmod'):
        oldmode = os.stat(fn).st_mode & 0xFFF # 0o7777
        newmode = (oldmode | 0x16D) & 0xFFF # 0o555, 0o7777
        os.chmod(fn, newmode)
        logger.info('Changed mode of %s to %s', fn, oct(newmode))

def _find_file(filename, dirs):
    for dir in dirs:
        if os.path.exists(join(dir, filename)):
            return join(dir, filename)
    return filename

def _install_req(py_executable, unzip=False, distribute=False,
                 search_dirs=None, never_download=False):

    if search_dirs is None:
        search_dirs = file_search_dirs()

    if not distribute:
        setup_fn = 'setuptools-0.6c11-py%s.egg' % sys.version[:3]
        project_name = 'setuptools'
        bootstrap_script = EZ_SETUP_PY
        source = None
    else:
        setup_fn = None
        source = 'distribute-0.6.16.tar.gz'
        project_name = 'distribute'
        bootstrap_script = DISTRIBUTE_SETUP_PY
        try:
            # check if the global Python has distribute installed or plain
            # setuptools
            import pkg_resources
            if not hasattr(pkg_resources, '_distribute'):
                location = os.path.dirname(pkg_resources.__file__)
                logger.notify("A globally installed setuptools was found (in %s)" % location)
                logger.notify("Use the --no-site-packages option to use distribute in "
                              "the virtualenv.")
        except ImportError:
            pass

    if setup_fn is not None:
        setup_fn = _find_file(setup_fn, search_dirs)

    if source is not None:
        source = _find_file(source, search_dirs)

    if is_jython and os._name == 'nt':
        # Jython's .bat sys.executable can't handle a command line
        # argument with newlines
        fd, ez_setup = tempfile.mkstemp('.py')
        os.write(fd, bootstrap_script)
        os.close(fd)
        cmd = [py_executable, ez_setup]
    else:
        cmd = [py_executable, '-c', bootstrap_script]
    if unzip:
        cmd.append('--always-unzip')
    env = {}
    remove_from_env = []
    if logger.stdout_level_matches(logger.DEBUG):
        cmd.append('-v')

    old_chdir = os.getcwd()
    if setup_fn is not None and os.path.exists(setup_fn):
        logger.info('Using existing %s egg: %s' % (project_name, setup_fn))
        cmd.append(setup_fn)
        if os.environ.get('PYTHONPATH'):
            env['PYTHONPATH'] = setup_fn + os.path.pathsep + os.environ['PYTHONPATH']
        else:
            env['PYTHONPATH'] = setup_fn
    else:
        # the source is found, let's chdir
        if source is not None and os.path.exists(source):
            logger.info('Using existing %s egg: %s' % (project_name, source))
            os.chdir(os.path.dirname(source))
            # in this case, we want to be sure that PYTHONPATH is unset (not
            # just empty, really unset), else CPython tries to import the
            # site.py that it's in virtualenv_support
            remove_from_env.append('PYTHONPATH')
        else:
            if never_download:
                logger.fatal("Can't find any local distributions of %s to install "
                             "and --never-download is set.  Either re-run virtualenv "
                             "without the --never-download option, or place a %s "
                             "distribution (%s) in one of these "
                             "locations: %r" % (project_name, project_name, 
                                                setup_fn or source,
                                                search_dirs))
                sys.exit(1)

            logger.info('No %s egg found; downloading' % project_name)
        cmd.extend(['--always-copy', '-U', project_name])
    logger.start_progress('Installing %s...' % project_name)
    logger.indent += 2
    cwd = None
    if project_name == 'distribute':
        env['DONT_PATCH_SETUPTOOLS'] = 'true'

    def _filter_ez_setup(line):
        return filter_ez_setup(line, project_name)

    if not os.access(os.getcwd(), os.W_OK):
        cwd = tempfile.mkdtemp()
        if source is not None and os.path.exists(source):
            # the current working dir is hostile, let's copy the
            # tarball to a temp dir
            target = os.path.join(cwd, os.path.split(source)[-1])
            shutil.copy(source, target)
    try:
        call_subprocess(cmd, show_stdout=False,
                        filter_stdout=_filter_ez_setup,
                        extra_env=env,
                        remove_from_env=remove_from_env,
                        cwd=cwd)
    finally:
        logger.indent -= 2
        logger.end_progress()
        if os.getcwd() != old_chdir:
            os.chdir(old_chdir)
        if is_jython and os._name == 'nt':
            os.remove(ez_setup)

def file_search_dirs():
    here = os.path.dirname(os.path.abspath(__file__))
    dirs = ['.', here,
            join(here, 'virtualenv_support')]
    if os.path.splitext(os.path.dirname(__file__))[0] != 'virtualenv':
        # Probably some boot script; just in case virtualenv is installed...
        try:
            import virtualenv
        except ImportError:
            pass
        else:
            dirs.append(os.path.join(os.path.dirname(virtualenv.__file__), 'virtualenv_support'))
    return [d for d in dirs if os.path.isdir(d)]

def install_setuptools(py_executable, unzip=False,
                       search_dirs=None, never_download=False):
    _install_req(py_executable, unzip, 
                 search_dirs=search_dirs, never_download=never_download)

def install_distribute(py_executable, unzip=False, 
                       search_dirs=None, never_download=False):
    _install_req(py_executable, unzip, distribute=True, 
                 search_dirs=search_dirs, never_download=never_download)

_pip_re = re.compile(r'^pip-.*(zip|tar.gz|tar.bz2|tgz|tbz)$', re.I)
def install_pip(py_executable, search_dirs=None, never_download=False):    
    if search_dirs is None:
        search_dirs = file_search_dirs()

    filenames = []
    for dir in search_dirs:
        filenames.extend([join(dir, fn) for fn in os.listdir(dir)
                          if _pip_re.search(fn)])
    filenames = [(os.path.basename(filename).lower(), i, filename) for i, filename in enumerate(filenames)]
    filenames.sort()
    filenames = [filename for basename, i, filename in filenames]
    if not filenames:
        filename = 'pip'
    else:
        filename = filenames[-1]
    easy_install_script = 'easy_install'
    if sys.platform == 'win32':
        easy_install_script = 'easy_install-script.py'
    cmd = [py_executable, join(os.path.dirname(py_executable), easy_install_script), filename]
    if filename == 'pip':
        if never_download:
            logger.fatal("Can't find any local distributions of pip to install "
                         "and --never-download is set.  Either re-run virtualenv "
                         "without the --never-download option, or place a pip "
                         "source distribution (zip/tar.gz/tar.bz2) in one of these "
                         "locations: %r" % search_dirs)
            sys.exit(1)
        logger.info('Installing pip from network...')
    else:
        logger.info('Installing existing %s distribution: %s' % (
                os.path.basename(filename), filename))
    logger.start_progress('Installing pip...')
    logger.indent += 2
    def _filter_setup(line):
        return filter_ez_setup(line, 'pip')
    try:
        call_subprocess(cmd, show_stdout=False,
                        filter_stdout=_filter_setup)
    finally:
        logger.indent -= 2
        logger.end_progress()

def filter_ez_setup(line, project_name='setuptools'):
    if not line.strip():
        return Logger.DEBUG
    if project_name == 'distribute':
        for prefix in ('Extracting', 'Now working', 'Installing', 'Before',
                       'Scanning', 'Setuptools', 'Egg', 'Already',
                       'running', 'writing', 'reading', 'installing',
                       'creating', 'copying', 'byte-compiling', 'removing',
                       'Processing'):
            if line.startswith(prefix):
                return Logger.DEBUG
        return Logger.DEBUG
    for prefix in ['Reading ', 'Best match', 'Processing setuptools',
                   'Copying setuptools', 'Adding setuptools',
                   'Installing ', 'Installed ']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.INFO

def main():
    parser = optparse.OptionParser(
        version=virtualenv_version,
        usage="%prog [OPTIONS] DEST_DIR")

    parser.add_option(
        '-v', '--verbose',
        action='count',
        dest='verbose',
        default=0,
        help="Increase verbosity")

    parser.add_option(
        '-q', '--quiet',
        action='count',
        dest='quiet',
        default=0,
        help='Decrease verbosity')

    parser.add_option(
        '-p', '--python',
        dest='python',
        metavar='PYTHON_EXE',
        help='The Python interpreter to use, e.g., --python=python2.5 will use the python2.5 '
        'interpreter to create the new environment.  The default is the interpreter that '
        'virtualenv was installed with (%s)' % sys.executable)

    parser.add_option(
        '--clear',
        dest='clear',
        action='store_true',
        help="Clear out the non-root install and start from scratch")

    parser.add_option(
        '--no-site-packages',
        dest='no_site_packages',
        action='store_true',
        help="Don't give access to the global site-packages dir to the "
             "virtual environment")

    parser.add_option(
        '--unzip-setuptools',
        dest='unzip_setuptools',
        action='store_true',
        help="Unzip Setuptools or Distribute when installing it")

    parser.add_option(
        '--relocatable',
        dest='relocatable',
        action='store_true',
        help='Make an EXISTING virtualenv environment relocatable.  '
        'This fixes up scripts and makes all .pth files relative')

    parser.add_option(
        '--distribute',
        dest='use_distribute',
        action='store_true',
        help='Use Distribute instead of Setuptools. Set environ variable '
        'VIRTUALENV_USE_DISTRIBUTE to make it the default ')

    default_search_dirs = file_search_dirs()
    parser.add_option(
        '--extra-search-dir',
        dest="search_dirs",
        action="append",
        default=default_search_dirs,
        help="Directory to look for setuptools/distribute/pip distributions in. "
        "You can add any number of additional --extra-search-dir paths.")

    parser.add_option(
        '--never-download',
        dest="never_download",
        action="store_true",
        help="Never download anything from the network.  Instead, virtualenv will fail "
        "if local distributions of setuptools/distribute/pip are not present.")

    parser.add_option(
        '--prompt=',
        dest='prompt',
        help='Provides an alternative prompt prefix for this environment')

    if 'extend_parser' in globals():
        extend_parser(parser)

    options, args = parser.parse_args()

    global logger

    if 'adjust_options' in globals():
        adjust_options(options, args)

    verbosity = options.verbose - options.quiet
    logger = Logger([(Logger.level_for_integer(2-verbosity), sys.stdout)])

    if options.python and not os.environ.get('VIRTUALENV_INTERPRETER_RUNNING'):
        env = os.environ.copy()
        interpreter = resolve_interpreter(options.python)
        if interpreter == sys.executable:
            logger.warn('Already using interpreter %s' % interpreter)
        else:
            logger.notify('Running virtualenv with interpreter %s' % interpreter)
            env['VIRTUALENV_INTERPRETER_RUNNING'] = 'true'
            file = __file__
            if file.endswith('.pyc'):
                file = file[:-1]
            popen = subprocess.Popen([interpreter, file] + sys.argv[1:], env=env)
            raise SystemExit(popen.wait())

    if not args:
        print('You must provide a DEST_DIR')
        parser.print_help()
        sys.exit(2)
    if len(args) > 1:
        print('There must be only one argument: DEST_DIR (you gave %s)' % (
            ' '.join(args)))
        parser.print_help()
        sys.exit(2)

    home_dir = args[0]

    if os.environ.get('WORKING_ENV'):
        logger.fatal('ERROR: you cannot run virtualenv while in a workingenv')
        logger.fatal('Please deactivate your workingenv, then re-run this script')
        sys.exit(3)

    if 'PYTHONHOME' in os.environ:
        logger.warn('PYTHONHOME is set.  You *must* activate the virtualenv before using it')
        del os.environ['PYTHONHOME']

    if options.relocatable:
        make_environment_relocatable(home_dir)
        return

    create_environment(home_dir, site_packages=not options.no_site_packages, clear=options.clear,
                       unzip_setuptools=options.unzip_setuptools,
                       use_distribute=options.use_distribute or majver > 2,
                       prompt=options.prompt,
                       search_dirs=options.search_dirs,
                       never_download=options.never_download)
    if 'after_install' in globals():
        after_install(options, home_dir)

def call_subprocess(cmd, show_stdout=True,
                    filter_stdout=None, cwd=None,
                    raise_on_returncode=True, extra_env=None,
                    remove_from_env=None):
    cmd_parts = []
    for part in cmd:
        if len(part) > 45:
            part = part[:20]+"..."+part[-20:]
        if ' ' in part or '\n' in part or '"' in part or "'" in part:
            part = '"%s"' % part.replace('"', '\\"')
        cmd_parts.append(part)
    cmd_desc = ' '.join(cmd_parts)
    if show_stdout:
        stdout = None
    else:
        stdout = subprocess.PIPE
    logger.debug("Running command %s" % cmd_desc)
    if extra_env or remove_from_env:
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)
        if remove_from_env:
            for varname in remove_from_env:
                env.pop(varname, None)
    else:
        env = None
    try:
        proc = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
            cwd=cwd, env=env)
    except Exception:
        e = sys.exc_info()[1]
        logger.fatal(
            "Error %s while executing command %s" % (e, cmd_desc))
        raise
    all_output = []
    if stdout is not None:
        stdout = proc.stdout
        encoding = sys.getdefaultencoding()
        while 1:
            line = stdout.readline().decode(encoding)
            if not line:
                break
            line = line.rstrip()
            all_output.append(line)
            if filter_stdout:
                level = filter_stdout(line)
                if isinstance(level, tuple):
                    level, line = level
                logger.log(level, line)
                if not logger.stdout_level_matches(level):
                    logger.show_progress()
            else:
                logger.info(line)
    else:
        proc.communicate()
    proc.wait()
    if proc.returncode:
        if raise_on_returncode:
            if all_output:
                logger.notify('Complete output from command %s:' % cmd_desc)
                logger.notify('\n'.join(all_output) + '\n----------------------------------------')
            raise OSError(
                "Command %s failed with error code %s"
                % (cmd_desc, proc.returncode))
        else:
            logger.warn(
                "Command %s had error code %s"
                % (cmd_desc, proc.returncode))


def create_environment(home_dir, site_packages=True, clear=False,
                       unzip_setuptools=False, use_distribute=False,
                       prompt=None, search_dirs=None, never_download=False):
    """
    Creates a new environment in ``home_dir``.

    If ``site_packages`` is true (the default) then the global
    ``site-packages/`` directory will be on the path.

    If ``clear`` is true (default False) then the environment will
    first be cleared.
    """
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)

    py_executable = os.path.abspath(install_python(
        home_dir, lib_dir, inc_dir, bin_dir,
        site_packages=site_packages, clear=clear))

    install_distutils(home_dir)

    if use_distribute or os.environ.get('VIRTUALENV_USE_DISTRIBUTE'):
        install_distribute(py_executable, unzip=unzip_setuptools, 
                           search_dirs=search_dirs, never_download=never_download)
    else:
        install_setuptools(py_executable, unzip=unzip_setuptools, 
                           search_dirs=search_dirs, never_download=never_download)

    install_pip(py_executable, search_dirs=search_dirs, never_download=never_download)

    install_activate(home_dir, bin_dir, prompt)

def path_locations(home_dir):
    """Return the path locations for the environment (where libraries are,
    where scripts go, etc)"""
    # XXX: We'd use distutils.sysconfig.get_python_inc/lib but its
    # prefix arg is broken: http://bugs.python.org/issue3386
    if sys.platform == 'win32':
        # Windows has lots of problems with executables with spaces in
        # the name; this function will remove them (using the ~1
        # format):
        mkdir(home_dir)
        if ' ' in home_dir:
            try:
                pass
            except ImportError:
                print('Error: the path "%s" has a space in it' % home_dir)
                pass
                print('  http://sourceforge.net/projects/pywin32/')
                sys.exit(3)
            pass
        lib_dir = join(home_dir, 'Lib')
        inc_dir = join(home_dir, 'Include')
        bin_dir = join(home_dir, 'Scripts')
    elif is_jython:
        lib_dir = join(home_dir, 'Lib')
        inc_dir = join(home_dir, 'Include')
        bin_dir = join(home_dir, 'bin')
    elif is_pypy:
        lib_dir = home_dir
        inc_dir = join(home_dir, 'include')
        bin_dir = join(home_dir, 'bin')
    else:
        lib_dir = join(home_dir, 'lib', py_version)
        inc_dir = join(home_dir, 'include', py_version + abiflags)
        bin_dir = join(home_dir, 'bin')
    return home_dir, lib_dir, inc_dir, bin_dir


def change_prefix(filename, dst_prefix):
    prefixes = [sys.prefix]

    if sys.platform == "darwin":
        prefixes.extend((
            os.path.join("/Library/Python", sys.version[:3], "site-packages"),
            os.path.join(sys.prefix, "Extras", "lib", "python"),
            os.path.join("~", "Library", "Python", sys.version[:3], "site-packages")))

    if hasattr(sys, 'real_prefix'):
        prefixes.append(sys.real_prefix)
    prefixes = list(map(os.path.abspath, prefixes))
    filename = os.path.abspath(filename)
    for src_prefix in prefixes:
        if filename.startswith(src_prefix):
            _, relpath = filename.split(src_prefix, 1)
            assert relpath[0] == os.sep
            relpath = relpath[1:]
            return join(dst_prefix, relpath)
    assert False, "Filename %s does not start with any of these prefixes: %s" % \
        (filename, prefixes)

def copy_required_modules(dst_prefix):
    import imp
    for modname in REQUIRED_MODULES:
        if modname in sys.builtin_module_names:
            logger.info("Ignoring built-in bootstrap module: %s" % modname)
            continue
        try:
            f, filename, _ = imp.find_module(modname)
        except ImportError:
            logger.info("Cannot import bootstrap module: %s" % modname)
        else:
            if f is not None:
                f.close()
            dst_filename = change_prefix(filename, dst_prefix)
            copyfile(filename, dst_filename)
            if filename.endswith('.pyc'):
                pyfile = filename[:-1]
                if os.path.exists(pyfile):
                    copyfile(pyfile, dst_filename[:-1])


def install_python(home_dir, lib_dir, inc_dir, bin_dir, site_packages, clear):
    """Install just the base environment, no distutils patches etc"""
    if sys.executable.startswith(bin_dir):
        print('Please use the *system* python to run this script')
        return

    if clear:
        rmtree(lib_dir)
        ## FIXME: why not delete it?
        ## Maybe it should delete everything with #!/path/to/venv/python in it
        logger.notify('Not deleting %s', bin_dir)

    if hasattr(sys, 'real_prefix'):
        logger.notify('Using real prefix %r' % sys.real_prefix)
        prefix = sys.real_prefix
    else:
        prefix = sys.prefix
    mkdir(lib_dir)
    fix_lib64(lib_dir)
    stdlib_dirs = [os.path.dirname(os.__file__)]
    if sys.platform == 'win32':
        stdlib_dirs.append(join(os.path.dirname(stdlib_dirs[0]), 'DLLs'))
    elif sys.platform == 'darwin':
        stdlib_dirs.append(join(stdlib_dirs[0], 'site-packages'))
    if hasattr(os, 'symlink'):
        logger.info('Symlinking Python bootstrap modules')
    else:
        logger.info('Copying Python bootstrap modules')
    logger.indent += 2
    try:
        # copy required files...
        for stdlib_dir in stdlib_dirs:
            if not os.path.isdir(stdlib_dir):
                continue
            for fn in os.listdir(stdlib_dir):
                bn = os.path.splitext(fn)[0]
                if fn != 'site-packages' and bn in REQUIRED_FILES:
                    copyfile(join(stdlib_dir, fn), join(lib_dir, fn))
        # ...and modules
        copy_required_modules(home_dir)
    finally:
        logger.indent -= 2
    mkdir(join(lib_dir, 'site-packages'))
    import site
    site_filename = site.__file__
    if site_filename.endswith('.pyc'):
        site_filename = site_filename[:-1]
    elif site_filename.endswith('$py.class'):
        site_filename = site_filename.replace('$py.class', '.py')
    site_filename_dst = change_prefix(site_filename, home_dir)
    site_dir = os.path.dirname(site_filename_dst)
    writefile(site_filename_dst, SITE_PY)
    writefile(join(site_dir, 'orig-prefix.txt'), prefix)
    site_packages_filename = join(site_dir, 'no-global-site-packages.txt')
    if not site_packages:
        writefile(site_packages_filename, '')
    else:
        if os.path.exists(site_packages_filename):
            logger.info('Deleting %s' % site_packages_filename)
            os.unlink(site_packages_filename)

    if is_pypy:
        stdinc_dir = join(prefix, 'include')
    else:
        stdinc_dir = join(prefix, 'include', py_version + abiflags)
    if os.path.exists(stdinc_dir):
        copyfile(stdinc_dir, inc_dir)
    else:
        logger.debug('No include dir %s' % stdinc_dir)

    # pypy never uses exec_prefix, just ignore it
    if sys.exec_prefix != prefix and not is_pypy:
        if sys.platform == 'win32':
            exec_dir = join(sys.exec_prefix, 'lib')
        elif is_jython:
            exec_dir = join(sys.exec_prefix, 'Lib')
        else:
            exec_dir = join(sys.exec_prefix, 'lib', py_version)
        for fn in os.listdir(exec_dir):
            copyfile(join(exec_dir, fn), join(lib_dir, fn))

    if is_jython:
        # Jython has either jython-dev.jar and javalib/ dir, or just
        # jython.jar
        for name in 'jython-dev.jar', 'javalib', 'jython.jar':
            src = join(prefix, name)
            if os.path.exists(src):
                copyfile(src, join(home_dir, name))
        # XXX: registry should always exist after Jython 2.5rc1
        src = join(prefix, 'registry')
        if os.path.exists(src):
            copyfile(src, join(home_dir, 'registry'), symlink=False)
        copyfile(join(prefix, 'cachedir'), join(home_dir, 'cachedir'),
                 symlink=False)

    mkdir(bin_dir)
    py_executable = join(bin_dir, os.path.basename(sys.executable))
    if 'Python.framework' in prefix:
        if re.search(r'/Python(?:-32|-64)*$', py_executable):
            # The name of the python executable is not quite what
            # we want, rename it.
            py_executable = os.path.join(
                    os.path.dirname(py_executable), 'python')

    logger.notify('New %s executable in %s', expected_exe, py_executable)
    if sys.executable != py_executable:
        ## FIXME: could I just hard link?
        executable = sys.executable
        if sys.platform == 'cygwin' and os.path.exists(executable + '.exe'):
            # Cygwin misreports sys.executable sometimes
            executable += '.exe'
            py_executable += '.exe'
            logger.info('Executable actually exists in %s' % executable)
        shutil.copyfile(executable, py_executable)
        make_exe(py_executable)
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
            if os.path.exists(pythonw):
                logger.info('Also created pythonw.exe')
                shutil.copyfile(pythonw, os.path.join(os.path.dirname(py_executable), 'pythonw.exe'))
        if is_pypy:
            # make a symlink python --> pypy-c
            python_executable = os.path.join(os.path.dirname(py_executable), 'python')
            logger.info('Also created executable %s' % python_executable)
            copyfile(py_executable, python_executable)

    if os.path.splitext(os.path.basename(py_executable))[0] != expected_exe:
        secondary_exe = os.path.join(os.path.dirname(py_executable),
                                     expected_exe)
        py_executable_ext = os.path.splitext(py_executable)[1]
        if py_executable_ext == '.exe':
            # python2.4 gives an extension of '.4' :P
            secondary_exe += py_executable_ext
        if os.path.exists(secondary_exe):
            logger.warn('Not overwriting existing %s script %s (you must use %s)'
                        % (expected_exe, secondary_exe, py_executable))
        else:
            logger.notify('Also creating executable in %s' % secondary_exe)
            shutil.copyfile(sys.executable, secondary_exe)
            make_exe(secondary_exe)

    if 'Python.framework' in prefix:
        logger.debug('MacOSX Python framework detected')

        # Make sure we use the the embedded interpreter inside
        # the framework, even if sys.executable points to
        # the stub executable in ${sys.prefix}/bin
        # See http://groups.google.com/group/python-virtualenv/
        #                              browse_thread/thread/17cab2f85da75951
        original_python = os.path.join(
            prefix, 'Resources/Python.app/Contents/MacOS/Python')
        shutil.copy(original_python, py_executable)

        # Copy the framework's dylib into the virtual
        # environment
        virtual_lib = os.path.join(home_dir, '.Python')

        if os.path.exists(virtual_lib):
            os.unlink(virtual_lib)
        copyfile(
            os.path.join(prefix, 'Python'),
            virtual_lib)

        # And then change the install_name of the copied python executable
        try:
            call_subprocess(
                ["install_name_tool", "-change",
                 os.path.join(prefix, 'Python'),
                 '@executable_path/../.Python',
                 py_executable])
        except:
            logger.fatal(
                "Could not call install_name_tool -- you must have Apple's development tools installed")
            raise

        # Some tools depend on pythonX.Y being present
        py_executable_version = '%s.%s' % (
            sys.version_info[0], sys.version_info[1])
        if not py_executable.endswith(py_executable_version):
            # symlinking pythonX.Y > python
            pth = py_executable + '%s.%s' % (
                    sys.version_info[0], sys.version_info[1])
            if os.path.exists(pth):
                os.unlink(pth)
            os.symlink('python', pth)
        else:
            # reverse symlinking python -> pythonX.Y (with --python)
            pth = join(bin_dir, 'python')
            if os.path.exists(pth):
                os.unlink(pth)
            os.symlink(os.path.basename(py_executable), pth)

    if sys.platform == 'win32' and ' ' in py_executable:
        # There's a bug with subprocess on Windows when using a first
        # argument that has a space in it.  Instead we have to quote
        # the value:
        py_executable = '"%s"' % py_executable
    cmd = [py_executable, '-c', 'import sys; print(sys.prefix)']
    logger.info('Testing executable with %s %s "%s"' % tuple(cmd))
    try:
        proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE)
        proc_stdout, proc_stderr = proc.communicate()
    except OSError:
        e = sys.exc_info()[1]
        if e.errno == errno.EACCES:
            logger.fatal('ERROR: The executable %s could not be run: %s' % (py_executable, e))
            sys.exit(100)
        else:
          raise e

    proc_stdout = proc_stdout.strip().decode(sys.getdefaultencoding())
    proc_stdout = os.path.normcase(os.path.abspath(proc_stdout))
    if proc_stdout != os.path.normcase(os.path.abspath(home_dir)):
        logger.fatal(
            'ERROR: The executable %s is not functioning' % py_executable)
        logger.fatal(
            'ERROR: It thinks sys.prefix is %r (should be %r)'
            % (proc_stdout, os.path.normcase(os.path.abspath(home_dir))))
        logger.fatal(
            'ERROR: virtualenv is not compatible with this system or executable')
        if sys.platform == 'win32':
            logger.fatal(
                'Note: some Windows users have reported this error when they installed Python for "Only this user".  The problem may be resolvable if you install Python "For all users".  (See https://bugs.launchpad.net/virtualenv/+bug/352844)')
        sys.exit(100)
    else:
        logger.info('Got sys.prefix result: %r' % proc_stdout)

    pydistutils = os.path.expanduser('~/.pydistutils.cfg')
    if os.path.exists(pydistutils):
        logger.notify('Please make sure you remove any previous custom paths from '
                      'your %s file.' % pydistutils)
    ## FIXME: really this should be calculated earlier
    return py_executable

def install_activate(home_dir, bin_dir, prompt=None):
    if sys.platform == 'win32' or is_jython and os._name == 'nt':
        files = {'activate.bat': ACTIVATE_BAT,
                 'deactivate.bat': DEACTIVATE_BAT}
        if os.environ.get('OS') == 'Windows_NT' and os.environ.get('OSTYPE') == 'cygwin':
            files['activate'] = ACTIVATE_SH
    else:
        files = {'activate': ACTIVATE_SH}

        # suppling activate.fish in addition to, not instead of, the
        # bash script support.
        files['activate.fish'] = ACTIVATE_FISH

        # same for csh/tcsh support...
        files['activate.csh'] = ACTIVATE_CSH



    files['activate_this.py'] = ACTIVATE_THIS
    vname = os.path.basename(os.path.abspath(home_dir))
    for name, content in files.items():
        content = content.replace('__VIRTUAL_PROMPT__', prompt or '')
        content = content.replace('__VIRTUAL_WINPROMPT__', prompt or '(%s)' % vname)
        content = content.replace('__VIRTUAL_ENV__', os.path.abspath(home_dir))
        content = content.replace('__VIRTUAL_NAME__', vname)
        content = content.replace('__BIN_NAME__', os.path.basename(bin_dir))
        writefile(os.path.join(bin_dir, name), content)

def install_distutils(home_dir):
    distutils_path = change_prefix(distutils.__path__[0], home_dir)
    mkdir(distutils_path)
    ## FIXME: maybe this prefix setting should only be put in place if
    ## there's a local distutils.cfg with a prefix setting?
    home_dir = os.path.abspath(home_dir)
    ## FIXME: this is breaking things, removing for now:
    #distutils_cfg = DISTUTILS_CFG + "\n[install]\nprefix=%s\n" % home_dir
    writefile(os.path.join(distutils_path, '__init__.py'), DISTUTILS_INIT)
    writefile(os.path.join(distutils_path, 'distutils.cfg'), DISTUTILS_CFG, overwrite=False)

def fix_lib64(lib_dir):
    """
    Some platforms (particularly Gentoo on x64) put things in lib64/pythonX.Y
    instead of lib/pythonX.Y.  If this is such a platform we'll just create a
    symlink so lib64 points to lib
    """
    if [p for p in distutils.sysconfig.get_config_vars().values()
        if isinstance(p, basestring) and 'lib64' in p]:
        logger.debug('This system uses lib64; symlinking lib64 to lib')
        assert os.path.basename(lib_dir) == 'python%s' % sys.version[:3], (
            "Unexpected python lib dir: %r" % lib_dir)
        lib_parent = os.path.dirname(lib_dir)
        assert os.path.basename(lib_parent) == 'lib', (
            "Unexpected parent dir: %r" % lib_parent)
        copyfile(lib_parent, os.path.join(os.path.dirname(lib_parent), 'lib64'))

def resolve_interpreter(exe):
    """
    If the executable given isn't an absolute path, search $PATH for the interpreter
    """
    if os.path.abspath(exe) != exe:
        paths = os.environ.get('PATH', '').split(os.pathsep)
        for path in paths:
            if os.path.exists(os.path.join(path, exe)):
                exe = os.path.join(path, exe)
                break
    if not os.path.exists(exe):
        logger.fatal('The executable %s (from --python=%s) does not exist' % (exe, exe))
        raise SystemExit(3)
    if not is_executable(exe):
        logger.fatal('The executable %s (from --python=%s) is not executable' % (exe, exe))
        raise SystemExit(3)
    return exe

def is_executable(exe):
    """Checks a file is executable"""
    return os.access(exe, os.X_OK)

############################################################
## Relocating the environment:

def make_environment_relocatable(home_dir):
    """
    Makes the already-existing environment use relative paths, and takes out
    the #!-based environment selection in scripts.
    """
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)
    activate_this = os.path.join(bin_dir, 'activate_this.py')
    if not os.path.exists(activate_this):
        logger.fatal(
            'The environment doesn\'t have a file %s -- please re-run virtualenv '
            'on this environment to update it' % activate_this)
    fixup_scripts(home_dir)
    fixup_pth_and_egg_link(home_dir)
    ## FIXME: need to fix up distutils.cfg

OK_ABS_SCRIPTS = ['python', 'python%s' % sys.version[:3],
                  'activate', 'activate.bat', 'activate_this.py']

def fixup_scripts(home_dir):
    # This is what we expect at the top of scripts:
    shebang = '#!%s/bin/python' % os.path.normcase(os.path.abspath(home_dir))
    # This is what we'll put:
    new_shebang = '#!/usr/bin/env python%s' % sys.version[:3]
    activate = "import os; activate_this=os.path.join(os.path.dirname(__file__), 'activate_this.py'); execfile(activate_this, dict(__file__=activate_this)); del os, activate_this"
    if sys.platform == 'win32':
        bin_suffix = 'Scripts'
    else:
        bin_suffix = 'bin'
    bin_dir = os.path.join(home_dir, bin_suffix)
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)
    for filename in os.listdir(bin_dir):
        filename = os.path.join(bin_dir, filename)
        if not os.path.isfile(filename):
            # ignore subdirs, e.g. .svn ones.
            continue
        f = open(filename, 'rb')
        lines = f.readlines()
        f.close()
        if not lines:
            logger.warn('Script %s is an empty file' % filename)
            continue
        if not lines[0].strip().startswith(shebang):
            if os.path.basename(filename) in OK_ABS_SCRIPTS:
                logger.debug('Cannot make script %s relative' % filename)
            elif lines[0].strip() == new_shebang:
                logger.info('Script %s has already been made relative' % filename)
            else:
                logger.warn('Script %s cannot be made relative (it\'s not a normal script that starts with %s)'
                            % (filename, shebang))
            continue
        logger.notify('Making script %s relative' % filename)
        lines = [new_shebang+'\n', activate+'\n'] + lines[1:]
        f = open(filename, 'wb')
        f.writelines(lines)
        f.close()

def fixup_pth_and_egg_link(home_dir, sys_path=None):
    """Makes .pth and .egg-link files use relative paths"""
    home_dir = os.path.normcase(os.path.abspath(home_dir))
    if sys_path is None:
        sys_path = sys.path
    for path in sys_path:
        if not path:
            path = '.'
        if not os.path.isdir(path):
            continue
        path = os.path.normcase(os.path.abspath(path))
        if not path.startswith(home_dir):
            logger.debug('Skipping system (non-environment) directory %s' % path)
            continue
        for filename in os.listdir(path):
            filename = os.path.join(path, filename)
            if filename.endswith('.pth'):
                if not os.access(filename, os.W_OK):
                    logger.warn('Cannot write .pth file %s, skipping' % filename)
                else:
                    fixup_pth_file(filename)
            if filename.endswith('.egg-link'):
                if not os.access(filename, os.W_OK):
                    logger.warn('Cannot write .egg-link file %s, skipping' % filename)
                else:
                    fixup_egg_link(filename)

def fixup_pth_file(filename):
    lines = []
    prev_lines = []
    f = open(filename)
    prev_lines = f.readlines()
    f.close()
    for line in prev_lines:
        line = line.strip()
        if (not line or line.startswith('#') or line.startswith('import ')
            or os.path.abspath(line) != line):
            lines.append(line)
        else:
            new_value = make_relative_path(filename, line)
            if line != new_value:
                logger.debug('Rewriting path %s as %s (in %s)' % (line, new_value, filename))
            lines.append(new_value)
    if lines == prev_lines:
        logger.info('No changes to .pth file %s' % filename)
        return
    logger.notify('Making paths in .pth file %s relative' % filename)
    f = open(filename, 'w')
    f.write('\n'.join(lines) + '\n')
    f.close()

def fixup_egg_link(filename):
    f = open(filename)
    link = f.read().strip()
    f.close()
    if os.path.abspath(link) != link:
        logger.debug('Link in %s already relative' % filename)
        return
    new_link = make_relative_path(filename, link)
    logger.notify('Rewriting link %s in %s as %s' % (link, filename, new_link))
    f = open(filename, 'w')
    f.write(new_link)
    f.close()

def make_relative_path(source, dest, dest_is_directory=True):
    """
    Make a filename relative, where the filename is dest, and it is
    being referred to from the filename source.

        >>> make_relative_path('/usr/share/something/a-file.pth',
        ...                    '/usr/share/another-place/src/Directory')
        '../another-place/src/Directory'
        >>> make_relative_path('/usr/share/something/a-file.pth',
        ...                    '/home/user/src/Directory')
        '../../../home/user/src/Directory'
        >>> make_relative_path('/usr/share/a-file.pth', '/usr/share/')
        './'
    """
    source = os.path.dirname(source)
    if not dest_is_directory:
        dest_filename = os.path.basename(dest)
        dest = os.path.dirname(dest)
    dest = os.path.normpath(os.path.abspath(dest))
    source = os.path.normpath(os.path.abspath(source))
    dest_parts = dest.strip(os.path.sep).split(os.path.sep)
    source_parts = source.strip(os.path.sep).split(os.path.sep)
    while dest_parts and source_parts and dest_parts[0] == source_parts[0]:
        dest_parts.pop(0)
        source_parts.pop(0)
    full_parts = ['..']*len(source_parts) + dest_parts
    if not dest_is_directory:
        full_parts.append(dest_filename)
    if not full_parts:
        # Special case for the current directory (otherwise it'd be '')
        return './'
    return os.path.sep.join(full_parts)



############################################################
## Bootstrap script creation:

def create_bootstrap_script(extra_text, python_version=''):
    """
    Creates a bootstrap script, which is like this script but with
    extend_parser, adjust_options, and after_install hooks.

    This returns a string that (written to disk of course) can be used
    as a bootstrap script with your own customizations.  The script
    will be the standard virtualenv.py script, with your extra text
    added (your extra text should be Python code).

    If you include these functions, they will be called:

    ``extend_parser(optparse_parser)``:
        You can add or remove options from the parser here.

    ``adjust_options(options, args)``:
        You can change options here, or change the args (if you accept
        different kinds of arguments, be sure you modify ``args`` so it is
        only ``[DEST_DIR]``).

    ``after_install(options, home_dir)``:

        After everything is installed, this function is called.  This
        is probably the function you are most likely to use.  An
        example would be::

            def after_install(options, home_dir):
                subprocess.call([join(home_dir, 'bin', 'easy_install'),
                                 'MyPackage'])
                subprocess.call([join(home_dir, 'bin', 'my-package-script'),
                                 'setup', home_dir])

        This example immediately installs a package, and runs a setup
        script from that package.

    If you provide something like ``python_version='2.4'`` then the
    script will start with ``#!/usr/bin/env python2.4`` instead of
    ``#!/usr/bin/env python``.  You can use this when the script must
    be run with a particular Python version.
    """
    filename = __file__
    if filename.endswith('.pyc'):
        filename = filename[:-1]
    f = open(filename, 'rb')
    content = f.read()
    f.close()
    py_exe = 'python%s' % python_version
    content = (('#!/usr/bin/env %s\n' % py_exe)
               + '## WARNING: This file is generated\n'
               + content)
    return content.replace('##EXT' 'END##', extra_text)


#
# Imported from odict.py
#

# odict.py
# An Ordered Dictionary object
# Copyright (C) 2005 Nicola Larosa, Michael Foord
# E-mail: nico AT tekNico DOT net, fuzzyman AT voidspace DOT org DOT uk

# This software is licensed under the terms of the BSD license.
# http://www.voidspace.org.uk/python/license.shtml
# Basically you're free to copy, modify, distribute and relicense it,
# So long as you keep a copy of the license with it.

# Documentation at http://www.voidspace.org.uk/python/odict.html
# For information about bugfixes, updates and support, please join the
# Pythonutils mailing list:
# http://groups.google.com/group/pythonutils/
# Comments, suggestions and bug reports welcome.

"""A dict that keeps keys in insertion order"""
#from __future__ import generators

__author__ = ('Nicola Larosa <nico-NoSp@m-tekNico.net>,'
    'Michael Foord <fuzzyman AT voidspace DOT org DOT uk>')

__docformat__ = "restructuredtext en"

__revision__ = '$Id: odict.py 129 2005-09-12 18:15:28Z teknico $'

__version__ = '0.2.2'

__all__ = ['OrderedDict', 'SequenceOrderedDict']

import sys
INTP_VER = sys.version_info[:2]
if INTP_VER < (2, 2):
    raise RuntimeError("Python v.2.2 or later required")

import types, warnings

class OrderedDict(dict):
    """
    A class of dictionary that keeps the insertion order of keys.

    All appropriate methods return keys, items, or values in an ordered way.

    All normal dictionary methods are available. Update and comparison is
    restricted to other OrderedDict objects.

    Various sequence methods are available, including the ability to explicitly
    mutate the key ordering.

    __contains__ tests:

    >>> d = OrderedDict(((1, 3),))
    >>> 1 in d
    1
    >>> 4 in d
    0

    __getitem__ tests:

    >>> OrderedDict(((1, 3), (3, 2), (2, 1)))[2]
    1
    >>> OrderedDict(((1, 3), (3, 2), (2, 1)))[4]
    Traceback (most recent call last):
    KeyError: 4

    __len__ tests:

    >>> len(OrderedDict())
    0
    >>> len(OrderedDict(((1, 3), (3, 2), (2, 1))))
    3

    get tests:

    >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
    >>> d.get(1)
    3
    >>> d.get(4) is None
    1
    >>> d.get(4, 5)
    5
    >>> d
    OrderedDict([(1, 3), (3, 2), (2, 1)])

    has_key tests:

    >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
    >>> d.has_key(1)
    1
    >>> d.has_key(4)
    0
    """

    def __init__(self, init_val=(), strict=False):
        """
        Create a new ordered dictionary. Cannot init from a normal dict,
        nor from kwargs, since items order is undefined in those cases.

        If the ``strict`` keyword argument is ``True`` (``False`` is the
        default) then when doing slice assignment - the ``OrderedDict`` you are
        assigning from *must not* contain any keys in the remaining dict.

        >>> OrderedDict()
        OrderedDict([])
        >>> OrderedDict({1: 1})
        Traceback (most recent call last):
        TypeError: undefined order, cannot get items from dict
        >>> OrderedDict({1: 1}.items())
        OrderedDict([(1, 1)])
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d
        OrderedDict([(1, 3), (3, 2), (2, 1)])
        >>> OrderedDict(d)
        OrderedDict([(1, 3), (3, 2), (2, 1)])
        """
        self.strict = strict
        dict.__init__(self)
        if isinstance(init_val, OrderedDict):
            self._sequence = init_val.keys()
            dict.update(self, init_val)
        elif isinstance(init_val, dict):
            # we lose compatibility with other ordered dict types this way
            raise TypeError('undefined order, cannot get items from dict')
        else:
            self._sequence = []
            self.update(init_val)

### Special methods ###

    def __delitem__(self, key):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> del d[3]
        >>> d
        OrderedDict([(1, 3), (2, 1)])
        >>> del d[3]
        Traceback (most recent call last):
        KeyError: 3
        >>> d[3] = 2
        >>> d
        OrderedDict([(1, 3), (2, 1), (3, 2)])
        >>> del d[0:1]
        >>> d
        OrderedDict([(2, 1), (3, 2)])
        """
        if isinstance(key, types.SliceType):
            # NOTE: efficiency?
            keys = self._sequence[key]
            for entry in keys:
                dict.__delitem__(self, entry)
            del self._sequence[key]
        else:
            # do the dict.__delitem__ *first* as it raises
            # the more appropriate error
            dict.__delitem__(self, key)
            self._sequence.remove(key)

    def __eq__(self, other):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d == OrderedDict(d)
        True
        >>> d == OrderedDict(((1, 3), (2, 1), (3, 2)))
        False
        >>> d == OrderedDict(((1, 0), (3, 2), (2, 1)))
        False
        >>> d == OrderedDict(((0, 3), (3, 2), (2, 1)))
        False
        >>> d == dict(d)
        False
        >>> d == False
        False
        """
        if isinstance(other, OrderedDict):
            # NOTE: efficiency?
            #   Generate both item lists for each compare
            return (self.items() == other.items())
        else:
            return False

    def __lt__(self, other):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> c < d
        True
        >>> d < c
        False
        >>> d < dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other OrderedDicts
        """
        if not isinstance(other, OrderedDict):
            raise TypeError('Can only compare with other OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() < other.items())

    def __le__(self, other):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> e = OrderedDict(d)
        >>> c <= d
        True
        >>> d <= c
        False
        >>> d <= dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other OrderedDicts
        >>> d <= e
        True
        """
        if not isinstance(other, OrderedDict):
            raise TypeError('Can only compare with other OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() <= other.items())

    def __ne__(self, other):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d != OrderedDict(d)
        False
        >>> d != OrderedDict(((1, 3), (2, 1), (3, 2)))
        True
        >>> d != OrderedDict(((1, 0), (3, 2), (2, 1)))
        True
        >>> d == OrderedDict(((0, 3), (3, 2), (2, 1)))
        False
        >>> d != dict(d)
        True
        >>> d != False
        True
        """
        if isinstance(other, OrderedDict):
            # NOTE: efficiency?
            #   Generate both item lists for each compare
            return not (self.items() == other.items())
        else:
            return True

    def __gt__(self, other):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> d > c
        True
        >>> c > d
        False
        >>> d > dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other OrderedDicts
        """
        if not isinstance(other, OrderedDict):
            raise TypeError('Can only compare with other OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() > other.items())

    def __ge__(self, other):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> e = OrderedDict(d)
        >>> c >= d
        False
        >>> d >= c
        True
        >>> d >= dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other OrderedDicts
        >>> e >= d
        True
        """
        if not isinstance(other, OrderedDict):
            raise TypeError('Can only compare with other OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() >= other.items())

    def __repr__(self):
        """
        Used for __repr__ and __str__

        >>> r1 = repr(OrderedDict((('a', 'b'), ('c', 'd'), ('e', 'f'))))
        >>> r1
        "OrderedDict([('a', 'b'), ('c', 'd'), ('e', 'f')])"
        >>> r2 = repr(OrderedDict((('a', 'b'), ('e', 'f'), ('c', 'd'))))
        >>> r2
        "OrderedDict([('a', 'b'), ('e', 'f'), ('c', 'd')])"
        >>> r1 == str(OrderedDict((('a', 'b'), ('c', 'd'), ('e', 'f'))))
        True
        >>> r2 == str(OrderedDict((('a', 'b'), ('e', 'f'), ('c', 'd'))))
        True
        """
        return '%s([%s])' % (self.__class__.__name__, ', '.join(
            ['(%r, %r)' % (key, self[key]) for key in self._sequence]))

    def __setitem__(self, key, val):
        """
        Allows slice assignment, so long as the slice is an OrderedDict
        >>> d = OrderedDict()
        >>> d['a'] = 'b'
        >>> d['b'] = 'a'
        >>> d[3] = 12
        >>> d
        OrderedDict([('a', 'b'), ('b', 'a'), (3, 12)])
        >>> d[:] = OrderedDict(((1, 2), (2, 3), (3, 4)))
        >>> d
        OrderedDict([(1, 2), (2, 3), (3, 4)])
        >>> d[::2] = OrderedDict(((7, 8), (9, 10)))
        >>> d
        OrderedDict([(7, 8), (2, 3), (9, 10)])
        >>> d = OrderedDict(((0, 1), (1, 2), (2, 3), (3, 4)))
        >>> d[1:3] = OrderedDict(((1, 2), (5, 6), (7, 8)))
        >>> d
        OrderedDict([(0, 1), (1, 2), (5, 6), (7, 8), (3, 4)])
        >>> d = OrderedDict(((0, 1), (1, 2), (2, 3), (3, 4)), strict=True)
        >>> d[1:3] = OrderedDict(((1, 2), (5, 6), (7, 8)))
        >>> d
        OrderedDict([(0, 1), (1, 2), (5, 6), (7, 8), (3, 4)])

        >>> a = OrderedDict(((0, 1), (1, 2), (2, 3)), strict=True)
        >>> a[3] = 4
        >>> a
        OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[::1] = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[:2] = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])
        Traceback (most recent call last):
        ValueError: slice assignment must be from unique keys
        >>> a = OrderedDict(((0, 1), (1, 2), (2, 3)))
        >>> a[3] = 4
        >>> a
        OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[::1] = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[:2] = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[::-1] = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        OrderedDict([(3, 4), (2, 3), (1, 2), (0, 1)])

        >>> d = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> d[:1] = 3
        Traceback (most recent call last):
        TypeError: slice assignment requires an OrderedDict

        >>> d = OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> d[:1] = OrderedDict([(9, 8)])
        >>> d
        OrderedDict([(9, 8), (1, 2), (2, 3), (3, 4)])
        """
        if isinstance(key, types.SliceType):
            if not isinstance(val, OrderedDict):
                # NOTE: allow a list of tuples?
                raise TypeError('slice assignment requires an OrderedDict')
            keys = self._sequence[key]
            # NOTE: Could use ``range(*key.indices(len(self._sequence)))``
            indexes = range(len(self._sequence))[key]
            if key.step is None:
                # NOTE: new slice may not be the same size as the one being
                #   overwritten !
                # NOTE: What is the algorithm for an impossible slice?
                #   e.g. d[5:3]
                pos = key.start or 0
                del self[key]
                newkeys = val.keys()
                for k in newkeys:
                    if k in self:
                        if self.strict:
                            raise ValueError('slice assignment must be from '
                                'unique keys')
                        else:
                            # NOTE: This removes duplicate keys *first*
                            #   so start position might have changed?
                            del self[k]
                self._sequence = (self._sequence[:pos] + newkeys +
                    self._sequence[pos:])
                dict.update(self, val)
            else:
                # extended slice - length of new slice must be the same
                # as the one being replaced
                if len(keys) != len(val):
                    raise ValueError('attempt to assign sequence of size %s '
                        'to extended slice of size %s' % (len(val), len(keys)))
                # NOTE: efficiency?
                del self[key]
                item_list = zip(indexes, val.items())
                # smallest indexes first - higher indexes not guaranteed to
                # exist
                item_list.sort()
                for pos, (newkey, newval) in item_list:
                    if self.strict and newkey in self:
                        raise ValueError('slice assignment must be from unique'
                            ' keys')
                    self.insert(pos, newkey, newval)
        else:
            if key not in self:
                self._sequence.append(key)
            dict.__setitem__(self, key, val)

    def __getitem__(self, key):
        """
        Allows slicing. Returns an OrderedDict if you slice.
        >>> b = OrderedDict([(7, 0), (6, 1), (5, 2), (4, 3), (3, 4), (2, 5), (1, 6)])
        >>> b[::-1]
        OrderedDict([(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)])
        >>> b[2:5]
        OrderedDict([(5, 2), (4, 3), (3, 4)])
        >>> type(b[2:4])
        <class '__main__.OrderedDict'>
        """
        if isinstance(key, types.SliceType):
            # NOTE: does this raise the error we want?
            keys = self._sequence[key]
            # NOTE: efficiency?
            return OrderedDict([(entry, self[entry]) for entry in keys])
        else:
            return dict.__getitem__(self, key)

    __str__ = __repr__

    def __setattr__(self, name, value):
        """
        Implemented so that accesses to ``sequence`` raise a warning and are
        diverted to the new ``setkeys`` method.
        """
        if name == 'sequence':
            warnings.warn('Use of the sequence attribute is deprecated.'
                ' Use the keys method instead.', DeprecationWarning)
            # NOTE: doesn't return anything
            self.setkeys(value)
        else:
            # NOTE: do we want to allow arbitrary setting of attributes?
            #   Or do we want to manage it?
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        """
        Implemented so that access to ``sequence`` raises a warning.

        >>> d = OrderedDict()
        >>> d.sequence
        []
        """
        if name == 'sequence':
            warnings.warn('Use of the sequence attribute is deprecated.'
                ' Use the keys method instead.', DeprecationWarning)
            # NOTE: Still (currently) returns a direct reference. Need to
            #   because code that uses sequence will expect to be able to
            #   mutate it in place.
            return self._sequence
        else:
            # raise the appropriate error
            raise AttributeError("OrderedDict has no '%s' attribute" % name)

    def __deepcopy__(self, memo):
        """
        To allow deepcopy to work with OrderedDict.

        >>> from copy import deepcopy
        >>> a = OrderedDict([(1, 1), (2, 2), (3, 3)])
        >>> a['test'] = {}
        >>> b = deepcopy(a)
        >>> b == a
        True
        >>> b is a
        False
        >>> a['test'] is b['test']
        False
        """
        from copy import deepcopy
        return self.__class__(deepcopy(self.items(), memo), self.strict)


### Read-only methods ###

    def copy(self):
        """
        >>> OrderedDict(((1, 3), (3, 2), (2, 1))).copy()
        OrderedDict([(1, 3), (3, 2), (2, 1)])
        """
        return OrderedDict(self)

    def items(self):
        """
        ``items`` returns a list of tuples representing all the
        ``(key, value)`` pairs in the dictionary.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.items()
        [(1, 3), (3, 2), (2, 1)]
        >>> d.clear()
        >>> d.items()
        []
        """
        return zip(self._sequence, self.values())

    def keys(self):
        """
        Return a list of keys in the ``OrderedDict``.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.keys()
        [1, 3, 2]
        """
        return self._sequence[:]

    def values(self, values=None):
        """
        Return a list of all the values in the OrderedDict.

        Optionally you can pass in a list of values, which will replace the
        current list. The value list must be the same len as the OrderedDict.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.values()
        [3, 2, 1]
        """
        return [self[key] for key in self._sequence]

    def iteritems(self):
        """
        >>> ii = OrderedDict(((1, 3), (3, 2), (2, 1))).iteritems()
        >>> ii.next()
        (1, 3)
        >>> ii.next()
        (3, 2)
        >>> ii.next()
        (2, 1)
        >>> ii.next()
        Traceback (most recent call last):
        StopIteration
        """
        def make_iter(self=self):
            keys = self.iterkeys()
            while True:
                key = keys.next()
                yield (key, self[key])
        return make_iter()

    def iterkeys(self):
        """
        >>> ii = OrderedDict(((1, 3), (3, 2), (2, 1))).iterkeys()
        >>> ii.next()
        1
        >>> ii.next()
        3
        >>> ii.next()
        2
        >>> ii.next()
        Traceback (most recent call last):
        StopIteration
        """
        return iter(self._sequence)

    __iter__ = iterkeys

    def itervalues(self):
        """
        >>> iv = OrderedDict(((1, 3), (3, 2), (2, 1))).itervalues()
        >>> iv.next()
        3
        >>> iv.next()
        2
        >>> iv.next()
        1
        >>> iv.next()
        Traceback (most recent call last):
        StopIteration
        """
        def make_iter(self=self):
            keys = self.iterkeys()
            while True:
                yield self[keys.next()]
        return make_iter()

### Read-write methods ###

    def clear(self):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.clear()
        >>> d
        OrderedDict([])
        """
        dict.clear(self)
        self._sequence = []

    def pop(self, key, *args):
        """
        No dict.pop in Python 2.2, gotta reimplement it

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.pop(3)
        2
        >>> d
        OrderedDict([(1, 3), (2, 1)])
        >>> d.pop(4)
        Traceback (most recent call last):
        KeyError: 4
        >>> d.pop(4, 0)
        0
        >>> d.pop(4, 0, 1)
        Traceback (most recent call last):
        TypeError: pop expected at most 2 arguments, got 3
        """
        if len(args) > 1:
            raise TypeError, ('pop expected at most 2 arguments, got %s' %
                (len(args) + 1))
        if key in self:
            val = self[key]
            del self[key]
        else:
            try:
                val = args[0]
            except IndexError:
                raise KeyError(key)
        return val

    def popitem(self, i=-1):
        """
        Delete and return an item specified by index, not a random one as in
        dict. The index is -1 by default (the last item).

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.popitem()
        (2, 1)
        >>> d
        OrderedDict([(1, 3), (3, 2)])
        >>> d.popitem(0)
        (1, 3)
        >>> OrderedDict().popitem()
        Traceback (most recent call last):
        KeyError: 'popitem(): dictionary is empty'
        >>> d.popitem(2)
        Traceback (most recent call last):
        IndexError: popitem(): index 2 not valid
        """
        if not self._sequence:
            raise KeyError('popitem(): dictionary is empty')
        try:
            key = self._sequence[i]
        except IndexError:
            raise IndexError('popitem(): index %s not valid' % i)
        return (key, self.pop(key))

    def setdefault(self, key, defval = None):
        """
        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.setdefault(1)
        3
        >>> d.setdefault(4) is None
        True
        >>> d
        OrderedDict([(1, 3), (3, 2), (2, 1), (4, None)])
        >>> d.setdefault(5, 0)
        0
        >>> d
        OrderedDict([(1, 3), (3, 2), (2, 1), (4, None), (5, 0)])
        """
        if key in self:
            return self[key]
        else:
            self[key] = defval
            return defval

    def update(self, from_od):
        """
        Update from another OrderedDict or sequence of (key, value) pairs

        >>> d = OrderedDict(((1, 0), (0, 1)))
        >>> d.update(OrderedDict(((1, 3), (3, 2), (2, 1))))
        >>> d
        OrderedDict([(1, 3), (0, 1), (3, 2), (2, 1)])
        >>> d.update({4: 4})
        Traceback (most recent call last):
        TypeError: undefined order, cannot get items from dict
        >>> d.update((4, 4))
        Traceback (most recent call last):
        TypeError: cannot convert dictionary update sequence element "4" to a 2-item sequence
        """
        if isinstance(from_od, OrderedDict):
            for key, val in from_od.items():
                self[key] = val
        elif isinstance(from_od, dict):
            # we lose compatibility with other ordered dict types this way
            raise TypeError('undefined order, cannot get items from dict')
        else:
            # NOTE: efficiency?
            # sequence of 2-item sequences, or error
            for item in from_od:
                try:
                    key, val = item
                except TypeError:
                    raise TypeError('cannot convert dictionary update'
                        ' sequence element "%s" to a 2-item sequence' % item)
                self[key] = val

    def rename(self, old_key, new_key):
        """
        Rename the key for a given value, without modifying sequence order.

        For the case where new_key already exists this raise an exception,
        since if new_key exists, it is ambiguous as to what happens to the
        associated values, and the position of new_key in the sequence.

        >>> od = OrderedDict()
        >>> od['a'] = 1
        >>> od['b'] = 2
        >>> od.items()
        [('a', 1), ('b', 2)]
        >>> od.rename('b', 'c')
        >>> od.items()
        [('a', 1), ('c', 2)]
        >>> od.rename('c', 'a')
        Traceback (most recent call last):
        ValueError: New key already exists: 'a'
        >>> od.rename('d', 'b')
        Traceback (most recent call last):
        KeyError: 'd'
        """
        if new_key == old_key:
            # no-op
            return
        if new_key in self:
            raise ValueError("New key already exists: %r" % new_key)
        # rename sequence entry
        value = self[old_key]
        old_idx = self._sequence.index(old_key)
        self._sequence[old_idx] = new_key
        # rename internal dict entry
        dict.__delitem__(self, old_key)
        dict.__setitem__(self, new_key, value)

    def setitems(self, items):
        """
        This method allows you to set the items in the dict.

        It takes a list of tuples - of the same sort returned by the ``items``
        method.

        >>> d = OrderedDict()
        >>> d.setitems(((3, 1), (2, 3), (1, 2)))
        >>> d
        OrderedDict([(3, 1), (2, 3), (1, 2)])
        """
        self.clear()
        # NOTE: this allows you to pass in an OrderedDict as well :-)
        self.update(items)

    def setkeys(self, keys):
        """
        ``setkeys`` all ows you to pass in a new list of keys which will
        replace the current set. This must contain the same set of keys, but
        need not be in the same order.

        If you pass in new keys that don't match, a ``KeyError`` will be
        raised.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.keys()
        [1, 3, 2]
        >>> d.setkeys((1, 2, 3))
        >>> d
        OrderedDict([(1, 3), (2, 1), (3, 2)])
        >>> d.setkeys(['a', 'b', 'c'])
        Traceback (most recent call last):
        KeyError: 'Keylist is not the same as current keylist.'
        """
        # NOTE: Efficiency? (use set for Python 2.4 :-)
        # NOTE: list(keys) rather than keys[:] because keys[:] returns
        #   a tuple, if keys is a tuple.
        kcopy = list(keys)
        kcopy.sort()
        self._sequence.sort()
        if kcopy != self._sequence:
            raise KeyError('Keylist is not the same as current keylist.')
        # NOTE: This makes the _sequence attribute a new object, instead
        #       of changing it in place.
        # NOTE: efficiency?
        self._sequence = list(keys)

    def setvalues(self, values):
        """
        You can pass in a list of values, which will replace the
        current list. The value list must be the same len as the OrderedDict.

        (Or a ``ValueError`` is raised.)

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.setvalues((1, 2, 3))
        >>> d
        OrderedDict([(1, 1), (3, 2), (2, 3)])
        >>> d.setvalues([6])
        Traceback (most recent call last):
        ValueError: Value list is not the same length as the OrderedDict.
        """
        if len(values) != len(self):
            # NOTE: correct error to raise?
            raise ValueError('Value list is not the same length as the '
                'OrderedDict.')
        self.update(zip(self, values))

### Sequence Methods ###

    def index(self, key):
        """
        Return the position of the specified key in the OrderedDict.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.index(3)
        1
        >>> d.index(4)
        Traceback (most recent call last):
        ValueError: list.index(x): x not in list
        """
        return self._sequence.index(key)

    def insert(self, index, key, value):
        """
        Takes ``index``, ``key``, and ``value`` as arguments.

        Sets ``key`` to ``value``, so that ``key`` is at position ``index`` in
        the OrderedDict.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.insert(0, 4, 0)
        >>> d
        OrderedDict([(4, 0), (1, 3), (3, 2), (2, 1)])
        >>> d.insert(0, 2, 1)
        >>> d
        OrderedDict([(2, 1), (4, 0), (1, 3), (3, 2)])
        >>> d.insert(8, 8, 1)
        >>> d
        OrderedDict([(2, 1), (4, 0), (1, 3), (3, 2), (8, 1)])
        """
        if key in self:
            # NOTE: efficiency?
            del self[key]
        self._sequence.insert(index, key)
        dict.__setitem__(self, key, value)

    def reverse(self):
        """
        Reverse the order of the OrderedDict.

        >>> d = OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.reverse()
        >>> d
        OrderedDict([(2, 1), (3, 2), (1, 3)])
        """
        self._sequence.reverse()

    def sort(self, *args, **kwargs):
        """
        Sort the key order in the OrderedDict.

        This method takes the same arguments as the ``list.sort`` method on
        your version of Python.

        >>> d = OrderedDict(((4, 1), (2, 2), (3, 3), (1, 4)))
        >>> d.sort()
        >>> d
        OrderedDict([(1, 4), (2, 2), (3, 3), (4, 1)])
        """
        self._sequence.sort(*args, **kwargs)

class Keys(object):
    # NOTE: should this object be a subclass of list?
    """
    Custom object for accessing the keys of an OrderedDict.

    Can be called like the normal ``OrderedDict.keys`` method, but also
    supports indexing and sequence methods.
    """

    def __init__(self, main):
        self._main = main

    def __call__(self):
        """Pretend to be the keys method."""
        return self._main._keys()

    def __getitem__(self, index):
        """Fetch the key at position i."""
        # NOTE: this automatically supports slicing :-)
        return self._main._sequence[index]

    def __setitem__(self, index, name):
        """
        You cannot assign to keys, but you can do slice assignment to re-order
        them.

        You can only do slice assignment if the new set of keys is a reordering
        of the original set.
        """
        if isinstance(index, types.SliceType):
            # NOTE: efficiency?
            # check length is the same
            indexes = range(len(self._main._sequence))[index]
            if len(indexes) != len(name):
                raise ValueError('attempt to assign sequence of size %s '
                    'to slice of size %s' % (len(name), len(indexes)))
            # check they are the same keys
            # NOTE: Use set
            old_keys = self._main._sequence[index]
            new_keys = list(name)
            old_keys.sort()
            new_keys.sort()
            if old_keys != new_keys:
                raise KeyError('Keylist is not the same as current keylist.')
            orig_vals = [self._main[k] for k in name]
            del self._main[index]
            vals = zip(indexes, name, orig_vals)
            vals.sort()
            for i, k, v in vals:
                if self._main.strict and k in self._main:
                    raise ValueError('slice assignment must be from '
                        'unique keys')
                self._main.insert(i, k, v)
        else:
            raise ValueError('Cannot assign to keys')

    ### following methods pinched from UserList and adapted ###
    def __repr__(self): return repr(self._main._sequence)

    # NOTE: do we need to check if we are comparing with another ``Keys``
    #   object? (like the __cast method of UserList)
    def __lt__(self, other): return self._main._sequence <  other
    def __le__(self, other): return self._main._sequence <= other
    def __eq__(self, other): return self._main._sequence == other
    def __ne__(self, other): return self._main._sequence != other
    def __gt__(self, other): return self._main._sequence >  other
    def __ge__(self, other): return self._main._sequence >= other
    # NOTE: do we need __cmp__ as well as rich comparisons?
    def __cmp__(self, other): return cmp(self._main._sequence, other)

    def __contains__(self, item): return item in self._main._sequence
    def __len__(self): return len(self._main._sequence)
    def __iter__(self): return self._main.iterkeys()
    def count(self, item): return self._main._sequence.count(item)
    def index(self, item, *args): return self._main._sequence.index(item, *args)
    def reverse(self): self._main._sequence.reverse()
    def sort(self, *args, **kwds): self._main._sequence.sort(*args, **kwds)
    def __mul__(self, n): return self._main._sequence*n
    __rmul__ = __mul__
    def __add__(self, other): return self._main._sequence + other
    def __radd__(self, other): return other + self._main._sequence

    ## following methods not implemented for keys ##
    def __delitem__(self, i): raise TypeError('Can\'t delete items from keys')
    def __iadd__(self, other): raise TypeError('Can\'t add in place to keys')
    def __imul__(self, n): raise TypeError('Can\'t multiply keys in place')
    def append(self, item): raise TypeError('Can\'t append items to keys')
    def insert(self, i, item): raise TypeError('Can\'t insert items into keys')
    def pop(self, i=-1): raise TypeError('Can\'t pop items from keys')
    def remove(self, item): raise TypeError('Can\'t remove items from keys')
    def extend(self, other): raise TypeError('Can\'t extend keys')

class Items(object):
    """
    Custom object for accessing the items of an OrderedDict.

    Can be called like the normal ``OrderedDict.items`` method, but also
    supports indexing and sequence methods.
    """

    def __init__(self, main):
        self._main = main

    def __call__(self):
        """Pretend to be the items method."""
        return self._main._items()

    def __getitem__(self, index):
        """Fetch the item at position i."""
        if isinstance(index, types.SliceType):
            # fetching a slice returns an OrderedDict
            return self._main[index].items()
        key = self._main._sequence[index]
        return (key, self._main[key])

    def __setitem__(self, index, item):
        """Set item at position i to item."""
        if isinstance(index, types.SliceType):
            # NOTE: item must be an iterable (list of tuples)
            self._main[index] = OrderedDict(item)
        else:
            # NOTE: Does this raise a sensible error?
            orig = self._main.keys[index]
            key, value = item
            if self._main.strict and key in self and (key != orig):
                raise ValueError('slice assignment must be from '
                        'unique keys')
            # delete the current one
            del self._main[self._main._sequence[index]]
            self._main.insert(index, key, value)

    def __delitem__(self, i):
        """Delete the item at position i."""
        key = self._main._sequence[i]
        if isinstance(i, types.SliceType):
            for k in key:
                # NOTE: efficiency?
                del self._main[k]
        else:
            del self._main[key]

    ### following methods pinched from UserList and adapted ###
    def __repr__(self): return repr(self._main.items())

    # NOTE: do we need to check if we are comparing with another ``Items``
    #   object? (like the __cast method of UserList)
    def __lt__(self, other): return self._main.items() <  other
    def __le__(self, other): return self._main.items() <= other
    def __eq__(self, other): return self._main.items() == other
    def __ne__(self, other): return self._main.items() != other
    def __gt__(self, other): return self._main.items() >  other
    def __ge__(self, other): return self._main.items() >= other
    def __cmp__(self, other): return cmp(self._main.items(), other)

    def __contains__(self, item): return item in self._main.items()
    def __len__(self): return len(self._main._sequence) # easier :-)
    def __iter__(self): return self._main.iteritems()
    def count(self, item): return self._main.items().count(item)
    def index(self, item, *args): return self._main.items().index(item, *args)
    def reverse(self): self._main.reverse()
    def sort(self, *args, **kwds): self._main.sort(*args, **kwds)
    def __mul__(self, n): return self._main.items()*n
    __rmul__ = __mul__
    def __add__(self, other): return self._main.items() + other
    def __radd__(self, other): return other + self._main.items()

    def append(self, item):
        """Add an item to the end."""
        # NOTE: this is only append if the key isn't already present
        key, value = item
        self._main[key] = value

    def insert(self, i, item):
        key, value = item
        self._main.insert(i, key, value)

    def pop(self, i=-1):
        key = self._main._sequence[i]
        return (key, self._main.pop(key))

    def remove(self, item):
        key, value = item
        try:
            assert value == self._main[key]
        except (KeyError, AssertionError):
            raise ValueError('ValueError: list.remove(x): x not in list')
        else:
            del self._main[key]

    def extend(self, other):
        # NOTE: is only a true extend if none of the keys already present
        for item in other:
            key, value = item
            self._main[key] = value

    def __iadd__(self, other):
        self.extend(other)

    ## following methods not implemented for items ##

    def __imul__(self, n): raise TypeError('Can\'t multiply items in place')

class Values(object):
    """
    Custom object for accessing the values of an OrderedDict.

    Can be called like the normal ``OrderedDict.values`` method, but also
    supports indexing and sequence methods.
    """

    def __init__(self, main):
        self._main = main

    def __call__(self):
        """Pretend to be the values method."""
        return self._main._values()

    def __getitem__(self, index):
        """Fetch the value at position i."""
        if isinstance(index, types.SliceType):
            return [self._main[key] for key in self._main._sequence[index]]
        else:
            return self._main[self._main._sequence[index]]

    def __setitem__(self, index, value):
        """
        Set the value at position i to value.

        You can only do slice assignment to values if you supply a sequence of
        equal length to the slice you are replacing.
        """
        if isinstance(index, types.SliceType):
            keys = self._main._sequence[index]
            if len(keys) != len(value):
                raise ValueError('attempt to assign sequence of size %s '
                    'to slice of size %s' % (len(name), len(keys)))
            # NOTE: efficiency?  Would be better to calculate the indexes
            #   directly from the slice object
            # NOTE: the new keys can collide with existing keys (or even
            #   contain duplicates) - these will overwrite
            for key, val in zip(keys, value):
                self._main[key] = val
        else:
            self._main[self._main._sequence[index]] = value

    ### following methods pinched from UserList and adapted ###
    def __repr__(self): return repr(self._main.values())

    # NOTE: do we need to check if we are comparing with another ``Values``
    #   object? (like the __cast method of UserList)
    def __lt__(self, other): return self._main.values() <  other
    def __le__(self, other): return self._main.values() <= other
    def __eq__(self, other): return self._main.values() == other
    def __ne__(self, other): return self._main.values() != other
    def __gt__(self, other): return self._main.values() >  other
    def __ge__(self, other): return self._main.values() >= other
    def __cmp__(self, other): return cmp(self._main.values(), other)

    def __contains__(self, item): return item in self._main.values()
    def __len__(self): return len(self._main._sequence) # easier :-)
    def __iter__(self): return self._main.itervalues()
    def count(self, item): return self._main.values().count(item)
    def index(self, item, *args): return self._main.values().index(item, *args)

    def reverse(self):
        """Reverse the values"""
        vals = self._main.values()
        vals.reverse()
        # NOTE: efficiency
        self[:] = vals

    def sort(self, *args, **kwds):
        """Sort the values."""
        vals = self._main.values()
        vals.sort(*args, **kwds)
        self[:] = vals

    def __mul__(self, n): return self._main.values()*n
    __rmul__ = __mul__
    def __add__(self, other): return self._main.values() + other
    def __radd__(self, other): return other + self._main.values()

    ## following methods not implemented for values ##
    def __delitem__(self, i): raise TypeError('Can\'t delete items from values')
    def __iadd__(self, other): raise TypeError('Can\'t add in place to values')
    def __imul__(self, n): raise TypeError('Can\'t multiply values in place')
    def append(self, item): raise TypeError('Can\'t append items to values')
    def insert(self, i, item): raise TypeError('Can\'t insert items into values')
    def pop(self, i=-1): raise TypeError('Can\'t pop items from values')
    def remove(self, item): raise TypeError('Can\'t remove items from values')
    def extend(self, other): raise TypeError('Can\'t extend values')

class SequenceOrderedDict(OrderedDict):
    """
    Experimental version of OrderedDict that has a custom object for ``keys``,
    ``values``, and ``items``.

    These are callable sequence objects that work as methods, or can be
    manipulated directly as sequences.

    Test for ``keys``, ``items`` and ``values``.

    >>> d = SequenceOrderedDict(((1, 2), (2, 3), (3, 4)))
    >>> d
    SequenceOrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.keys
    [1, 2, 3]
    >>> d.keys()
    [1, 2, 3]
    >>> d.setkeys((3, 2, 1))
    >>> d
    SequenceOrderedDict([(3, 4), (2, 3), (1, 2)])
    >>> d.setkeys((1, 2, 3))
    >>> d.keys[0]
    1
    >>> d.keys[:]
    [1, 2, 3]
    >>> d.keys[-1]
    3
    >>> d.keys[-2]
    2
    >>> d.keys[0:2] = [2, 1]
    >>> d
    SequenceOrderedDict([(2, 3), (1, 2), (3, 4)])
    >>> d.keys.reverse()
    >>> d.keys
    [3, 1, 2]
    >>> d.keys = [1, 2, 3]
    >>> d
    SequenceOrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.keys = [3, 1, 2]
    >>> d
    SequenceOrderedDict([(3, 4), (1, 2), (2, 3)])
    >>> a = SequenceOrderedDict()
    >>> b = SequenceOrderedDict()
    >>> a.keys == b.keys
    1
    >>> a['a'] = 3
    >>> a.keys == b.keys
    0
    >>> b['a'] = 3
    >>> a.keys == b.keys
    1
    >>> b['b'] = 3
    >>> a.keys == b.keys
    0
    >>> a.keys > b.keys
    0
    >>> a.keys < b.keys
    1
    >>> 'a' in a.keys
    1
    >>> len(b.keys)
    2
    >>> 'c' in d.keys
    0
    >>> 1 in d.keys
    1
    >>> [v for v in d.keys]
    [3, 1, 2]
    >>> d.keys.sort()
    >>> d.keys
    [1, 2, 3]
    >>> d = SequenceOrderedDict(((1, 2), (2, 3), (3, 4)), strict=True)
    >>> d.keys[::-1] = [1, 2, 3]
    >>> d
    SequenceOrderedDict([(3, 4), (2, 3), (1, 2)])
    >>> d.keys[:2]
    [3, 2]
    >>> d.keys[:2] = [1, 3]
    Traceback (most recent call last):
    KeyError: 'Keylist is not the same as current keylist.'

    >>> d = SequenceOrderedDict(((1, 2), (2, 3), (3, 4)))
    >>> d
    SequenceOrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.values
    [2, 3, 4]
    >>> d.values()
    [2, 3, 4]
    >>> d.setvalues((4, 3, 2))
    >>> d
    SequenceOrderedDict([(1, 4), (2, 3), (3, 2)])
    >>> d.values[::-1]
    [2, 3, 4]
    >>> d.values[0]
    4
    >>> d.values[-2]
    3
    >>> del d.values[0]
    Traceback (most recent call last):
    TypeError: Can't delete items from values
    >>> d.values[::2] = [2, 4]
    >>> d
    SequenceOrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> 7 in d.values
    0
    >>> len(d.values)
    3
    >>> [val for val in d.values]
    [2, 3, 4]
    >>> d.values[-1] = 2
    >>> d.values.count(2)
    2
    >>> d.values.index(2)
    0
    >>> d.values[-1] = 7
    >>> d.values
    [2, 3, 7]
    >>> d.values.reverse()
    >>> d.values
    [7, 3, 2]
    >>> d.values.sort()
    >>> d.values
    [2, 3, 7]
    >>> d.values.append('anything')
    Traceback (most recent call last):
    TypeError: Can't append items to values
    >>> d.values = (1, 2, 3)
    >>> d
    SequenceOrderedDict([(1, 1), (2, 2), (3, 3)])

    >>> d = SequenceOrderedDict(((1, 2), (2, 3), (3, 4)))
    >>> d
    SequenceOrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.items()
    [(1, 2), (2, 3), (3, 4)]
    >>> d.setitems([(3, 4), (2 ,3), (1, 2)])
    >>> d
    SequenceOrderedDict([(3, 4), (2, 3), (1, 2)])
    >>> d.items[0]
    (3, 4)
    >>> d.items[:-1]
    [(3, 4), (2, 3)]
    >>> d.items[1] = (6, 3)
    >>> d.items
    [(3, 4), (6, 3), (1, 2)]
    >>> d.items[1:2] = [(9, 9)]
    >>> d
    SequenceOrderedDict([(3, 4), (9, 9), (1, 2)])
    >>> del d.items[1:2]
    >>> d
    SequenceOrderedDict([(3, 4), (1, 2)])
    >>> (3, 4) in d.items
    1
    >>> (4, 3) in d.items
    0
    >>> len(d.items)
    2
    >>> [v for v in d.items]
    [(3, 4), (1, 2)]
    >>> d.items.count((3, 4))
    1
    >>> d.items.index((1, 2))
    1
    >>> d.items.index((2, 1))
    Traceback (most recent call last):
    ValueError: list.index(x): x not in list
    >>> d.items.reverse()
    >>> d.items
    [(1, 2), (3, 4)]
    >>> d.items.reverse()
    >>> d.items.sort()
    >>> d.items
    [(1, 2), (3, 4)]
    >>> d.items.append((5, 6))
    >>> d.items
    [(1, 2), (3, 4), (5, 6)]
    >>> d.items.insert(0, (0, 0))
    >>> d.items
    [(0, 0), (1, 2), (3, 4), (5, 6)]
    >>> d.items.insert(-1, (7, 8))
    >>> d.items
    [(0, 0), (1, 2), (3, 4), (7, 8), (5, 6)]
    >>> d.items.pop()
    (5, 6)
    >>> d.items
    [(0, 0), (1, 2), (3, 4), (7, 8)]
    >>> d.items.remove((1, 2))
    >>> d.items
    [(0, 0), (3, 4), (7, 8)]
    >>> d.items.extend([(1, 2), (5, 6)])
    >>> d.items
    [(0, 0), (3, 4), (7, 8), (1, 2), (5, 6)]
    """

    def __init__(self, init_val=(), strict=True):
        OrderedDict.__init__(self, init_val, strict=strict)
        self._keys = self.keys
        self._values = self.values
        self._items = self.items
        self.keys = Keys(self)
        self.values = Values(self)
        self.items = Items(self)
        self._att_dict = {
            'keys': self.setkeys,
            'items': self.setitems,
            'values': self.setvalues,
        }

    def __setattr__(self, name, value):
        """Protect keys, items, and values."""
        if not '_att_dict' in self.__dict__:
            object.__setattr__(self, name, value)
        else:
            try:
                fun = self._att_dict[name]
            except KeyError:
                OrderedDict.__setattr__(self, name, value)
            else:
                fun(value)


#
# Imported from OrderedConfigParser.py
#

#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import ConfigParser
import StringIO

if not 'OrderedDict' in dir():
    from odict import OrderedDict


class OrderedConfigParser(ConfigParser.ConfigParser):
    """
    Customization of ConfigParser to (a) use an ordered dictionary and (b)
    keep the original case of the data keys.
    """

    def __init__(self):
        if sys.version >= (2,6,0):
            ConfigParser.ConfigParser.__init__(self, dict_type=OrderedDict)
        else:
            ConfigParser.ConfigParser.__init__(self)
            self._defaults = OrderedDict()
            self._sections = OrderedDict()

    def _get_sections(self, fp):
        """
        In old version of Python, we prefetch the sections, to
        ensure that the data structures we are using are OrderedDict.
        """
        if sys.version >= (2,6,0):
            return
        while True:
            line = fp.readline()
            if not line:
                break
            line.strip()
            mo = self.SECTCRE.match(line)
            if mo:
                sectname = mo.group('header')
                if not sectname in self._sections:
                    self._sections[sectname] = OrderedDict()
                    self._sections[sectname]['__name__'] = sectname

    def _read(self, fp, fpname):
        """Parse a sectoned setup file.

        This first calls _get_sections to preparse the section info,
        and then calls the ConfigParser._read method.
        """
        self._get_sections(fp)
        fp.seek(0)
        return ConfigParser.ConfigParser._read(self, fp, fpname)

    def optionxform(self, option):
        """Do not convert to lower case"""
        return option


#
# Imported from header.py
#

#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#
#
# This script was created with the virtualenv_install script.
#

import commands
import re
import urllib2
import zipfile
import shutil
import string
import textwrap
import sys
import glob
import errno
import stat

using_subversion = True

#
# Working around error with PYTHONHOME
#
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']
    print "WARNING: ignoring the value of the PYTHONHOME environment variable!  This value can corrupt the virtual python installation."

print "\nNOTE: this Python executable used to create virtual environment:\n\t%s\n" % sys.executable
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
    if using_subversion and not sys.platform.startswith('win'):
        output = commands.getoutput('svn ls '+svndir)
        if output=="":
            return None
        #print output
        versions = []
        for link in re.split('/',output.strip()):
            tmp = link.strip()
            if tmp != '':
                versions.append( tmp )
        #print versions
    else:
        if sys.version_info[:2] <= (2,5):
            output = urllib2.urlopen(svndir).read()
        else:
            output = urllib2.urlopen(svndir, timeout=30).read()
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
    if latest_str is None:
        return None
    if not latest_str[0] in '0123456789':
        return svndir
    return svndir+"/"+latest_str



def zip_file(filename,fdlist):
    zf = zipfile.ZipFile(filename, 'w')
    for file in fdlist:
        if os.path.isdir(file):
            for root, dirs, files in os.walk(file):
                if root.startswith(file+os.sep+'lib') or root.startswith(file+os.sep+'bin'):
                    continue
                for fname in files:
                    if fname.endswith('pyc') or fname.endswith('pyo') or fname.endswith('zip'):
                        continue
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

    svn_get='checkout'
    easy_install_path = ["easy_install"]
    easy_install_flag = '-q'
    pip_path = ["pip"]
    python = "python"
    svn = "svn"
    dev = []

    def __init__(self, name, root=None, trunk=None, stable=None, release=None, tag=None, pyname=None, pypi=None, dev=False, username=None, install=True, rev=None, local=None, platform=None):
        class _TEMP_(object): pass
        self.config = _TEMP_()
        self.config.name=name
        self.config.root=root
        self.config.trunk=trunk
        self.config.stable=stable
        self.config.release=release
        self.config.tag=tag
        self.config.pyname=pyname
        self.config.pypi=pypi
        self.config.local=local
        self.config.platform=platform
        if dev == 'True' or dev is True:
            self.config.dev=True
        else:
            self.config.dev=False
        self.config.username=username
        if install == 'False' or install is False:
            self.config.install=False
        else:
            self.config.install=True
        self.config.rev=rev
        self.initialize(self.config)

    def initialize(self, config):
        self.name = config.name
        self.root = config.root
        self.trunk = None
        self.trunk_root = None
        self.stable = None
        self.stable_root = None
        self.release = None
        self.tag = None
        self.release_root = None
        #
        self.pypi = config.pypi
        self.local = config.local
        self.platform = config.platform
        if config.platform is None:
            self.platform_re = None
        else:
            self.platform_re = re.compile(config.platform)
        if not config.pypi is None:
            self.pyname=config.pypi
        else:
            self.pyname=config.pyname
        self.dev = config.dev
        if config.dev:
            Repository.dev.append(config.name)
        self.pkgdir = None
        self.pkgroot = None
        if config.username is None or '$' in config.username:
            self.svn_username = []
        else:
            self.svn_username = ['--username', config.username]
        if config.rev is None:
            self.rev=''
            self.revarg=[]
        else:
            self.rev='@'+config.rev
            self.revarg=['-r',config.rev]
        self.install = config.install

    def guess_versions(self, offline=False):
        if not self.config.root is None:
            if not offline:
                if using_subversion and not sys.platform.startswith('win'):
                    rootdir_output = commands.getoutput('svn ls ' + self.config.root)
                else:
                    if sys.version_info[:2] <= (2,5):
                        rootdir_output = urllib2.urlopen(self.config.root).read()
                    else:
                        rootdir_output = urllib2.urlopen(self.config.root, timeout=30).read()
            self.trunk = self.config.root+'/trunk'
            self.trunk_root = self.trunk
            try:
                if offline or not 'stable' in rootdir_output:
                    raise IOError
                self.stable = guess_release(self.config.root+'/stable')
                self.stable_root = self.stable
            except (urllib2.HTTPError,IOError):
                self.stable = None
                self.stable_root = None
            try:
                if offline or not 'releases' in rootdir_output:
                    raise IOError
                self.release = guess_release(self.config.root+'/releases')
                self.tag = None
                self.release_root = self.release
            except (urllib2.HTTPError,IOError):
                try:
                    if offline or not 'tags' in rootdir_output:
                        raise IOError
                    self.release = guess_release(self.config.root+'/tags')
                    self.tag = self.release
                    self.release_root = self.release
                except (urllib2.HTTPError,IOError):
                    self.release = None
                    self.release_root = None
        if not self.config.trunk is None:
            if self.trunk is None:
                self.trunk = self.config.trunk
            else:
                self.trunk += self.config.trunk
        if not self.config.stable is None:
            if self.stable is None:
                self.stable = self.config.stable
            else:
                self.stable += self.config.stable
        if not self.config.release is None:
            if self.release is None:
                self.release = self.config.release
            else:
                self.release += self.config.release
        if not self.config.tag is None:
            if self.release is None:
                self.release = self.config.tag
            else:
                self.release += self.config.tag


    def write_config(self, OUTPUT):
        config = self.config
        print >>OUTPUT, '[%s]' % config.name
        if not config.root is None:
            print >>OUTPUT, 'root=%s' % config.root
        if not config.trunk is None:
            print >>OUTPUT, 'trunk=%s' % config.trunk
        if not config.stable is None:
            print >>OUTPUT, 'stable=%s' % config.stable
        if not config.tag is None:
            print >>OUTPUT, 'tag=%s' % config.tag
        elif not config.release is None:
            print >>OUTPUT, 'release=%s' % config.release
        if not config.local is None:
            print >>OUTPUT, 'local=%s' % config.local
        if not config.pypi is None:
            print >>OUTPUT, 'pypi=%s' % config.pypi
        elif not config.pyname is None:
            print >>OUTPUT, 'pypi=%s' % config.pyname
        print >>OUTPUT, 'dev=%s' % str(config.dev)
        print >>OUTPUT, 'install=%s' % str(config.install)
        if not config.rev is None:
            print >>OUTPUT, 'rev=%s' % str(config.rev)
        if not config.username is None:
            print >>OUTPUT, 'username=%s' % str(config.username)
        if not config.platform is None:
            print >>OUTPUT, 'platform=%s' % config.platform


    def find_pkgroot(self, trunk=False, stable=False, release=False):
        if trunk:
            if self.trunk is None:
                if not self.stable is None:
                    self.find_pkgroot(stable=True)
                elif self.pypi is None and self.local is None:
                    self.find_pkgroot(release=True)
                else:
                    # use easy_install
                    self.pkgdir = None
                    self.pkgroot = None
                    return
            else:
                self.pkgdir = self.trunk
                self.pkgroot = self.trunk_root
                return

        elif stable:
            if self.stable is None:
                if not self.release is None:
                    self.find_pkgroot(release=True)
                elif self.pypi is None and self.local is None:
                    self.find_pkgroot(trunk=True)
                else:
                    # use easy_install
                    self.pkgdir = None
                    self.pkgroot = None
                    return
            else:
                self.pkgdir = self.stable
                self.pkgroot = self.stable_root
                return

        elif release:
            if self.release is None:
                if not self.stable is None:
                    self.find_pkgroot(stable=True)
                elif self.pypi is None and self.local is None:
                    self.find_pkgroot(trunk=True)
                else:
                    # use easy_install
                    self.pkgdir = None
                    self.pkgroot = None
                    return
            else:
                self.pkgdir = self.release
                self.pkgroot = self.release_root

        else:
            raise IOError, "Must have one of trunk, stable or release specified"


    def install_trunk(self, dir=None, install=True, preinstall=False, offline=False):
        self.find_pkgroot(trunk=True)
        self.perform_install(dir=dir, install=install, preinstall=preinstall, offline=offline)

    def install_stable(self, dir=None, install=True, preinstall=False, offline=False):
        self.find_pkgroot(stable=True)
        self.perform_install(dir=dir, install=install, preinstall=preinstall, offline=offline)

    def install_release(self, dir=None, install=True, preinstall=False, offline=False):
        self.find_pkgroot(release=True)
        self.perform_install(dir=dir, install=install, preinstall=preinstall, offline=offline)

    def perform_install(self, dir=None, install=True, preinstall=False, offline=False):
        if not self.platform_re is None and not self.platform_re.match(sys.platform):
            return
        if self.pkgdir is None and self.local is None:
            self.easy_install(install, preinstall, dir, offline)
            return
        if self.local:
            install = True
        print "-----------------------------------------------------------------"
        print "  Installing branch"
        print "  Checking out source for package",self.name
        if self.local:
            print "     Package dir: "+self.local
        else:
            print "     Subversion dir: "+self.pkgdir
        if os.path.exists(dir):
            print "     No checkout required"
            print "-----------------------------------------------------------------"
        elif not using_subversion:
            print ""
            print "Error: Cannot checkout software %s with subversion." % self.name
            print "A problem was detected executing subversion commands."
            sys.exit(1)
        else:
            print "-----------------------------------------------------------------"
            try:
                self.run([self.svn]+self.svn_username+[Repository.svn_get,'-q',self.pkgdir+self.rev, dir])
            except OSError, err:
                print ""
                print "Error checkout software %s with subversion at %s" % (self.name,self.pkgdir+self.rev)
                print str(err)
                sys.exit(1)
        if install:
            try:
                if self.dev:
                    if offline:
                        self.run([self.python, 'setup.py', 'develop', '--no-deps'], dir=dir)
                    else:
                        self.run([self.python, 'setup.py', 'develop'], dir=dir)
                else:
                    self.run([self.python, 'setup.py', 'install'], dir=dir)
            except OSError, err:
                print ""
                print "Error installing software %s from source using the setup.py file." % self.name
                print "This is probably due to a syntax or configuration error in this package."
                print str(err)
                sys.exit(1)

    def update_trunk(self, dir=None):
        self.find_pkgroot(trunk=True)
        self.perform_update(dir=dir)

    def update_stable(self, dir=None):
        self.find_pkgroot(stable=True)
        self.perform_update(dir=dir)

    def update_release(self, dir=None):
        self.find_pkgroot(release=True)
        self.perform_update(dir=dir)

    def perform_update(self, dir=None):
        if self.pkgdir is None:
            self.easy_upgrade()
            return
        print "-----------------------------------------------------------------"
        print "  Updating branch"
        print "  Updating source for package",self.name
        print "     Subversion dir: "+self.pkgdir
        print "     Source dir:     "+dir
        print "-----------------------------------------------------------------"
        self.run([self.svn,'update','-q']+self.revarg+[dir])
        if self.dev:
            self.run([self.python, 'setup.py', 'develop'], dir=dir)
        else:
            self.run([self.python, 'setup.py', 'install'], dir=dir)

    def easy_install(self, install, preinstall, dir, offline):
        #return self.pip_install(install, preinstall, dir, offline)
        try:
            if install:
                if offline:
                    self.run([self.python, 'setup.py', 'install'], dir=dir)
                else:
                    self.run(self.easy_install_path + [Repository.easy_install_flag, self.pypi], dir=os.path.dirname(dir))
            elif preinstall:
                if not os.path.exists(dir):
                    self.run(self.easy_install_path + [Repository.easy_install_flag, '--exclude-scripts', '--always-copy', '--editable', '--build-directory', '.', self.pypi], dir=os.path.dirname(dir))
        except OSError, err:
            print ""
            print "Error installing package %s with easy_install" % self.name
            print str(err)
            sys.exit(1)

    def pip_install(self, install, preinstall, dir, offline):
        try:
            if install:
                if offline:
                    self.run([self.python, 'setup.py', 'install'], dir=dir)
                else:
                    self.run(self.pip_path + ['-v', self.pypi])
            elif preinstall:
                if not os.path.exists(dir):
                    self.run(self.pip_path + ['-v', '--no-install', '--download', '.', self.pypi], dir=os.path.dirname(dir))
        except OSError, err:
            print ""
            print "Error installing package %s with pip" % self.name
            print str(err)
            sys.exit(1)

    def easy_upgrade(self):
        self.run(self.easy_install_path + [Repository.easy_install_flag, '--upgrade', self.pypi])

    def run(self, cmd, dir=None):
        cwd=os.getcwd()
        if not dir is None:
            os.chdir(dir)
            cwd=dir
        print "Running command '%s' in directory %s" % (" ".join(cmd), cwd)
        sys.stdout.flush()
        call_subprocess(cmd, filter_stdout=filter_python_develop, show_stdout=True)
        if not dir is None:
            os.chdir(cwd)


if sys.platform.startswith('win'):
    if not is_jython:
        Repository.python += 'w.exe'
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


def apply_template(str, d):
    t = string.Template(str)
    return t.safe_substitute(d)


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
        self.srcdir = None
        self.config=None
        self.config_file=None
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
        if not 'root' in kwds and not 'pypi' in kwds and not 'release' in kwds and not 'trunk' in kwds and not 'stable' in kwds:
            raise IOError, "No repository info specified for repository "+args[0]
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
        parser.add_option('--debug',
            help='Configure script to generate debugging IO and to raise exceptions.',
            action='store_true',
            dest='debug',
            default=False)

        parser.add_option('--release',
            help='Install release branches of Python software using subversion.',
            action='store_true',
            dest='release',
            default=False)

        parser.add_option('--trunk',
            help='Install trunk branches of Python software using subversion.',
            action='store_true',
            dest='trunk',
            default=False)

        parser.add_option('--stable',
            help='Install stable branches of Python software using subversion.',
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

        parser.add_option('--source', '--src',
            help='Use packages defined in the specified source directory',
            action='store',
            dest='source',
            default=None)

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

        parser.add_option(
            '-a', '--add-package',
            dest='packages',
            action='append',
            help='Specify a package that is added to the virtual Python installation.  This option can specify a directory for the Python package source or PyPI package name that is downloaded automatically.  This option can be specified multiple times to declare multiple packages.',
            default=[])

        parser.add_option('--config',
            help='Use an INI config file to specify the packages used in this installation.  Using this option clears the initial configuration, but multiple uses of this option will add package specifications.',
            action='append',
            dest='config_files',
            default=[])

        parser.add_option('--keep-config',
            help='Keep the initial configuration data that was specified if the --config option is specified.',
            action='store_true',
            dest='keep_config',
            default=False)

        parser.add_option('--without-externals',
            help="Ignore the 'externals' section of the config file.",
            action='store_false',
            dest='follow_externals',
            default=True)

        parser.add_option('--localize',
            help='Force localization of DOS scripts on Linux platforms',
            action='store_true',
            dest='localize',
            default=False)

        #
        # Change the virtualenv options
        #
        parser.remove_option("--python")
        parser.add_option("--python",
            dest='python',
            metavar='PYTHON_EXE',
            help="Specify the Python interpreter to use, e.g., --python=python2.5 will install with the python2.5 interpreter.")
        parser.remove_option("--relocatable")
        parser.remove_option("--version")
        parser.remove_option("--unzip-setuptools")
        parser.remove_option("--no-site-packages")
        parser.remove_option("--clear")
        #
        # Add description
        #
        parser.description=self.description
        parser.epilog="If DEST_DIR is not specified, then a default installation path is used:  "+self.default_windir+" on Windows and "+self.default_unixdir+" on Linux.  This command uses the Python 'setuptools' package to install Python packages.  This package installs packages by downloading files from the internet.  If you are running this from within a firewall, you may need to set the HTTP_PROXY environment variable to a value like 'http://<proxyhost>:<port>'."


    def adjust_options(self, options, args):
        #
        # Force options.clear to be False.  This allows us to preserve the logic
        # associated with --clear, which we may want to use later.
        #
        options.clear=False
        #
        global vpy_main
        if options.debug:
            vpy_main.raise_exceptions=True
        #
        global logger
        if options.verbose:
            Repository.easy_install_flag = '-v'
        verbosity = options.verbose - options.quiet
        self.logger = Logger([(Logger.level_for_integer(2-verbosity), sys.stdout)])
        logger = self.logger
        #
        # Determine if the subversion command is available
        #
        global using_subversion
        try:
            sys.stdout.flush()
            call_subprocess(['svn'+executable_extension,'help'], show_stdout=False)
        except OSError, err:
            print ""
            print "------------------------------------------------"
            print "WARNING: problems executing subversion commands."
            print "Subversion is disabled."
            print "------------------------------------------------"
            print ""
            using_subversion = False
        #
        if options.update and (options.stable or options.trunk):
            self.logger.fatal("ERROR: cannot specify --stable or --trunk when specifying the --update option.")
            sys.exit(1000)
        if options.update and len(options.config_files) > 0:
            self.logger.fatal("ERROR: cannot specify --config when specifying the --update option.")
            sys.exit(1000)
        if options.update and options.keep_config:
            self.logger.fatal("ERROR: cannot specify --keep-config when specifying the --update option.")
            sys.exit(1000)
        if len(args) > 1:
            self.logger.fatal("ERROR: installer script can only have one argument")
            sys.exit(1000)
        #
        # Error checking
        #
        if not options.preinstall and (os.path.exists(self.abshome_dir) ^ options.update):
            if options.update:
                self.logger.fatal(wrapper.fill("ERROR: The 'update' option is specified, but the installation path '%s' does not exist!" % self.home_dir))
                sys.exit(1000)
            elif os.path.exists(join(self.abshome_dir,'bin')):
                self.logger.fatal(wrapper.fill("ERROR: The installation path '%s' already exists!  Use the --update option if you wish to update, or remove this directory to create a fresh installation." % self.home_dir))
                sys.exit(1000)
        if len(args) == 0:
            args.append(self.abshome_dir)
        #
        # Reset the config file if no options are specified
        #
        if not self.config_file is None and not (options.trunk or options.stable or options.release):
            self.config_file = os.path.dirname(self.config_file)+"/pypi.ini"
        #
        # Parse config files
        #
        if options.update:
            self.config=None
            options.config_files.append( join(self.abshome_dir, 'admin', 'config.ini') )
        if not self.config is None and (len(options.config_files) == 0 or options.keep_config):
            fp = StringIO.StringIO(self.config)
            self.read_config_file(fp=fp, follow_externals=options.follow_externals)
            fp.close()
        if not self.config_file is None and (len(options.config_files) == 0 or options.keep_config):
            self.read_config_file(file=self.config_file, follow_externals=options.follow_externals)
        for file in options.config_files:
            self.read_config_file(file=file, follow_externals=options.follow_externals)
        print "-----------------------------------------------------------------"
        print "Finished processing configuration information."
        print "-----------------------------------------------------------------"
        print " START - Configuration summary"
        print "-----------------------------------------------------------------"
        self.write_config(stream=sys.stdout)
        print "-----------------------------------------------------------------"
        print " END - Configuration summary"
        print "-----------------------------------------------------------------"
        #
        # If applying preinstall, then only do subversion exports
        #
        if options.preinstall:
            Repository.svn_get='export'

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
        if options.source is None:
            self.srcdir = join(self.abshome_dir,'src')
        else:
            self.srcdir = os.path.abspath(options.source)
            if not os.path.exists(self.srcdir):
                raise ValueError, "Specified source directory does not exist! %s" % self.srcdir

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
        if options.offline:
            os.environ['HTTP_PROXY'] = ''
            os.environ['http_proxy'] = ''
        else:
            proxy = ''
            if not options.proxy is None:
                proxy = options.proxy
            if proxy is '':
                proxy = os.environ.get('HTTP_PROXY', '')
            if proxy is '':
                proxy = os.environ.get('http_proxy', '')
            os.environ['HTTP_PROXY'] = proxy
            os.environ['http_proxy'] = proxy
            print "  using the HTTP_PROXY environment: %s" % proxy
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
        # When preinstalling or working offline, disable the
        # default install_setuptools() function.
        #
        if options.offline:
            install_setuptools.use_default=False
            install_pip.use_default=False
        #
        # If we're clearing the current installation, then remove a bunch of
        # directories
        #
        elif options.clear and not options.source is None:
            if os.path.exists(self.srcdir):
                rmtree(self.srcdir)
        #
        # Open up zip files
        #
        for file in options.zip:
            unzip_file(file, dir=self.abshome_dir)

        if options.preinstall or not options.offline:
            #self.get_packages(options)
            pass
        else:
            self.sw_packages.insert( 0, Repository('virtualenv', pypi='virtualenv') )
            self.sw_packages.insert( 0, Repository('pip', pypi='pip') )
            self.sw_packages.insert( 0, Repository('distribute', pypi='distribute') )
            self.sw_packages.insert( 0, Repository('setuptools', pypi='setuptools') )
            #
            # Configure the package versions, for offline installs
            #
            for pkg in self.sw_packages:
                pkg.guess_versions(True)

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
            options.release = INPUT.readline().strip() != 'False'
            INPUT.close()
        else:
            OUTPUT=open(join(self.abshome_dir,'admin',"virtualenv.cfg"),'w')
            print >>OUTPUT, options.trunk
            print >>OUTPUT, options.stable
            print >>OUTPUT, options.release
            OUTPUT.close()
            self.write_config( join(self.abshome_dir,'admin','config.ini') )
        #
        # Setup package directories
        #
        if not os.path.exists(join(self.abshome_dir,'dist')):
            os.mkdir(join(self.abshome_dir,'dist'))
        if not os.path.exists(self.srcdir):
            os.mkdir(self.srcdir)
        if not os.path.exists(self.abshome_dir+os.sep+"bin"):
            os.mkdir(self.abshome_dir+os.sep+"bin")
        #
        # Get source packages
        #
        self.sw_packages.insert( 0, Repository('virtualenv', pypi='virtualenv') )
        self.sw_packages.insert( 0, Repository('pip', pypi='pip') )
        if options.preinstall:
            #
            # When preinstalling, add the setuptools package to the installation list
            #
            self.sw_packages.insert( 0, Repository('distribute', pypi='distribute') )
            self.sw_packages.insert( 0, Repository('setuptools', pypi='setuptools') )
        for _pkg in options.packages:
            if os.path.exists(_pkg):
                self.sw_packages.append( Repository(_pkg, local=os.path.abspath(_pkg)) )
            else:
                self.sw_packages.append( Repository(_pkg, pypi=_pkg) )
        #
        # Add Coopr Forum packages
        #
        self.get_other_packages(options)
        #
        # Get package source
        #
        for pkg in self.sw_packages:
            pkg.guess_versions(False)
            if not pkg.install:
                pkg.find_pkgroot(trunk=options.trunk, stable=options.stable, release=options.release)
                continue
            if pkg.local:
                tmp = pkg.local
            elif pkg.dev:
                tmp = join(self.srcdir,pkg.name)
            else:
                tmp = join(self.abshome_dir,'dist',pkg.name)
            if options.trunk:
                if not options.update:
                    pkg.install_trunk(dir=tmp, install=False, preinstall=options.preinstall, offline=options.offline)
            elif options.stable:
                if not options.update:
                    pkg.install_stable(dir=tmp, install=False, preinstall=options.preinstall, offline=options.offline)
            else:
                if not options.update:
                    pkg.install_release(dir=tmp, install=False, preinstall=options.preinstall, offline=options.offline)
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

    def get_other_packages(self, options):
        #
        # Used by subclasses of Installer to
        # add packages that were requested through other means....
        #
        pass

    def install_packages(self, options):
        #
        # Set the bin directory
        #
        if os.path.exists(self.abshome_dir+os.sep+"Scripts"):
            bindir = join(self.abshome_dir,"Scripts")
        else:
            bindir = join(self.abshome_dir,"bin")
        if is_jython:
            Repository.python = os.path.abspath(join(bindir, 'jython.bat'))
        #elif sys.platform.startswith('win'):
            #Repository.python = os.path.abspath(join(bindir, 'python'))
        else:
            Repository.python = os.path.abspath(join(bindir, 'python'))
        if os.path.exists(os.path.abspath(join(bindir, 'easy_install'))):
            Repository.easy_install_path = [Repository.python, os.path.abspath(join(bindir, 'easy_install'))]
        else:
            Repository.easy_install_path = [os.path.abspath(join(bindir, 'easy_install.exe'))]
        if os.path.exists(os.path.abspath(join(bindir, 'pip'))):
            Repository.pip_path = [Repository.python, os.path.abspath(join(bindir, 'pip'))]
        else:
            Repository.pip_path = [os.path.abspath(join(bindir, 'pip.exe'))]
        #
        if options.preinstall or not options.offline:
            self.get_packages(options)
        #
        # Install the related packages
        #
        for pkg in self.sw_packages:
            if not pkg.install:
                pkg.find_pkgroot(trunk=options.trunk, stable=options.stable, release=options.release)
                continue
            if pkg.local:
                srcdir = pkg.local
            elif pkg.dev:
                srcdir = join(self.srcdir,pkg.name)
            else:
                srcdir = join(self.abshome_dir,'dist',pkg.name)
            if options.trunk:
                if options.update:
                    pkg.update_trunk(dir=srcdir)
                else:
                    pkg.install_trunk(dir=srcdir, preinstall=options.preinstall, offline=options.offline)
            elif options.stable:
                if options.update:
                    pkg.update_stable(dir=srcdir)
                else:
                    pkg.install_stable(dir=srcdir, preinstall=options.preinstall, offline=options.offline)
            else:
                if options.update:
                    pkg.update_release(dir=srcdir)
                else:
                    pkg.install_release(dir=srcdir, preinstall=options.preinstall, offline=options.offline)
        #
        # Localize DOS cmd files
        #
        self.localize_cmd_files(self.abshome_dir, options.localize)
        #
        # Copy the <env>/Scripts/* files into <env>/bin
        #
        if os.path.exists(self.abshome_dir+os.sep+"Scripts"):
            if not os.path.exists(self.abshome_dir+os.sep+"bin"):
                os.mkdir(self.abshome_dir+os.sep+"bin")
            for file in glob.glob(self.abshome_dir+os.sep+"Scripts"+os.sep+"*"):
                shutil.copy(file, self.abshome_dir+os.sep+"bin")
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

    def localize_cmd_files(self, dir, force_localization=False):
        """
        Hard-code the path to Python that is used in the Python CMD files that
        are installed.
        """
        if not (sys.platform.startswith('win') or force_localization):
            return
        if os.path.exists(dir+os.sep+"Scripts"):
            bindir = 'Scripts'
        else:
            bindir = 'bin'
        for file in self.cmd_files:
            fname = join(dir,bindir,file)
            if not os.path.exists(fname):
                print "WARNING: Problem while localizing file '%s'.  This file is missing" % fname
                continue
            INPUT = open(fname, 'r')
            content = "".join(INPUT.readlines())
            INPUT.close()
            content = content.replace('__VIRTUAL_ENV__',dir)
            OUTPUT = open(fname, 'w')
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
                cmd = [Repository.svn,Repository.svn_get,'-q',self.svnjoin(pkgroot,fromdir),join(self.abshome_dir,todir)]
            print "Running command '%s'" % " ".join(cmd)
            sys.stdout.flush()
            call_subprocess(cmd, filter_stdout=filter_python_develop,show_stdout=True)

    def read_config_file(self, file=None, fp=None, follow_externals=True):
        """
        Read a config file.
        """
        parser = OrderedConfigParser()
        if not fp is None:
            parser.readfp(fp, '<default configuration>')
        elif not os.path.exists(file):
            if not '/' in file and not self.config_file is None:
                file = os.path.dirname(self.config_file)+"/"+file
            try:
                if sys.version_info[:2] <= (2,5):
                    output = urllib2.urlopen(file).read()
                else:
                    output = urllib2.urlopen(file, timeout=30).read()
            except Exception, err:
                print "Problems opening configuration url:",file
                raise
            fp = StringIO.StringIO(output)
            parser.readfp(fp, file)
            fp.close()
        else:
            if not file in parser.read(file):
                raise IOError, "Error while parsing file %s." % file
        sections = parser.sections()
        if 'installer' in sections:
            for option, value in parser.items('installer'):
                setattr(self, option, apply_template(value, os.environ) )
        if follow_externals and 'externals' in sections:
            for option, value in parser.items('externals'):
                self.read_config_file(file=value, follow_externals=follow_externals)
        if 'localize' in sections:
            for option, value in parser.items('localize'):
                self.add_dos_cmd(option)
        for sec in sections:
            if sec in ['installer', 'localize', 'externals']:
                continue
            if sec.endswith(':auxdir'):
                auxdir = sec[:-7]
                for option, value in parser.items(sec):
                    self.add_auxdir(auxdir, option, apply_template(value, os.environ) )
            else:
                options = {}
                for option, value in parser.items(sec):
                    options[option] = apply_template(value, os.environ)
                self.add_repository(sec, **options)

    def write_config(self, filename=None, stream=None):
        if not filename is None:
            OUTPUT=open(filename,'w')
            self.write_config(stream=OUTPUT)
            OUTPUT.close()
        else:
            for repos in self.sw_packages:
                repos.write_config(stream)
                print >>stream, ""
            if len(self.cmd_files) > 0:
                print >>stream, "[localize]"
                for file in self.cmd_files:
                    print >>stream, file+"="
                print >>stream, "\n"



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
# Override the default definition of rmtree, to better handle MSWindows errors
# that are associated with read-only files
#
def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise

def rmtree(dir):
    if os.path.exists(dir):
        logger.notify('Deleting tree %s', dir)
        shutil.rmtree(dir, ignore_errors=False, onerror=handleRemoveReadonly)
    else:
        logger.info('Do not need to delete %s; already gone', dir)

#
# This is a monkey patch, to add control for exception management.
#
vpy_main = main
vpy_main.raise_exceptions=False
def main():
    if sys.platform != 'win32':
        if os.environ.get('TMPDIR','') == '.':
            os.environ['TMPDIR'] = '/tmp'
        elif os.environ.get('TEMPDIR','') == '.':
            os.environ['TEMPDIR'] = '/tmp'
    try:
        vpy_main()
    except Exception, err:
        if vpy_main.raise_exceptions:
            raise
        print ""
        print "ERROR:",str(err)

#
# This is a monkey patch, to control the execution of the install_setuptools()
# function that is defined by virtualenv.
#
default_install_setuptools = install_setuptools


def install_setuptools(py_executable, unzip=False,
                       search_dirs=None, never_download=False):
    try:
        if install_setuptools.use_default:
            default_install_setuptools(py_executable, unzip, search_dirs, never_download)
    except OSError, err:
        print "-----------------------------------------------------------------"
        print "Error installing the 'setuptools' package!"
        if os.environ['HTTP_PROXY'] == '':
            print ""
            print "WARNING: you may need to set your HTTP_PROXY environment variable!"
        print "-----------------------------------------------------------------"
        sys.exit(1)

install_setuptools.use_default=True


#
# This is a monkey patch, to control the execution of the install_pip()
# function that is defined by virtualenv.
#
default_install_pip = install_pip

def install_pip(*args, **kwds):
    try:
        if install_pip.use_default:
            default_install_pip(*args, **kwds)
    except OSError, err:
        print "-----------------------------------------------------------------"
        print "Error installing the 'pip' package!"
        if os.environ['HTTP_PROXY'] == '':
            print ""
            print "WARNING: you may need to set your HTTP_PROXY environment variable!"
        print "-----------------------------------------------------------------"
        sys.exit(1)

install_pip.use_default=True


#
# This is a monkey patch, to catch errors when a directory cannot be created
# by virtualenv.
#
def mkdir(path):
    if not os.path.exists(path):
        logger.info('Creating %s', path)
        try:
            os.makedirs(path)
        except Exception, e:
            print "Cannot create directory '%s'!" % path
            print "Verify that you have write permissions to this directory."
            sys.exit(1)
    else:
        logger.info('Directory %s already exists', path)

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



def convert(s):
    b = base64.b64decode(s.encode('ascii'))
    return zlib.decompress(b).decode('utf-8')
    
##file site.py
SITE_PY = convert("""
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
""")





##file ez_setup.py
EZ_SETUP_PY = convert("""
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
BDaonX65d/fwEjNqlDjLVIvM9X+XVxF7
""")





##file distribute_setup.py
DISTRIBUTE_SETUP_PY = convert("""
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
""")





##file activate.sh
ACTIVATE_SH = convert("""
eJytVU1v4jAQPW9+xTT0ANVS1GsrDlRFAqmFqmG72m0rY5IJsRRslDiktNr/vuMQ8tFQpNU2B4I9
H36eeW/SglkgYvBFiLBKYg0LhCRGD1KhA7BjlUQuwkLIHne12HCNNpz5kVrBgsfBmdWCrUrA5VIq
DVEiQWjwRISuDreW5eE+CtodeLeAnhZEGKMGFXqAciMiJVcoNWx4JPgixDjzEj48QVeCfcqmtzfs
cfww+zG4ZfeD2ciGF7gCHaDMPM1jtvuHXAsPfF2rSGeOxV4iDY5GUGb3xVEYv2aj6WQ0vRseAlMY
G5DKsAawwnQUXt2LQOYlzZoYByqhonqoqfxZf4BLD97i4DukgXADCPgGgdOLTK5arYxZB1xnrc9T
EQFcHoZEAa1gSQioo/TPV5FZrDlxJA+NzwF+Ek1UonOzFnKZp6k5mgLBqSkuuAGXS4whJb5xz/xs
wXCHjiVerAk5eh9Kfz1wqOldtVv9dkbscfjgjKeTA8XPrtaNauX5rInOxaHuOReNtpFjo1/OxdFG
5eY9hJ3L3jqcPJbATggXAemDLZX0MNZRYjSDH7C1wMHQh73DyYfTu8a0F9v+6D8W6XNnF1GEIXW/
JrSKPOtnW1YFat9mrLJkzLbyIlTvYzV0RGXcaTBfVLx7jF2PJ2wyuBsydpm7VSVa4C4Zb6pFO2TR
huypCEPwuQjNftUrNl6GsYZzuFrrLdC9iJjQ3omAPBbcI2lsU77tUD43kw1NPZhTrnZWzuQKLomx
Rd4OXM1ByExVVkmoTwfBJ7Lt10Iq1Kgo23Bmd8Ib1KrGbsbO4Pp2yO4fpnf3s6MnZiwuiJuls1/L
Pu4yUCvhpA+vZaJvWWDTr0yFYYyVnHMqCEq+QniuYX225xmnzRENjbXACF3wkCYNVZ1mBwxoR9Iw
WAo3/36oSOTfgjwEEQKt15e9Xpqm52+oaXxszmnE9GLl65RH2OMmS6+u5acKxDmlPgj2eT5/gQOX
LLK0j1y0Uwbmn438VZkVpqlfNKa/YET/53j+99G8H8tUhr9ZSXs2
""")





##file activate.fish
ACTIVATE_FISH = convert("""
eJydVm1v4jgQ/s6vmA1wBxUE7X2stJVYlVWR2lK13d6d9laRk0yIr8HmbIe0++tvnIQQB9pbXT5A
Ys/LM55nZtyHx5RrSHiGsMm1gRAh1xhDwU0Kng8hFzMWGb5jBv2E69SDs0TJDdj3MxilxmzPZzP7
pVPMMl+q9bjXh1eZQ8SEkAZULoAbiLnCyGSvvV6SC7IoBcS4Nw0wjcFbvJDcjiuTswzFDpiIQaHJ
lQAjQUi1YRmUboC2uZJig8J4PaCnT5IaDcgsbm/CjinOwgx1KcUTMEhhTgV4g2B1fRk8Le8fv86v
g7v545UHpZB9rKnp+gXsMhxLunIIpwVQxP/l9c/Hq9Xt1epm4R27bva6AJqN92G4YhbMG2i+LB+u
grv71c3dY7B6WtzfLy9bePbp0taDTXSwJQJszUnnp0y57mvpPcrF7ZODyhswtd59+/jdgw+fwBNS
xLSscksUPIDqwwNmCez3PpxGeyBYg6HE0YdcWBxcKczYzuVJi5Wu915vn5oWePCCoPUZBN5B7IgV
MCi54ZDLG7TUZ0HweXkb3M5vFmSpFm/gthhBx0UrveoPpv9AJ9unIbQYdUoe21bKg2q48sPFGVwu
H+afrxd1qvclaNlRFyh1EQ2sSccEuNAGWQwysfVpz1tPajUqbqJUnEcIJkWo6OXDaodK8ZiLdbmM
L1wb+9H0D+pcyPSrX5u5kgWSygRYXCnJUi/KKcuU4cqsAyTKZBiissLc7NFwizvjxtieKBVCIdWz
fzilzPaYyljZN0cGN1v7NnaIPNCGmVy3GKuJaQ6iVjE1Qfm+36hglErwmnAD8hu0dDy4uICBA8ZV
pQr/q/+O0KFW2kjelu9Dgb9SDBsWV4F4x5CswgS0zBVlk5tDMP5bVtUGpslbm81Lu2sdKq7uNMGh
MVQ4fy9xhogC1lS5guhISa0DlBWv0O8odT6/LP+4WZzDV6FzIkEqC0uolGZSZoMnlpxplmD2euaT
O4hkTpPnbztDccey0bhjDaBIqaWQa0uwEtQEwtyU56i4fq54F9IE3ORR6mKriODM4XOYZwaVYLYz
7SPbKkz4i7VkB6/Ot1upDE3znNqYKpM8raa0Bx8vfvntJ32UENsM4aI6gJL+jJwhxhh3jVIDOcpi
m0r2hmEtS8XXXNBk71QCDXTBNhhPiHX2LtHkrVIlhoEshH/EZgdq53Eirqs5iFKMnkOmqZTtr3Xq
djvPTWZT4S3NT5aVLgurMPUWI07BRVYqkQrmtCKohNY8qu9EdACoT6ki0a66XxVF4f9AQ3W38yO5
mWmZmIIpnDFrbXakvKWeZhLwhvrbUH8fahhqD0YUcBDJjEBMQwiznE4y5QbHrbhHBOnUAYzb2tVN
jJa65e+eE2Ya30E2GurxUP8ssA6e/wOnvo3V78d3vTcvMB3n7l3iX1JXWqk=
""")





##file activate.csh
ACTIVATE_CSH = convert("""
eJx9U11vmzAUffevOCVRu+UB9pws29Kl0iq1aVWllaZlcgxciiViItsQdb9+xiQp+dh4QOB7Pu49
XHqY59IgkwVhVRmLmFAZSrGRNkdgykonhFiqSCRW1sJSmJg8wCDT5QrucRCyHn6WFRKhVGmhKwVp
kUpNiS3emup3TY6XIn7DVNQyJUwlrgthJD6n/iCNv72uhCzCpFx9CRkThRQGKe08cWXJ9db/yh/u
pvzl9mn+PLnjj5P5D1yM8QmXlzBkSdXwZ0H/BBc0mEo5FE5qI2jKhclHOOvy9HD/OO/6YO1mX9vx
sY0H/tPIV0dtqel0V7iZvWyNg8XFcBA0ToEqVeqOdNUEQFvN41SumAv32VtJrakQNSmLWmgp4oJM
yDoBHgoydtoEAs47r5wHHnUal5vbJ8oOI+9wI86vb2d8Nrm/4Xy4RZ8R85E4uTZPB5EZPnTaaAGu
E59J8BE2J8XgrkbLeXMlVoQxznEYFYY8uFFdxsKQRx90Giwx9vSueHP1YNaUSFG4vTaErNSYuBOF
lXiVyXa9Sy3JdClEyK1dD6Nos9mEf8iKlOpmqSNTZnYjNEWiUYn2pKNB3ttcLJ3HmYYXy6Un76f7
r8rRsC1TpTJj7f19m5sUf/V3Ir+x/yjtLu8KjLX/CmN/AcVGUUo=
""")





##file activate.bat
ACTIVATE_BAT = convert("""
eJyFUkEKgzAQvAfyhz0YaL9QEWpRqlSjWGspFPZQTevFHOr/adQaU1GaUzI7Mzu7ZF89XhKkEJS8
qxaKMMsvboQ+LxxE44VICSW1gEa2UFaibqoS0iyJ0xw2lIA6nX5AHCu1jpRsv5KRjknkac9VLVug
sX9mtzxIeJDE/mg4OGp47qoLo3NHX2jsMB3AiDht5hryAUOEifoTdCXbSh7V0My2NMq/Xbh5MEjU
ZT63gpgNT9lKOJ/CtHsvT99re3pX303kydn4HeyOeAg5cjf2EW1D6HOPkg9NGKhu
""")





##file deactivate.bat
DEACTIVATE_BAT = convert("""
eJxzSE3OyFfIT0vj4spMU0hJTcvMS01RiPf3cYkP8wwKCXX0iQ8I8vcNCFHQ4FIAguLUEgWIgK0q
FlWqXJpcICVYpGzx2BAZ4uHv5+Hv6wq1BWINXBTdKriEKkI1DhW2QAfhttcxxANiFZCBbglQSJUL
i2dASrm4rFz9XLgAwJNbyQ==
""")





##file distutils-init.py
DISTUTILS_INIT = convert("""
eJytV92L4zYQf/dfMU0ottuse7RvC6FQrg8Lxz2Ugz4si9HacqKuIxlJ2ST313dG8odkO9d7aGBB
luZLv/nNjFacOqUtKJMIvzK3cXlhWgp5MDBsqK5SNYftsBAGpLLA4F1oe2Ytl+9wUvW55TswCi4c
KibhbFDSglXQCFmDPXIwtm7FawLRbwtPzg2T9gf4gupKv4GS0N262w7V0NvpbCy8cvTo3eAus6C5
ETU3ICQZX1hFTw/dzR6V/AW1RCN4/XAtbsVXqIXmlVX6liS4lOzEYY9QFB2zx6LfoSNjz1a0pqT9
QOIfJWQ2E888NEVZNqLlZZnvIB0NpHkimlFdKn2iRRY7yGG/CCJb6Iz280d34SFXBS2yEYPNF0Q7
yM7oCjpWvbEDQmnhRwOs6zjThpKE8HogwRAgraqYFZgGZvzmzVh+mgz9vskT3hruwyjdFcqyENJw
bbMPO5jdzonxK68QKT7B57CMRRG5shRSWDTX3dI8LzRndZbnSWL1zfvriUmK4TcGWSnZiEPCrxXv
bM+sP7VW2is2WgWXCO3sAu3Rzysz3FiNCA8WPyM4gb1JAAmCiyTZbhFjWx3h9SzauuRXC9MFoVbc
yNTCm1QXOOIfIn/g1kGMhDUBN72hI5XCBQtIXQw8UEEdma6Jaz4vJIJ51Orc15hzzmu6TdFp3ogr
Aof0c98tsw1SiaiWotHffk3XYCkqdToxWRfTFXqgpg2khcLluOHMVC0zZhLKIomesfSreUNNgbXi
Ky9VRzwzkBneNoGQyyvGjbsFQqOZvpWIjqH281lJ/jireFgR3cPzSyTGWzQpDNIU+03Fs4XKLkhp
/n0uFnuF6VphB44b3uWRneSbBoMSioqE8oeF0JY+qTvYfEK+bPLYdoR4McfYQ7wMZj39q0kfP8q+
FfsymO0GzNlPh644Jje06ulqHpOEQqdJUfoidI2O4CWx4qOglLye6RrFQirpCRXvhoRqXH3sYdVJ
AItvc+VUsLO2v2hVAWrNIfVGtkG351cUMNncbh/WdowtSPtCdkzYFv6mwYc9o2Jt68ud6wectBr8
hYAulPSlgzH44YbV3ikjrulEaNJxt+/H3wZ7bXSXje/YY4tfVVrVmUstaDwwOBLMg6iduDB0lMVC
UyzYx7Ab4kjCqdViEJmDcdk/SKbgsjYXgfMznUWcrtS4z4fmJ/XOM1LPk/iIpqass5XwNbdnLb1Y
8h3ERXSWZI6rZJxKs1LBqVH65w0Oy4ra0CBYxEeuOMbDmV5GI6E0Ha/wgVTtkX0+OXvqsD02CKLf
XHbeft85D7tTCMYy2Njp4DJP7gWJr6paVWXZ1+/6YXLv/iE0M90FktiI7yFJD9e7SOLhEkkaMTUO
azq9i2woBNR0/0eoF1HFMf0H8ChxH/jgcB34GZIz3Qn4/vid+VEamQrOVqAPTrOfmD4MPdVh09tb
8dLLjvh/61lEP4yW5vJaH4vHcevG8agXvzPGoOhhXNncpTr99PTHx6e/UvffFLaxUSjuSeP286Dw
gtEMcW1xKr/he4/6IQ6FUXP+0gkioHY5iwC9Eyx3HKO7af0zPPe+XyLn7fAY78k4aiR387bCr5XT
5C4rFgwLGfMvJuAMew==
""")





##file distutils.cfg
DISTUTILS_CFG = convert("""
eJxNj00KwkAMhfc9xYNuxe4Ft57AjYiUtDO1wXSmNJnK3N5pdSEEAu8nH6lxHVlRhtDHMPATA4uH
xJ4EFmGbvfJiicSHFRzUSISMY6hq3GLCRLnIvSTnEefN0FIjw5tF0Hkk9Q5dRunBsVoyFi24aaLg
9FDOlL0FPGluf4QjcInLlxd6f6rqkgPu/5nHLg0cXCscXoozRrP51DRT3j9QNl99AP53T2Q=
""")





##file activate_this.py
ACTIVATE_THIS = convert("""
eJyNUlGL2zAMfvevEBlHEujSsXsL9GGDvW1jD3sZpQQ3Ua7aJXawnbT595Ocpe0dO5ghseVP+vRJ
VpIkn2cYPZknwAvWLXWYhRP5Sk4baKgOWRWNqtpdgTyH2Y5wpq5Tug406YAgKEzkwqg7NBPwR86a
Hk0olPopaK0NHJHzYQPnE5rI0o8+yBUwiBfyQcT8mMPJGiAT0A0O+b8BY4MKJ7zPcSSzHaKrSpJE
qeDmUgGvVbPCS41DgO+6xy/OWbfAThMn/OQ9ukDWRCSLiKzk1yrLjWapq6NnvHUoHXQ4bYPdrsVX
4lQMc/q6ZW975nmSK+oH6wL42a9H65U6aha342Mh0UVDzrD87C1bH73s16R5zsStkBZDp0NrXQ+7
HaRnMo8f06UBnljKoOtn/YT+LtdvSyaT/BtIv9KR60nF9f3qmuYKO4//T9ItJMsjPfgUHqKwCZ3n
xu/Lx8M/UvCLTxW7VULHxB1PRRbrYfvWNY5S8it008jOjcleaMqVBDnUXcWULV2YK9JEQ92OfC96
1Tv4ZicZZZ7GpuEpZbbeQ7DxquVx5hdqoyFSSmXwfC90f1Dc7hjFs/tK99I0fpkI8zSLy4tSy+sI
3vMWehjQNJmE5VePlZbL61nzX3S93ZcfDqznnkb9AZ3GWJU=
""")





if __name__ == '__main__':
    main()

## TODO:
## Copy python.exe.manifest
## Monkeypatch distutils.sysconfig
