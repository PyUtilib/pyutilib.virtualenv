#!/usr/bin/env python
## WARNING: This file is generated
#!/usr/bin/env python
"""Create a "virtual" Python installation
"""

# If you change the version here, change it in setup.py
# and docs/conf.py as well.
virtualenv_version = "1.7.1.2"

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
from distutils.util import strtobool

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

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

join = os.path.join
py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])

is_jython = sys.platform.startswith('java')
is_pypy = hasattr(sys, 'pypy_version_info')
is_win  = (sys.platform == 'win32')
abiflags = getattr(sys, 'abiflags', '')

user_dir = os.path.expanduser('~')
if sys.platform == 'win32':
    user_dir = os.environ.get('APPDATA', user_dir)  # Use %APPDATA% for roaming
    default_storage_dir = os.path.join(user_dir, 'virtualenv')
else:
    default_storage_dir = os.path.join(user_dir, '.virtualenv')
default_config_file = os.path.join(default_storage_dir, 'virtualenv.ini')

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
            "_dummy_thread",
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
        >>> l = Logger([])
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
            if stop is not None and stop <= consumer_level:
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
    if symlink and hasattr(os, 'symlink') and not is_win:
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
    for dir in reversed(dirs):
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
        source = 'distribute-0.6.24.tar.gz'
        project_name = 'distribute'
        bootstrap_script = DISTRIBUTE_SETUP_PY

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
    cmd = [join(os.path.dirname(py_executable), easy_install_script), filename]
    if sys.platform == 'win32':
        cmd.insert(0, py_executable)
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


class UpdatingDefaultsHelpFormatter(optparse.IndentedHelpFormatter):
    """
    Custom help formatter for use in ConfigOptionParser that updates
    the defaults before expanding them, allowing them to show up correctly
    in the help listing
    """
    def expand_default(self, option):
        if self.parser is not None:
            self.parser.update_defaults(self.parser.defaults)
        return optparse.IndentedHelpFormatter.expand_default(self, option)


class ConfigOptionParser(optparse.OptionParser):
    """
    Custom option parser which updates its defaults by by checking the
    configuration files and environmental variables
    """
    def __init__(self, *args, **kwargs):
        self.config = ConfigParser.RawConfigParser()
        self.files = self.get_config_files()
        self.config.read(self.files)
        optparse.OptionParser.__init__(self, *args, **kwargs)

    def get_config_files(self):
        config_file = os.environ.get('VIRTUALENV_CONFIG_FILE', False)
        if config_file and os.path.exists(config_file):
            return [config_file]
        return [default_config_file]

    def update_defaults(self, defaults):
        """
        Updates the given defaults with values from the config files and
        the environ. Does a little special handling for certain types of
        options (lists).
        """
        # Then go and look for the other sources of configuration:
        config = {}
        # 1. config files
        config.update(dict(self.get_config_section('virtualenv')))
        # 2. environmental variables
        config.update(dict(self.get_environ_vars()))
        # Then set the options with those values
        for key, val in config.items():
            key = key.replace('_', '-')
            if not key.startswith('--'):
                key = '--%s' % key  # only prefer long opts
            option = self.get_option(key)
            if option is not None:
                # ignore empty values
                if not val:
                    continue
                # handle multiline configs
                if option.action == 'append':
                    val = val.split()
                else:
                    option.nargs = 1
                if option.action in ('store_true', 'store_false', 'count'):
                    val = strtobool(val)
                try:
                    val = option.convert_value(key, val)
                except optparse.OptionValueError:
                    e = sys.exc_info()[1]
                    print("An error occured during configuration: %s" % e)
                    sys.exit(3)
                defaults[option.dest] = val
        return defaults

    def get_config_section(self, name):
        """
        Get a section of a configuration
        """
        if self.config.has_section(name):
            return self.config.items(name)
        return []

    def get_environ_vars(self, prefix='VIRTUALENV_'):
        """
        Returns a generator with all environmental vars with prefix VIRTUALENV
        """
        for key, val in os.environ.items():
            if key.startswith(prefix):
                yield (key.replace(prefix, '').lower(), val)

    def get_default_values(self):
        """
        Overridding to make updating the defaults after instantiation of
        the option parser possible, update_defaults() does the dirty work.
        """
        if not self.process_default_values:
            # Old, pre-Optik 1.5 behaviour.
            return optparse.Values(self.defaults)

        defaults = self.update_defaults(self.defaults.copy()) # ours
        for option in self._get_all_options():
            default = defaults.get(option.dest)
            if isinstance(default, basestring):
                opt_str = option.get_opt_string()
                defaults[option.dest] = option.check_value(opt_str, default)
        return optparse.Values(defaults)


def main():
    parser = ConfigOptionParser(
        version=virtualenv_version,
        usage="%prog [OPTIONS] DEST_DIR",
        formatter=UpdatingDefaultsHelpFormatter())

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
        '--system-site-packages',
        dest='system_site_packages',
        action='store_true',
        help="Give access to the global site-packages dir to the "
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
        'VIRTUALENV_DISTRIBUTE to make it the default ')

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

    # Force --distribute on Python 3, since setuptools is not available.
    if majver > 2:
        options.use_distribute = True

    if os.environ.get('PYTHONDONTWRITEBYTECODE') and not options.use_distribute:
        print(
            "The PYTHONDONTWRITEBYTECODE environment variable is "
            "not compatible with setuptools. Either use --distribute "
            "or unset PYTHONDONTWRITEBYTECODE.")
        sys.exit(2)
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

    if options.no_site_packages:
        logger.warn('The --no-site-packages flag is deprecated; it is now '
                    'the default behavior.')

    create_environment(home_dir,
                       site_packages=options.system_site_packages,
                       clear=options.clear,
                       unzip_setuptools=options.unzip_setuptools,
                       use_distribute=options.use_distribute,
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
        if hasattr(part, 'decode'):
            try:
                part = part.decode(sys.getdefaultencoding())
            except UnicodeDecodeError:
                part = part.decode(sys.getfilesystemencoding())
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
        fs_encoding = sys.getfilesystemencoding()
        while 1:
            line = stdout.readline()
            try:
                line = line.decode(encoding)
            except UnicodeDecodeError:
                line = line.decode(fs_encoding)
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


def create_environment(home_dir, site_packages=False, clear=False,
                       unzip_setuptools=False, use_distribute=False,
                       prompt=None, search_dirs=None, never_download=False):
    """
    Creates a new environment in ``home_dir``.

    If ``site_packages`` is true, then the global ``site-packages/``
    directory will be on the path.

    If ``clear`` is true (default False) then the environment will
    first be cleared.
    """
    home_dir, lib_dir, inc_dir, bin_dir = path_locations(home_dir)

    py_executable = os.path.abspath(install_python(
        home_dir, lib_dir, inc_dir, bin_dir,
        site_packages=site_packages, clear=clear))

    install_distutils(home_dir)

    # use_distribute also is True if VIRTUALENV_DISTRIBUTE env var is set
    # we also check VIRTUALENV_USE_DISTRIBUTE for backwards compatibility
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
    # If we are running under -p, we need to remove the current
    # directory from sys.path temporarily here, so that we
    # definitely get the modules from the site directory of
    # the interpreter we are running under, not the one
    # virtualenv.py is installed under (which might lead to py2/py3
    # incompatibility issues)
    _prev_sys_path = sys.path
    if os.environ.get('VIRTUALENV_INTERPRETER_RUNNING'):
        sys.path = sys.path[1:]
    try:
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
    finally:
        sys.path = _prev_sys_path

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

    if is_pypy or is_win:
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
    pcbuild_dir = os.path.dirname(sys.executable)
    pyd_pth = os.path.join(lib_dir, 'site-packages', 'virtualenv_builddir_pyd.pth')
    if is_win and os.path.exists(os.path.join(pcbuild_dir, 'build.bat')):
        logger.notify('Detected python running from build directory %s', pcbuild_dir)
        logger.notify('Writing .pth file linking to build directory for *.pyd files')
        writefile(pyd_pth, pcbuild_dir)
    else:
        pcbuild_dir = None
        if os.path.exists(pyd_pth):
            logger.info('Deleting %s (not Windows env or not build directory python)' % pyd_pth)
            os.unlink(pyd_pth)
        
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
            python_d = os.path.join(os.path.dirname(sys.executable), 'python_d.exe')
            python_d_dest = os.path.join(os.path.dirname(py_executable), 'python_d.exe')
            if os.path.exists(python_d):
                logger.info('Also created python_d.exe')
                shutil.copyfile(python_d, python_d_dest)
            elif os.path.exists(python_d_dest):
                logger.info('Removed python_d.exe as it is no longer at the source')
                os.unlink(python_d_dest)
            # we need to copy the DLL to enforce that windows will load the correct one.
            # may not exist if we are cygwin.
            py_executable_dll = 'python%s%s.dll' % (
                sys.version_info[0], sys.version_info[1])
            py_executable_dll_d = 'python%s%s_d.dll' % (
                sys.version_info[0], sys.version_info[1])
            pythondll = os.path.join(os.path.dirname(sys.executable), py_executable_dll)
            pythondll_d = os.path.join(os.path.dirname(sys.executable), py_executable_dll_d)
            pythondll_d_dest = os.path.join(os.path.dirname(py_executable), py_executable_dll_d)
            if os.path.exists(pythondll):
                logger.info('Also created %s' % py_executable_dll)
                shutil.copyfile(pythondll, os.path.join(os.path.dirname(py_executable), py_executable_dll))
            if os.path.exists(pythondll_d):
                logger.info('Also created %s' % py_executable_dll_d)
                shutil.copyfile(pythondll_d, pythondll_d_dest)
            elif os.path.exists(pythondll_d_dest):
                logger.info('Removed %s as the source does not exist' % pythondll_d_dest)
                os.unlink(pythondll_d_dest)
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

    if '.framework' in prefix:
        if 'Python.framework' in prefix:
            logger.debug('MacOSX Python framework detected')
            # Make sure we use the the embedded interpreter inside
            # the framework, even if sys.executable points to
            # the stub executable in ${sys.prefix}/bin
            # See http://groups.google.com/group/python-virtualenv/
            #                              browse_thread/thread/17cab2f85da75951
            original_python = os.path.join(
                prefix, 'Resources/Python.app/Contents/MacOS/Python')
        if 'EPD' in prefix:
            logger.debug('EPD framework detected')
            original_python = os.path.join(prefix, 'bin/python')
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
    cmd = [py_executable, '-c', """
import sys
prefix = sys.prefix
if sys.version_info[0] == 3:
    prefix = prefix.encode('utf8')
if hasattr(sys.stdout, 'detach'):
    sys.stdout = sys.stdout.detach()
elif hasattr(sys.stdout, 'buffer'):
    sys.stdout = sys.stdout.buffer
sys.stdout.write(prefix)
"""]
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

    proc_stdout = proc_stdout.strip().decode("utf-8")
    proc_stdout = os.path.normcase(os.path.abspath(proc_stdout))
    norm_home_dir = os.path.normcase(os.path.abspath(home_dir))
    if hasattr(norm_home_dir, 'decode'):
        norm_home_dir = norm_home_dir.decode(sys.getfilesystemencoding())
    if proc_stdout != norm_home_dir:
        logger.fatal(
            'ERROR: The executable %s is not functioning' % py_executable)
        logger.fatal(
            'ERROR: It thinks sys.prefix is %r (should be %r)'
            % (proc_stdout, norm_home_dir))
        logger.fatal(
            'ERROR: virtualenv is not compatible with this system or executable')
        if sys.platform == 'win32':
            logger.fatal(
                'Note: some Windows users have reported this error when they '
                'installed Python for "Only this user" or have multiple '
                'versions of Python installed. Copying the appropriate '
                'PythonXX.dll to the virtualenv Scripts/ directory may fix '
                'this problem.')
        sys.exit(100)
    else:
        logger.info('Got sys.prefix result: %r' % proc_stdout)

    pydistutils = os.path.expanduser('~/.pydistutils.cfg')
    if os.path.exists(pydistutils):
        logger.notify('Please make sure you remove any previous custom paths from '
                      'your %s file.' % pydistutils)
    ## FIXME: really this should be calculated earlier

    fix_local_scheme(home_dir)

    return py_executable

def install_activate(home_dir, bin_dir, prompt=None):
    home_dir = os.path.abspath(home_dir)
    if sys.platform == 'win32' or is_jython and os._name == 'nt':
        files = {
            'activate.bat': ACTIVATE_BAT,
            'deactivate.bat': DEACTIVATE_BAT,
            'activate.ps1': ACTIVATE_PS,
        }

        # MSYS needs paths of the form /c/path/to/file
        drive, tail = os.path.splitdrive(home_dir.replace(os.sep, '/'))
        home_dir_msys = (drive and "/%s%s" or "%s%s") % (drive[:1], tail)

        # Run-time conditional enables (basic) Cygwin compatibility
        home_dir_sh = ("""$(if [ "$OSTYPE" "==" "cygwin" ]; then cygpath -u '%s'; else echo '%s'; fi;)""" % 
                       (home_dir, home_dir_msys))
        files['activate'] = ACTIVATE_SH.replace('__VIRTUAL_ENV__', home_dir_sh)

    else:
        files = {'activate': ACTIVATE_SH}

        # suppling activate.fish in addition to, not instead of, the
        # bash script support.
        files['activate.fish'] = ACTIVATE_FISH

        # same for csh/tcsh support...
        files['activate.csh'] = ACTIVATE_CSH

    files['activate_this.py'] = ACTIVATE_THIS
    if hasattr(home_dir, 'decode'):
        home_dir = home_dir.decode(sys.getfilesystemencoding())
    vname = os.path.basename(home_dir)
    for name, content in files.items():
        content = content.replace('__VIRTUAL_PROMPT__', prompt or '')
        content = content.replace('__VIRTUAL_WINPROMPT__', prompt or '(%s)' % vname)
        content = content.replace('__VIRTUAL_ENV__', home_dir)
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

def fix_local_scheme(home_dir):
    """
    Platforms that use the "posix_local" install scheme (like Ubuntu with
    Python 2.7) need to be given an additional "local" location, sigh.
    """
    try:
        import sysconfig
    except ImportError:
        pass
    else:
        if sysconfig._get_default_scheme() == 'posix_local':
            local_path = os.path.join(home_dir, 'local')
            if not os.path.exists(local_path):
                os.mkdir(local_path)
                for subdir_name in os.listdir(home_dir):
                    if subdir_name == 'local':
                        continue
                    os.symlink(os.path.abspath(os.path.join(home_dir, subdir_name)), \
                                                            os.path.join(local_path, subdir_name))

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
    activate = "import os; activate_this=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'activate_this.py'); execfile(activate_this, dict(__file__=activate_this)); del os, activate_this"
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
        try:
            try:
                lines = f.read().decode('utf-8').splitlines()
            except UnicodeDecodeError:
                # This is probably a binary program instead
                # of a script, so just ignore it.
                continue
        finally:
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
        f.write('\n'.join(lines).encode('utf-8'))
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

__all__ = ['_OrderedDict', 'Sequence_OrderedDict']

import sys
INTP_VER = sys.version_info[:2]
if INTP_VER < (2, 2):
    raise RuntimeError("Python v.2.2 or later required")

import types, warnings

class _OrderedDict(dict):
    """
    A class of dictionary that keeps the insertion order of keys.

    All appropriate methods return keys, items, or values in an ordered way.

    All normal dictionary methods are available. Update and comparison is
    restricted to other _OrderedDict objects.

    Various sequence methods are available, including the ability to explicitly
    mutate the key ordering.

    __contains__ tests:

    >>> d = _OrderedDict(((1, 3),))
    >>> 1 in d
    1
    >>> 4 in d
    0

    __getitem__ tests:

    >>> _OrderedDict(((1, 3), (3, 2), (2, 1)))[2]
    1
    >>> _OrderedDict(((1, 3), (3, 2), (2, 1)))[4]
    Traceback (most recent call last):
    KeyError: 4

    __len__ tests:

    >>> len(_OrderedDict())
    0
    >>> len(_OrderedDict(((1, 3), (3, 2), (2, 1))))
    3

    get tests:

    >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
    >>> d.get(1)
    3
    >>> d.get(4) is None
    1
    >>> d.get(4, 5)
    5
    >>> d
    _OrderedDict([(1, 3), (3, 2), (2, 1)])

    has_key tests:

    >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
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
        default) then when doing slice assignment - the ``_OrderedDict`` you are
        assigning from *must not* contain any keys in the remaining dict.

        >>> _OrderedDict()
        _OrderedDict([])
        >>> _OrderedDict({1: 1})
        Traceback (most recent call last):
        TypeError: undefined order, cannot get items from dict
        >>> _OrderedDict({1: 1}.items())
        _OrderedDict([(1, 1)])
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d
        _OrderedDict([(1, 3), (3, 2), (2, 1)])
        >>> _OrderedDict(d)
        _OrderedDict([(1, 3), (3, 2), (2, 1)])
        """
        self.strict = strict
        dict.__init__(self)
        if isinstance(init_val, _OrderedDict):
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
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> del d[3]
        >>> d
        _OrderedDict([(1, 3), (2, 1)])
        >>> del d[3]
        Traceback (most recent call last):
        KeyError: 3
        >>> d[3] = 2
        >>> d
        _OrderedDict([(1, 3), (2, 1), (3, 2)])
        >>> del d[0:1]
        >>> d
        _OrderedDict([(2, 1), (3, 2)])
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
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d == _OrderedDict(d)
        True
        >>> d == _OrderedDict(((1, 3), (2, 1), (3, 2)))
        False
        >>> d == _OrderedDict(((1, 0), (3, 2), (2, 1)))
        False
        >>> d == _OrderedDict(((0, 3), (3, 2), (2, 1)))
        False
        >>> d == dict(d)
        False
        >>> d == False
        False
        """
        if isinstance(other, _OrderedDict):
            # NOTE: efficiency?
            #   Generate both item lists for each compare
            return (self.items() == other.items())
        else:
            return False

    def __lt__(self, other):
        """
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = _OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> c < d
        True
        >>> d < c
        False
        >>> d < dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other _OrderedDicts
        """
        if not isinstance(other, _OrderedDict):
            raise TypeError('Can only compare with other _OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() < other.items())

    def __le__(self, other):
        """
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = _OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> e = _OrderedDict(d)
        >>> c <= d
        True
        >>> d <= c
        False
        >>> d <= dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other _OrderedDicts
        >>> d <= e
        True
        """
        if not isinstance(other, _OrderedDict):
            raise TypeError('Can only compare with other _OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() <= other.items())

    def __ne__(self, other):
        """
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d != _OrderedDict(d)
        False
        >>> d != _OrderedDict(((1, 3), (2, 1), (3, 2)))
        True
        >>> d != _OrderedDict(((1, 0), (3, 2), (2, 1)))
        True
        >>> d == _OrderedDict(((0, 3), (3, 2), (2, 1)))
        False
        >>> d != dict(d)
        True
        >>> d != False
        True
        """
        if isinstance(other, _OrderedDict):
            # NOTE: efficiency?
            #   Generate both item lists for each compare
            return not (self.items() == other.items())
        else:
            return True

    def __gt__(self, other):
        """
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = _OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> d > c
        True
        >>> c > d
        False
        >>> d > dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other _OrderedDicts
        """
        if not isinstance(other, _OrderedDict):
            raise TypeError('Can only compare with other _OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() > other.items())

    def __ge__(self, other):
        """
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> c = _OrderedDict(((0, 3), (3, 2), (2, 1)))
        >>> e = _OrderedDict(d)
        >>> c >= d
        False
        >>> d >= c
        True
        >>> d >= dict(c)
        Traceback (most recent call last):
        TypeError: Can only compare with other _OrderedDicts
        >>> e >= d
        True
        """
        if not isinstance(other, _OrderedDict):
            raise TypeError('Can only compare with other _OrderedDicts')
        # NOTE: efficiency?
        #   Generate both item lists for each compare
        return (self.items() >= other.items())

    def __repr__(self):
        """
        Used for __repr__ and __str__

        >>> r1 = repr(_OrderedDict((('a', 'b'), ('c', 'd'), ('e', 'f'))))
        >>> r1
        "_OrderedDict([('a', 'b'), ('c', 'd'), ('e', 'f')])"
        >>> r2 = repr(_OrderedDict((('a', 'b'), ('e', 'f'), ('c', 'd'))))
        >>> r2
        "_OrderedDict([('a', 'b'), ('e', 'f'), ('c', 'd')])"
        >>> r1 == str(_OrderedDict((('a', 'b'), ('c', 'd'), ('e', 'f'))))
        True
        >>> r2 == str(_OrderedDict((('a', 'b'), ('e', 'f'), ('c', 'd'))))
        True
        """
        return '%s([%s])' % (self.__class__.__name__, ', '.join(
            ['(%r, %r)' % (key, self[key]) for key in self._sequence]))

    def __setitem__(self, key, val):
        """
        Allows slice assignment, so long as the slice is an _OrderedDict
        >>> d = _OrderedDict()
        >>> d['a'] = 'b'
        >>> d['b'] = 'a'
        >>> d[3] = 12
        >>> d
        _OrderedDict([('a', 'b'), ('b', 'a'), (3, 12)])
        >>> d[:] = _OrderedDict(((1, 2), (2, 3), (3, 4)))
        >>> d
        _OrderedDict([(1, 2), (2, 3), (3, 4)])
        >>> d[::2] = _OrderedDict(((7, 8), (9, 10)))
        >>> d
        _OrderedDict([(7, 8), (2, 3), (9, 10)])
        >>> d = _OrderedDict(((0, 1), (1, 2), (2, 3), (3, 4)))
        >>> d[1:3] = _OrderedDict(((1, 2), (5, 6), (7, 8)))
        >>> d
        _OrderedDict([(0, 1), (1, 2), (5, 6), (7, 8), (3, 4)])
        >>> d = _OrderedDict(((0, 1), (1, 2), (2, 3), (3, 4)), strict=True)
        >>> d[1:3] = _OrderedDict(((1, 2), (5, 6), (7, 8)))
        >>> d
        _OrderedDict([(0, 1), (1, 2), (5, 6), (7, 8), (3, 4)])

        >>> a = _OrderedDict(((0, 1), (1, 2), (2, 3)), strict=True)
        >>> a[3] = 4
        >>> a
        _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[::1] = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[:2] = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])
        Traceback (most recent call last):
        ValueError: slice assignment must be from unique keys
        >>> a = _OrderedDict(((0, 1), (1, 2), (2, 3)))
        >>> a[3] = 4
        >>> a
        _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[::1] = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[:2] = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a[::-1] = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> a
        _OrderedDict([(3, 4), (2, 3), (1, 2), (0, 1)])

        >>> d = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> d[:1] = 3
        Traceback (most recent call last):
        TypeError: slice assignment requires an _OrderedDict

        >>> d = _OrderedDict([(0, 1), (1, 2), (2, 3), (3, 4)])
        >>> d[:1] = _OrderedDict([(9, 8)])
        >>> d
        _OrderedDict([(9, 8), (1, 2), (2, 3), (3, 4)])
        """
        if isinstance(key, types.SliceType):
            if not isinstance(val, _OrderedDict):
                # NOTE: allow a list of tuples?
                raise TypeError('slice assignment requires an _OrderedDict')
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
        Allows slicing. Returns an _OrderedDict if you slice.
        >>> b = _OrderedDict([(7, 0), (6, 1), (5, 2), (4, 3), (3, 4), (2, 5), (1, 6)])
        >>> b[::-1]
        _OrderedDict([(1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)])
        >>> b[2:5]
        _OrderedDict([(5, 2), (4, 3), (3, 4)])
        >>> type(b[2:4])
        <class '__main__._OrderedDict'>
        """
        if isinstance(key, types.SliceType):
            # NOTE: does this raise the error we want?
            keys = self._sequence[key]
            # NOTE: efficiency?
            return _OrderedDict([(entry, self[entry]) for entry in keys])
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

        >>> d = _OrderedDict()
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
            raise AttributeError("_OrderedDict has no '%s' attribute" % name)

    def __deepcopy__(self, memo):
        """
        To allow deepcopy to work with _OrderedDict.

        >>> from copy import deepcopy
        >>> a = _OrderedDict([(1, 1), (2, 2), (3, 3)])
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
        >>> _OrderedDict(((1, 3), (3, 2), (2, 1))).copy()
        _OrderedDict([(1, 3), (3, 2), (2, 1)])
        """
        return _OrderedDict(self)

    def items(self):
        """
        ``items`` returns a list of tuples representing all the
        ``(key, value)`` pairs in the dictionary.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.items()
        [(1, 3), (3, 2), (2, 1)]
        >>> d.clear()
        >>> d.items()
        []
        """
        return zip(self._sequence, self.values())

    def keys(self):
        """
        Return a list of keys in the ``_OrderedDict``.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.keys()
        [1, 3, 2]
        """
        return self._sequence[:]

    def values(self, values=None):
        """
        Return a list of all the values in the _OrderedDict.

        Optionally you can pass in a list of values, which will replace the
        current list. The value list must be the same len as the _OrderedDict.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.values()
        [3, 2, 1]
        """
        return [self[key] for key in self._sequence]

    def iteritems(self):
        """
        >>> ii = _OrderedDict(((1, 3), (3, 2), (2, 1))).iteritems()
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
        >>> ii = _OrderedDict(((1, 3), (3, 2), (2, 1))).iterkeys()
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
        >>> iv = _OrderedDict(((1, 3), (3, 2), (2, 1))).itervalues()
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
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.clear()
        >>> d
        _OrderedDict([])
        """
        dict.clear(self)
        self._sequence = []

    def pop(self, key, *args):
        """
        No dict.pop in Python 2.2, gotta reimplement it

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.pop(3)
        2
        >>> d
        _OrderedDict([(1, 3), (2, 1)])
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
            raise TypeError('pop expected at most 2 arguments, got %s' %
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

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.popitem()
        (2, 1)
        >>> d
        _OrderedDict([(1, 3), (3, 2)])
        >>> d.popitem(0)
        (1, 3)
        >>> _OrderedDict().popitem()
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
        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.setdefault(1)
        3
        >>> d.setdefault(4) is None
        True
        >>> d
        _OrderedDict([(1, 3), (3, 2), (2, 1), (4, None)])
        >>> d.setdefault(5, 0)
        0
        >>> d
        _OrderedDict([(1, 3), (3, 2), (2, 1), (4, None), (5, 0)])
        """
        if key in self:
            return self[key]
        else:
            self[key] = defval
            return defval

    def update(self, from_od):
        """
        Update from another _OrderedDict or sequence of (key, value) pairs

        >>> d = _OrderedDict(((1, 0), (0, 1)))
        >>> d.update(_OrderedDict(((1, 3), (3, 2), (2, 1))))
        >>> d
        _OrderedDict([(1, 3), (0, 1), (3, 2), (2, 1)])
        >>> d.update({4: 4})
        Traceback (most recent call last):
        TypeError: undefined order, cannot get items from dict
        >>> d.update((4, 4))
        Traceback (most recent call last):
        TypeError: cannot convert dictionary update sequence element "4" to a 2-item sequence
        """
        if isinstance(from_od, _OrderedDict):
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

        >>> od = _OrderedDict()
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

        >>> d = _OrderedDict()
        >>> d.setitems(((3, 1), (2, 3), (1, 2)))
        >>> d
        _OrderedDict([(3, 1), (2, 3), (1, 2)])
        """
        self.clear()
        # NOTE: this allows you to pass in an _OrderedDict as well :-)
        self.update(items)

    def setkeys(self, keys):
        """
        ``setkeys`` all ows you to pass in a new list of keys which will
        replace the current set. This must contain the same set of keys, but
        need not be in the same order.

        If you pass in new keys that don't match, a ``KeyError`` will be
        raised.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.keys()
        [1, 3, 2]
        >>> d.setkeys((1, 2, 3))
        >>> d
        _OrderedDict([(1, 3), (2, 1), (3, 2)])
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
        current list. The value list must be the same len as the _OrderedDict.

        (Or a ``ValueError`` is raised.)

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.setvalues((1, 2, 3))
        >>> d
        _OrderedDict([(1, 1), (3, 2), (2, 3)])
        >>> d.setvalues([6])
        Traceback (most recent call last):
        ValueError: Value list is not the same length as the _OrderedDict.
        """
        if len(values) != len(self):
            # NOTE: correct error to raise?
            raise ValueError('Value list is not the same length as the '
                '_OrderedDict.')
        self.update(zip(self, values))

### Sequence Methods ###

    def index(self, key):
        """
        Return the position of the specified key in the _OrderedDict.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
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
        the _OrderedDict.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.insert(0, 4, 0)
        >>> d
        _OrderedDict([(4, 0), (1, 3), (3, 2), (2, 1)])
        >>> d.insert(0, 2, 1)
        >>> d
        _OrderedDict([(2, 1), (4, 0), (1, 3), (3, 2)])
        >>> d.insert(8, 8, 1)
        >>> d
        _OrderedDict([(2, 1), (4, 0), (1, 3), (3, 2), (8, 1)])
        """
        if key in self:
            # NOTE: efficiency?
            del self[key]
        self._sequence.insert(index, key)
        dict.__setitem__(self, key, value)

    def reverse(self):
        """
        Reverse the order of the _OrderedDict.

        >>> d = _OrderedDict(((1, 3), (3, 2), (2, 1)))
        >>> d.reverse()
        >>> d
        _OrderedDict([(2, 1), (3, 2), (1, 3)])
        """
        self._sequence.reverse()

    def sort(self, *args, **kwargs):
        """
        Sort the key order in the _OrderedDict.

        This method takes the same arguments as the ``list.sort`` method on
        your version of Python.

        >>> d = _OrderedDict(((4, 1), (2, 2), (3, 3), (1, 4)))
        >>> d.sort()
        >>> d
        _OrderedDict([(1, 4), (2, 2), (3, 3), (4, 1)])
        """
        self._sequence.sort(*args, **kwargs)

class Keys(object):
    # NOTE: should this object be a subclass of list?
    """
    Custom object for accessing the keys of an _OrderedDict.

    Can be called like the normal ``_OrderedDict.keys`` method, but also
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
    Custom object for accessing the items of an _OrderedDict.

    Can be called like the normal ``_OrderedDict.items`` method, but also
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
            # fetching a slice returns an _OrderedDict
            return self._main[index].items()
        key = self._main._sequence[index]
        return (key, self._main[key])

    def __setitem__(self, index, item):
        """Set item at position i to item."""
        if isinstance(index, types.SliceType):
            # NOTE: item must be an iterable (list of tuples)
            self._main[index] = _OrderedDict(item)
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
    Custom object for accessing the values of an _OrderedDict.

    Can be called like the normal ``_OrderedDict.values`` method, but also
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

class Sequence_OrderedDict(_OrderedDict):
    """
    Experimental version of _OrderedDict that has a custom object for ``keys``,
    ``values``, and ``items``.

    These are callable sequence objects that work as methods, or can be
    manipulated directly as sequences.

    Test for ``keys``, ``items`` and ``values``.

    >>> d = Sequence_OrderedDict(((1, 2), (2, 3), (3, 4)))
    >>> d
    Sequence_OrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.keys
    [1, 2, 3]
    >>> d.keys()
    [1, 2, 3]
    >>> d.setkeys((3, 2, 1))
    >>> d
    Sequence_OrderedDict([(3, 4), (2, 3), (1, 2)])
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
    Sequence_OrderedDict([(2, 3), (1, 2), (3, 4)])
    >>> d.keys.reverse()
    >>> d.keys
    [3, 1, 2]
    >>> d.keys = [1, 2, 3]
    >>> d
    Sequence_OrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.keys = [3, 1, 2]
    >>> d
    Sequence_OrderedDict([(3, 4), (1, 2), (2, 3)])
    >>> a = Sequence_OrderedDict()
    >>> b = Sequence_OrderedDict()
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
    >>> d = Sequence_OrderedDict(((1, 2), (2, 3), (3, 4)), strict=True)
    >>> d.keys[::-1] = [1, 2, 3]
    >>> d
    Sequence_OrderedDict([(3, 4), (2, 3), (1, 2)])
    >>> d.keys[:2]
    [3, 2]
    >>> d.keys[:2] = [1, 3]
    Traceback (most recent call last):
    KeyError: 'Keylist is not the same as current keylist.'

    >>> d = Sequence_OrderedDict(((1, 2), (2, 3), (3, 4)))
    >>> d
    Sequence_OrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.values
    [2, 3, 4]
    >>> d.values()
    [2, 3, 4]
    >>> d.setvalues((4, 3, 2))
    >>> d
    Sequence_OrderedDict([(1, 4), (2, 3), (3, 2)])
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
    Sequence_OrderedDict([(1, 2), (2, 3), (3, 4)])
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
    Sequence_OrderedDict([(1, 1), (2, 2), (3, 3)])

    >>> d = Sequence_OrderedDict(((1, 2), (2, 3), (3, 4)))
    >>> d
    Sequence_OrderedDict([(1, 2), (2, 3), (3, 4)])
    >>> d.items()
    [(1, 2), (2, 3), (3, 4)]
    >>> d.setitems([(3, 4), (2 ,3), (1, 2)])
    >>> d
    Sequence_OrderedDict([(3, 4), (2, 3), (1, 2)])
    >>> d.items[0]
    (3, 4)
    >>> d.items[:-1]
    [(3, 4), (2, 3)]
    >>> d.items[1] = (6, 3)
    >>> d.items
    [(3, 4), (6, 3), (1, 2)]
    >>> d.items[1:2] = [(9, 9)]
    >>> d
    Sequence_OrderedDict([(3, 4), (9, 9), (1, 2)])
    >>> del d.items[1:2]
    >>> d
    Sequence_OrderedDict([(3, 4), (1, 2)])
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
        _OrderedDict.__init__(self, init_val, strict=strict)
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
                _OrderedDict.__setattr__(self, name, value)
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

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

try:
    from collections import OrderedDict
except ImportError:
    if not '_OrderedDict' in dir():
        from odict import OrderedDict
    else:
        OrderedDict = _OrderedDict


class OrderedConfigParser(ConfigParser.ConfigParser):
    """
    Customization of ConfigParser to (a) use an ordered dictionary and (b)
    keep the original case of the data keys.
    """

    def __init__(self):
        if sys.version_info >= (2,6,0):
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
        if sys.version_info >= (2,6,0):
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

import subprocess
import re
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
try:
    import StringIO
except ImportError:
    import io as StringIO
import zipfile
import shutil
import string
import textwrap
import sys
import glob
import errno
import stat
import os

using_subversion = True

#
# Working around error with PYTHONHOME
#
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']
    print("WARNING: ignoring the value of the PYTHONHOME environment variable!  This value can corrupt the virtual python installation.")

print("\nNOTE: this Python executable used to create virtual environment:\n\t%s\n" % sys.executable)
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
        output = subprocess.Popen(['svn','ls',svndir], stdout=subprocess.PIPE).communicate()[0]
        if sys.version_info[:2] >= (3,0):
            if sys.stdout.encoding is None:
                output = output.decode('utf-8')
            else:
                output = output.decode(sys.stdout.encoding)
        if output=="":
            return None
        versions = []
        for link in re.split('/',output.strip()):
            tmp = link.strip()
            if tmp != '':
                versions.append( tmp )
    else:
        if sys.version_info[:2] <= (2,5):
            output = urllib2.urlopen(svndir).read()
        else:
            output = urllib2.urlopen(svndir, timeout=30).read()
            if sys.stdout.encoding is None:
                output = output.decode('utf-8')
            else:
                output = output.decode(sys.stdout.encoding)
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
                    try:
                        long16 = long(16)
                        long28 = long(28)
                    except NameError:
                        long16 = 16
                        long28 = 28
                    if fname.endswith('exe'):
                        # Octal shifts
                        #zf.external_attr = (0777 << 16L) | (010 << 28L)
                        # Decimal shifts
                        zf.external_attr = (511 << long16) | (8 << long28)
                    else:
                        # Octal shifts
                        #zf.external_attr = (0660 << 16L) | (010 << 28L)
                        # Decimal shifts
                        zf.external_attr = (432 << long16) | (8 << long28)
                    zf.write(join(root,fname))
        else:
            zf.write(file)
    zf.close()


def unzip_file(filename, dir=None, verbose=False):
    fname = os.path.abspath(filename)
    logger.info("Unzipping from file '%s'" % fname)
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
    logger.info("Unzipping done.")



class Repository(object):

    svn_get='checkout'
    easy_install_path = ["easy_install"]
    easy_install_flag = '-q'
    pip_path = ["pip"]
    python = "python"
    svn = "svn"
    dev = []

    def __init__(self, name, **kwds):
        class _TEMP_(object):
            def __init__(self, root=None, trunk=None, stable=None, release=None, tag=None, pyname=None, pypi=None, dev=False, username=None, install=True, rev=None, local=None, platform=None, version=None, branch=None, exit=True):
                import inspect
                args, varargs, varkw, defaults = inspect.getargspec(self.__init__)
                for i in range(len(args)-1):
                    kwd = args[i+1]
                    setattr(self, kwd, defaults[i])
        self.config = _TEMP_()
        self.config.name = name
        for kwd in kwds:
            if kwd == 'dev':
                if kwds[kwd] == 'True' or kwds[kwd] is True:
                    self.config.dev = True
                else:
                    self.config.dev = False
            elif kwd == 'install':
                if kwds[kwd] == 'False' or kwds[kwd] is False:
                    self.config.install = False
                else:
                    self.config.install = True
            elif kwd == 'exit':
                if kwds[kwd] == 'False' or kwds[kwd] is False:
                    self.config.exit = False
                else:
                    self.config.exit = True
            else:
                setattr(self.config, kwd, kwds[kwd])
        self.initialize(self.config)

    def initialize(self, config):
        self.name = config.name
        self.root = config.root
        self.trunk = None
        self.trunk_root = None
        self.branch = None
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
        self.version = config.version
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
                    rootdir_output = subprocess.Popen(['svn','ls',self.config.root], stdout=subprocess.PIPE).communicate()[0]
                else:
                    if sys.version_info[:2] <= (2,5):
                        rootdir_output = urllib2.urlopen(self.config.root).read()
                    else:
                        rootdir_output = urllib2.urlopen(self.config.root, timeout=30).read()
                if sys.version_info[:2] >= (3,0):
                    if sys.stdout.encoding is None:
                        rootdir_output = rootdir_output.decode('utf-8')
                    else:
                        rootdir_output = rootdir_output.decode(sys.stdout.encoding)
            if self.config.branch:
                self.trunk = self.config.root+'/branches/'+self.config.branch
            else:
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
        sys.stdout = OUTPUT
        print('[%s]' % config.name)
        if not config.root is None:
            print('root=%s' % config.root)
        if not config.trunk is None:
            print('trunk=%s' % config.trunk)
        if not config.stable is None:
            print('stable=%s' % config.stable)
        if not config.tag is None:
            print('tag=%s' % config.tag)
        elif not config.release is None:
            print('release=%s' % config.release)
        if not config.local is None:
            print('local=%s' % config.local)
        if not config.pypi is None:
            print('pypi=%s' % config.pypi)
        elif not config.pyname is None:
            print('pypi=%s' % config.pyname)
        print('dev=%s' % str(config.dev))
        if not config.branch is None:
            print('branch=%s' % str(config.branch))
        print('install=%s' % str(config.install))
        if not config.rev is None:
            print('rev=%s' % str(config.rev))
        if not config.username is None:
            print('username=%s' % str(config.username))
        if not config.platform is None:
            print('platform=%s' % config.platform)
        if not config.version is None:
            print('version=%s' % config.version)
        print('exit=%s' % config.exit)
        sys.stdout = sys.__stdout__


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
            raise IOError("Must have one of trunk, stable or release specified: %s" % self.name)


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
        if not self.version is None and not eval(self.version):
            return
        if self.pkgdir is None and self.local is None:
            self.easy_install(install, preinstall, dir, offline)
            return
        if self.local:
            install = True
        print("-----------------------------------------------------------------")
        print("  Installing branch")
        print("  Checking out source for package "+self.name)
        if self.local:
            print("     Package dir: "+self.local)
        else:
            print("     Subversion dir: "+self.pkgdir)
        if os.path.exists(dir):
            print("     No checkout required")
            print("-----------------------------------------------------------------")
        elif not using_subversion:
            print("")
            print("Error: Cannot checkout software %s with subversion." % self.name)
            print("A problem was detected executing subversion commands.")
            if self.config.exit:
                print("Aborting installer!")
                sys.exit(1)
            print("Not aborting installer...")
            return
        else:
            print("-----------------------------------------------------------------")
            try:
                self.run([self.svn]+self.svn_username+[Repository.svn_get,'-q',self.pkgdir+self.rev, dir])
            except OSError:
                err = sys.exc_info()[1] # BUG?
                print("")
                print("Error checkout software %s with subversion at %s" % (self.name,self.pkgdir+self.rev))
                print(str(err))
                if self.config.exit:
                    print("Aborting installer!")
                    sys.exit(1)
                print("Not aborting installer...")
                return
        if install:
            try:
                if self.dev:
                    if offline:
                        self.run([self.python, 'setup.py', 'develop', '--no-deps'], dir=dir)
                    else:
                        self.run([self.python, 'setup.py', 'develop'], dir=dir)
                else:
                    self.run([self.python, 'setup.py', 'install'], dir=dir)
            except OSError:
                err = sys.exc_info()[1] # BUG?
                print("")
                print("Error installing software %s from source using the setup.py file." % self.name)
                print("This is probably due to a syntax or configuration error in this package.")
                print(str(err))
                if self.config.exit:
                    print("Aborting installer!")
                    sys.exit(1)
                print("Not aborting installer...")

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
        print("-----------------------------------------------------------------")
        print("  Updating branch")
        print("  Updating source for package "+self.name)
        print("     Subversion dir: "+self.pkgdir)
        print("     Source dir:     "+dir)
        print("-----------------------------------------------------------------")
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
        except OSError:
            err = sys.exc_info()[1] # BUG?
            print("")
            print("Error installing package %s with easy_install" % self.name)
            print(str(err))
            if self.config.exit:
                print("Aborting installer!")
                sys.exit(1)
            print("Not aborting installer...")

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
        except OSError:
            err = sys.exc_info()[1] # BUG?
            print("")
            print("Error installing package %s with pip" % self.name)
            print(str(err))
            if self.config.exit:
                print("Aborting installer!")
                sys.exit(1)
            print("Not aborting installer...")

    def easy_upgrade(self):
        self.run(self.easy_install_path + [Repository.easy_install_flag, '--upgrade', self.pypi])

    def run(self, cmd, dir=None):
        cwd=os.getcwd()
        if not dir is None:
            os.chdir(dir)
            cwd=dir
        print("Running command '%s' in directory %s" % (" ".join(cmd), cwd))
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
            raise IOError("No repository info specified for repository "+args[0])
        repos = Repository( *args, **kwds)
        if repos.name in self.sw_dict:
            for i in range(len(self.sw_packages)):
                if self.sw_packages[i].name == repos.name:
                    self.sw_packages.pop(i)
                    break
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
            call_subprocess(['svn'+executable_extension,'--version'], show_stdout=False)
        except OSError:
            print("")
            print("------------------------------------------------")
            print("WARNING: problems executing subversion commands.")
            print("Subversion is disabled.")
            print("------------------------------------------------")
            print("")
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
                raise ValueError(
                    "Specified source directory does not exist! %s"
                    % self.srcdir )
        if os.path.abspath(sys.executable).startswith(self.abshome_dir):
            raise ValueError(
                "Python executable used to create the virtual environment:"
                "\n\t    %s\n\tfound within the target installation directory:"
                "\n\t    %s\n\tCowardly refusing to continue installation."
                % ( os.path.abspath(sys.executable), self.abshome_dir ) )

    def guess_path(self):
        return None

    def setup_installer(self, options):
        if options.preinstall:
            print("Creating preinstall zip file in '%s'" % self.home_dir)
        elif options.update:
            print("Updating existing installation in '%s'" % self.home_dir)
        else:
            print("Starting fresh installation in '%s'" % self.home_dir)
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
            print("  using the HTTP_PROXY environment: %s" % proxy)
            print("")
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
            print("-----------------------------------------------------------------")
            print(" STARTING preinstall in directory %s" % self.home_dir)
            print("-----------------------------------------------------------------")
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
        #
        # Parse config files
        #
        if options.update or options.release:
            if os.path.exists(join(self.abshome_dir, 'admin', 'config.ini')):
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
        print("-----------------------------------------------------------------")
        print("Finished processing configuration information.")
        print("-----------------------------------------------------------------")
        print(" START - Configuration summary")
        print("-----------------------------------------------------------------")
        self.write_config(stream=sys.stdout)
        print("-----------------------------------------------------------------")
        print(" END - Configuration summary")
        print("-----------------------------------------------------------------")
        #
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
            sys.stdout = open(join(self.abshome_dir,'admin',"virtualenv.cfg"),'w')
            print(options.trunk)
            print(options.stable)
            print(options.release)
            sys.stdout.close()
            sys.stdout = sys.__stdout__
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
        sys.stdout = open(join(self.abshome_dir,"README.txt"),"w")
        print(self.README.strip())
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        #
        # Finalize package export
        #
        self.finalize_packages(options)
        #
        # Finalize preinstall
        #
        if options.preinstall:
            print("-----------------------------------------------------------------")
            print(" FINISHED preinstall in directory %s" % self.home_dir)
            print("-----------------------------------------------------------------")
            os.chdir(self.abshome_dir)
            zip_file(self.default_dirname+'.zip', ['.'])
            sys.exit(0)

    def get_other_packages(self, options):
        #
        # Used by subclasses of Installer to
        # add packages that were requested through other means....
        #
        pass

    def finalize_packages(self, options):
        #
        # Perform final steps need to get packages
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
            print("")
            print("-----------------------------------------------------------------")
            print("  Add %s to the PATH environment variable" % (self.home_dir+os.sep+"bin"))
            print("-----------------------------------------------------------------")
        print("")
        print("Finished installation in '%s'" % self.home_dir)

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
                print("WARNING: Problem while localizing file '%s'.  This file is missing" % fname)
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
            print("Running command '%s'" % " ".join(cmd))
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
                    if sys.stdout.encoding is None:
                        output = output.decode('utf-8')
                    else:
                        output = output.decode(sys.stdout.encoding)
            except Exception:
                print("Problems opening configuration url: "+file)
                raise
            fp = StringIO.StringIO(output)
            parser.readfp(fp, file)
            fp.close()
        else:
            if not file in parser.read(file):
                raise IOError("Error while parsing file %s." % file)
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
                    # NB: option may come back unicode; if it does,
                    # convert it to a string (otherwise, **options can fail)
                    options[str(option)] = apply_template(value, os.environ)
                self.add_repository(sec, **options)

    def write_config(self, filename=None, stream=None):
        if not filename is None:
            OUTPUT=open(filename,'w')
            self.write_config(stream=OUTPUT)
            OUTPUT.close()
        else:
            sys.stdout = stream
            for repos in self.sw_packages:
                repos.write_config(stream)
                print("")
            if len(self.cmd_files) > 0:
                print("[localize]")
                for file in self.cmd_files:
                    print(file+"=")
                print("\n")
            sys.stdout = sys.__stdout__



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
    except Exception:
        err = sys.exc_info()[1] # BUG?
        if vpy_main.raise_exceptions:
            raise
        print("")
        print("ERROR: "+str(err))

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
    except OSError:
        print("-----------------------------------------------------------------")
        print("Error installing the 'setuptools' package!")
        if os.environ['HTTP_PROXY'] == '':
            print("")
            print("WARNING: you may need to set your HTTP_PROXY environment variable!")
        print("-----------------------------------------------------------------")
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
    except OSError:
        print("-----------------------------------------------------------------")
        print("Error installing the 'pip' package!")
        if os.environ['HTTP_PROXY'] == '':
            print("")
            print("WARNING: you may need to set your HTTP_PROXY environment variable!")
        print("-----------------------------------------------------------------")
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
        except Exception:
            print("Cannot create directory '%s'!" % path)
            print("Verify that you have write permissions to this directory.")
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
eJzFPf1z2zaWv/OvwMqTIZXKdD66nR2n7o2TOK333MTbpLO5dT1aSoIs1hTJEqRl7c3d337vAwAB
kvLHpp3TdGKJBB4eHt43HtDRaHRcljJfiHWxaDIplEyq+UqUSb1SYllUol6l1WK/TKp6C0/n18mV
VKIuhNqqGFvFQfD0Cz/BU/FplSqDAnxLmrpYJ3U6T7JsK9J1WVS1XIhFU6X5lUjztE6TLP0XtCjy
WDz9cgyC01zAzLNUVuJGVgrgKlEsxfm2XhW5iJoS5/w8/nPycjwRal6lZQ0NKo0zUGSV1EEu5QLQ
hJaNAlKmtdxXpZyny3RuG26KJluIMkvmUvzznzw1ahqGgSrWcrOSlRQ5IAMwJcAqEQ/4mlZiXixk
LMRrOU9wAH7eEitgaBNcM4VkzAuRFfkVzCmXc6lUUm1FNGtqAkQoi0UBOKWAQZ1mWbApqms1hiWl
9djAI5Ewe/iTYfaAeeL4fc4BHD/kwc95ejth2MA9CK5eMdtUcpneigTBwk95K+dT/SxKl2KRLpdA
g7weY5OAEVAiS2cHJS3Ht3qFvjsgrCxXJjCGRJS5Mb+kHnFwWoskU8C2TYk0UoT5WzlLkxyokd/A
cAARSBoMjbNIVW3HodmJAgBUuI41SMlaiWidpDkw64/JnND+e5ovio0aEwVgtZT4tVG1O/9ogADQ
2iHAJMDFMqvZ5Fl6LbPtGBD4BNhXUjVZjQKxSCs5r4sqlYoAAGpbIW8B6YlIKqlJyJxp5HZC9Cea
pDkuLAoYCjy+RJIs06umIgkTyxQ4F7ji3YefxNuT16fH7zWPGWAss1drwBmg0EI7OMEA4qBR1UFW
gEDHwRn+EcligUJ2heMDXm2Dg3tXOohg7mXc7eMsOJBdL64eBuZYgzKhsQLq99/QZaJWQJ//uWe9
g+B4F1Vo4vxtsypAJvNkLcUqYf5Czgi+1XC+i8t69Qq4QSGcGkilcHEQwRThAUlcmkVFLkUJLJal
uRwHQKEZtfVXEVjhfZHv01p3OAEgVEEOL51nYxoxlzDRPqxXqC9M4y3NTDcJ7Dqvi4oUB/B/Pidd
lCX5NeGoiKH420xepXmOCCEvBOFeSAOr6xQ4cRGLM2pFesE0EiFrL26JItEALyHTAU/K22RdZnLC
4ou69W41QoPJWpi1zpjjoGVN6pVWrZ3qIO+9iD93uI7QrFeVBODNzBO6ZVFMxAx0NmFTJmsWr3pT
EOcEA/JEnZAnqCX0xe9A0WOlmrW0L5FXQLMQQwXLIsuKDZDsMAiE2MNGxij7zAlv4R38C3Dx30zW
81UQOCNZwBoUIr8LFAIBkyBzzdUaCY/bNCt3lUyas6YoqoWsaKiHEfuAEX9gY5xr8L6otVHj6eIq
F+u0RpU00yYzZYuXhzXrx1c8b5gGWG5FNDNNWzqtcXpZuUpm0rgkM7lESdCL9MouO4wZDIxJtrgW
a7Yy8A7IIlO2IMOKBZXOspbkBAAMFr4kT8smo0YKGUwkMNC6JPjrBE16oZ0lYG82ywEqJDbfc7A/
gNu/QIw2qxToMwcIoGFQS8HyzdK6Qgeh1UeBb/RNfx4fOPV0qW0TD7lM0kxb+SQPTunhSVWR+M5l
ib0mmhgKZpjX6Npd5UBHFPPRaBQExh3aKvO1UEFdbQ+BFYQZZzqdNSkavukUTb3+oQIeRTgDe91s
OwsPNITp9B6o5HRZVsUaX9u5fQRlAmNhj2BPnJOWkewge5z4CsnnqvTSNEXb7bCzQD0UnP908u70
88lHcSQuWpU26eqzSxjzJE+ArckiAFN1hm11GbRExZei7hPvwLwTU4A9o94kvjKpG+BdQP1T1dBr
mMbcexmcvD9+fXYy/fnjyU/Tj6efTgBBsDMy2KMpo3lswGFUMQgHcOVCxdq+Br0e9OD18Uf7IJim
alpuyy08AEMJLFxFMN+JCPHhVNvgaZovi3BMjX9lJ/yI1Yr2uC4Ov74UR0ci/DW5ScIAvJ62KS/i
jyQAn7alhK41/IkKNQ6ChVyCsFxLFKnoKXmyY+4ARISWhbasvxZpbt4zH7lDkMRH1ANwmE7nWaIU
Np5OQyAtdRj4QIeY3WGUkwg6llu361ijgp9KwlLk2GWC/wygmMyoH6LBKLpdTCMQsPU8UZJb0fSh
33SKWmY6jfSAIH7E4+AiseIIhWmCWqZKwRMlXkGtM1NFhj8RPsotiQwGQ6jXcJF0sBPfJFkjVeRM
CogYRR0yompMFXEQOBUR2M526cbjLjUNz0AzIF9WgN6rOpTDzx54KKBgTNiFoRlHS0wzxPSvHBsQ
DuAkhqiglepAYX0mzk/OxctnL/bRAYEocWGp4zVHm5rmjbQPl7BaV7J2EOZe4YSEYezSZYmaEZ8e
3g1zHduV6bPCUi9xJdfFjVwAtsjAziqLn+gNxNIwj3kCqwiamCw4Kz3j6SUYOfLsQVrQ2gP11gTF
rL9Z+j0O32WuQHVwKEyk1nE6G6+yKm5SdA9mW/0SrBuoN7RxxhUJnIXzmAyNGGgI8FtzpNRGhqDA
qoZdTMIbQaKGX7SqMCZwZ6hbL+nrdV5s8inHrkeoJqOxZV0ULM282KBdgj3xDuwGIFlAKNYSjaGA
ky5QtvYBeZg+TBcoS9EAAALTrCjAcmCZ4IymyHEeDoswxq8ECW8l0cLfmCEoODLEcCDR29g+MFoC
IcHkrIKzqkEzGcqaaQYDOyTxue4s5qDRB9ChYgyGLtLQuJGh38UhKGdx5iolpx/a0M+fPzPbqBVl
RBCxGU4ajf6SzFtcbsEUpqATjA/F+RVigw24owCmUZo1xf5HUZTsP8F6nmvZBssN8Vhdl4cHB5vN
Jtb5gKK6OlDLgz//5Ztv/vKMdeJiQfwD03GkRSfH4gN6hz5o/K2xQN+ZlevwY5r73EiwIkl+FDmP
iN/3TbooxOH+2OpP5OLWsOK/xvkABTI1gzKVgbajFqMnav9J/FKNxBMRuW2jMXsS2qRaK+ZbXehR
F2C7wdOYF01eh44iVeIrsG4QUy/krLkK7eCejTQ/YKoop5Hlgf3nl4iBzxmGr4wpnqKWILZAi++Q
/idmm4T8Ga0hkLxoonrx7nZYixniLh4u79Y7dITGzDBVyB0oEX6TBwugbdyXHPxoZxTtnuOMmo9n
CIylDwzzalcwQsEhXHAtJq7UOVyNPipI04ZVMygYVzWCgga3bsbU1uDIRoYIEr0bE57zwuoWQKdO
rs9E9GYVoIU7Ts/adVnB8YSQB47Ec3oiwak97L17xkvbZBmlYDo86lGFAXsLjXa6AL6MDICJGFU/
j7ilCSw+dBaF12AAWMFZG2SwZY+Z8I3rA472RgPs1LP6u3ozjYdA4CJFnD16EHRC+YhHqBRIUxn5
PXexuCVuf7A7LQ4xlVkmEmm1Q7i6ymNQqO40TMs0R93rLFI8zwrwiq1WJEZq3/vOAkUu+HjImGkJ
1GRoyeE0OiJvzxPAULfDhNdVg6kBN3OCGK1TRdYNybSCf8CtoIwEpY+AlgTNgnmolPkT+x1kzs5X
f9nBHpbQyBBu011uSM9iaDjm/Z5AMur8CUhBDiTsCyO5jqwOMuAwZ4E84YbXcqd0E4xYgZw5FoTU
DOBOL70AB5/EuGdBEoqQb2slS/GVGMHydUX1Ybr7d+VSkzaInAbkKuh8w5Gbi3DyEEedvITP0H5G
gnY3ygI4eAYuj5uad9ncMK1Nk4Cz7ituixRoZMqcjMYuqpeGMG76909HTouWWGYQw1DeQN4mjBlp
HNjl1qBhwQ0Yb827Y+nHbsYC+0ZhoV7I9S3Ef2GVqnmhQgxwe7kL96O5ok8bi+1ZOhvBH28BRuNL
D5LMdP4Csyz/xiChBz0cgu5NFtMii6TapHlICkzT78hfmh4elpSekTv4SOHUAUwUc5QH7yoQENqs
PABxQk0AUbkMlXb7+2DvnOLIwuXuI89tvjh8edkn7mRXhsd+hpfq5LauEoWrlfGisVDgavUNOCpd
mFySb/V2o96OxjChKhREkeLDx88CCcGZ2E2yfdzUW4ZHbO6dk/cxqINeu5dcndkRuwAiqBWRUQ7C
x3Pkw5F97OTumNgjgDyKYe5YFANJ88m/A+euhYIx9hfbHPNoXZWBH3j9zdfTgcyoi+Q3X4/uGaVD
jCGxjzqeoB2ZygDE4LRNl0omGfkaTifKKuYt79g25ZgVOsV/mskuB5xO/Jj3xmS08HvNe4Gj+ewR
PSDMLma/QrCqdH7rJkkzSsoDGvv7qOdMnM2pg2F8PEh3o4w5KfBYnk0GQyF18QwWJuTAftyfjvaL
jk3udyAgNZ8yUX1U9vQGfLt/5G2qu3uHfajamBgeesaZ/hcDWsKb8ZBd/xINh5/fRRlYYB4NRkNk
9xzt/+9ZPvtjJvnAqZht39/RMD0S0O81E9bjDE3r8XHHIA4tu2sCDbAHWIodHuAdHlp/aN7oWxo/
i1WSEk9Rdz0VG9rrpzQnbtoAlAW7YANwcBn1jvGbpqp435dUYCmrfdzLnAgsczJOGFVP9cEcvJc1
YmKbzSlt7BTFFENqJNSJYDuTsHXhh+VsVZj0kcxv0gr6gsKNwh8+/HgS9hlAD4OdhsG562i45OEm
HOE+gmlDTZzwMX2YQo/p8u9LVTeK8AlqttNNclaTbdA++DlZE9IPr8E9yRlv75T3qDFYnq/k/Hoq
ad8d2RS7OvnpN/gaMbHb8X7xlEqWVAEGM5lnDdKKfWAs3Vs2+Zy2KmoJro6us8W6G9pN50zcMkuu
RESdF5gF0txIiaKbpNKOYFkVWNkpmnRxcJUuhPytSTKMsOVyCbjgPpJ+FfPwlAwSb7kggCv+lJw3
VVpvgQSJKvQ2HNUOOA1nW55o5CHJOy5MQKwmOBQfcdr4ngm3MOQycbq/+YCTxBAYO5h9UuQueg7v
82KKo06pQHbCSPW3yOlx0B2hAAAjAArzH411Es1/I+mVu9dHa+4SFbWkR0o36C/IGUMo0RiTDvyb
fvqM6PLWDiyvdmN5dTeWV10srwaxvPKxvLobS1ckcGFt/shIwlAOqbvDMFis4qZ/eJiTZL7idlg4
iQWSAFGUJtY1MsX1w16SibfaCAipbWfvlx62xScpV2RWBWejNUjkftxP0nG1qfx2OlMpi+7MUzHu
7K4CHL/vQRxTndWMurO8LZI6iT25uMqKGYitRXfSApiIbi0Opy3zm+mME60dSzU6/69PP3x4j80R
1MhUGlA3XEQ0LDiV6GlSXam+NLVxWAnsSC39mhjqpgHuPTDJxaPs8T9vqdgCGUdsqFigECV4AFQS
ZZu5hUNh2HmuK4z0c2Zy3vc5EqO8HrWT2kGk4/Pzt8efjkeUfRv978gVGENbXzpcfEwL26Dvv7nN
LcWxDwi1TjO1xs+dk0frliPut7EGbM+H7zx48RCDPRix+7P8QykFSwKEinUe9jGEenAM9EVhQo8+
hhF7lXPuJhc7K/adI3uOi+KI/tAOQHcAf98RY4wpEEC7UJGJDNpgqqP0rXm9g6IO0Af6el8cgnVD
r24k41PUTmLAAXQoa5vtdv+8LRM2ekrWr0++P31/dvr6/PjTD44LiK7ch48HL8TJj58FlWqgAWOf
KMEqhRqLgsCwuKeExKKA/xrM/CyamvO10Ovt2ZneNFnjOREsHEabE8Nzriiy0Dh9xQlh+1CXAiFG
mQ6QnAM5VDlDB3YwXlrzYRBV6OJiOuczQ2e10aGXPmhlDmTRFnMM0geNXVIwCK72gldUAl6bqLDi
zTh9SGkAKW2jbY1GRum53s69sxVlNjq8nCV1hidtZ63oL0IX1/AyVmWWQiT3KrSypLthpUrLOPqh
3WtmvIY0oNMdRtYNedY7sUCr9Srkuen+45bRfmsAw5bB3sK8c0mVGlS+jHVmIsRGvKkSylv4apde
r4GCBcM9txoX0TBdCrNPILgWqxQCCODJFVhfjBMAQmcl/Nz8oZMdkAUWSoRv1ov9v4WaIH7rX34Z
aF5X2f4/RAlRkOCqnnCAmG7jtxD4xDIWJx/ejUNGjqpkxd8arK0Hh4QSoI60UykRb2ZPIyWzpS71
8PUBvtB+Ar3udK9kWenuw65xiBLwREXkNTxRhn4hVl5Z2BOcyrgDGo8NWMzw+J1bEWA+e+LjSmaZ
LhY/fXt2Ar4jnmRACeItsBMYjvMluJut6+D4eGAHFO51w+sK2bhCF5bqHRax12wwaY0iR729Egm7
TpQY7vfqZYGrJFUu2hFOm2GZWvwYWRnWwiwrs3anDVLYbUMUR5lhlpieV1RL6vME8DI9TTgkglgJ
z0mYDDxv6KZ5bYoHs3QOehRULijUCQgJEhcPAxLnFTnnwItKmTNE8LDcVunVqsZ9Bugc0/kFbP7j
8eez0/dU0//iZet1DzDnhCKBCddzHGG1HmY74ItbgYdcNZ0O8ax+hTBQ+8Cf7isuFDniAXr9OLGI
f7qv+BDXkRMJ8gxAQTVlVzwwAHC6DclNKwuMq42D8eNW47WY+WAoF4lnRnTNhTu/Pifalh1TQnkf
8/IRGzjLUtMwMp3d6rDuR89xWeKO0yIabgRvh2TLfGbQ9br3ZlcdmvvpSSGeJwWM+q39MUyhVq+p
no7DbLu4hcJabWN/yZ1cqdNunqMoAxEjt/PYZbJhJaybMwd6Fc09YOJbja6RxEFVPvolH2kPw8PE
ErsXp5iOdKKEjABmMqQ+ONOAD4UWARQIFeJGjuROxk9feHN0rMH9c9S6C2zjD6AIdVksHbcoKuBE
+PIbO478itBCPXooQsdTyWVe2JIt/GxW6FU+9+c4KAOUxESxq5L8SkYMa2JgfuUTe0cKlrStR+qL
9HLIsIhTcE5vd3B4Xy6GN04Mah1G6LW7ltuuOvLJgw0GT2XcSTAffJVsQPeXTR3xSg6L/PBBtN1Q
74eIhYDQVO+DRyGmY34Ld6xPC3iQGhoWeni/7diF5bUxjqy1j50DRqF9oT3YeQWhWa1oW8Y52Wd8
UesFtAb3qDX5I/tU1+zY3wNHtpyckAXKg7sgvbmNdINOOmHEJ4f42GVKlentwRb9biFvZFaA6wVR
HR48+NUePBjHNp0yWJL1xdidb8+3w7jRmxazQ3MyAj0zVcL6xbmsDxCdwYzPXZi1yOBS/6JDkiS/
Ji/5zd9PJ+LN+5/g39fyA8RVeHJwIv4BaIg3RQXxJR99pTsJ8FBFzYFj0Sg8XkjQaKuCr29At+3c
ozNui+jTHv4xD6spBRa4Vmu+MwRQ5AnScfDWTzBnGOC3OWTV8UaNpzi0KCP9Emmw+9wJntU40C3j
Vb3O0F44WZJ2NS9GZ6dvTt5/PInrW+Rw83PkZFH82iicjt4jrnA/bCLsk3mDTy4dx/kHmZUDfrMO
Os0ZFgw6RQhxSWkDTb6PIrHBRVJh5kCU20Uxj7ElsDwfm6s34EiPnfjyXkPvWVmEFY31LlrrzeNj
oIb4pauIRtCQ+ug5UU9CKJnh+S1+HI+GTfFEUGob/jy93izczLg+iEMT7GLazjryu1tduGI6a3iW
kwivI7sM5mxmliZqPZu7Z/Y+5EJfJwJajvY55DJpslrIHCSXgny61wE0vXvMjiWEWYXNGZ09ozRN
tkm2yilCSpQY4agjOpqOGzKUMYQY/Mfkmu0Bnv8TDR8kBuiEKMVPhdNVNfMVSzCHRES9gcKDTZq/
dOt5NIV5UI6Q560jC/NEt5ExupK1nj8/iMYXz9tKB8pKz71DtvMSrJ7LJnugOsunT5+OxH/c7/0w
KnFWFNfglgHsQa/ljF7vsNx6cna1+p69eRMDP85X8gIeXFL23D5vckpN3tGVFkTavwZGiGsTWmY0
7Tt2mZN2FW80cwvesNKW4+c8pUuDMLUkUdnqu5cw7WSkiVgSFEOYqHmahpymgPXYFg2ej8M0o+YX
eQscnyKYCb7FHTIOtVfoYVItq+Uei86RGBHgEdWW8Wh0wJhOiAGe0/OtRnN6mqd1e7Tjmbt5qg/S
1/YuIM1XItmgZJh5dIjhHLX0WLX1sIs7WdSLWIr5hZtw7MySX9+HO7A2SFqxXBpM4aFZpHkhq7kx
p7hi6TytHTCmHcLhznQFElmfOBhAaQTqnazCwkq0ffsnuy4uph9oH3nfjKTLh2p7rRQnh5K8U2AY
x+34lIayhLR8a76MYZT3lNbWnoA3lviTTqpiXb93+4V7xLDJ9a0WXL/RXnUBcOgmJasgLTt6OsK5
vsvCZ6bdcRcFfihEJ9xu0qpukmyqL0+YosM2tRvrGk97NO3OQ5fWWwEnvwAPeF9X0YPjYKpskJ5Y
BGtOSRyJpU5RxO5pL/9gVFmgl/eCfSXwKZAyi6k5o2ySSBeWXe3hT12z6ah4BPWVOVD0EJtgjrX0
ToS405hQ0VM47la59lrhBos5tmA9725k8KghO7B8L95MsHunhfjuSETPJ+LPnUBsXm7xViYgw5NF
/GQR+j4hdb04fNHauX7g24GwE8jLy0dPN0tnNL1wqPz8/r666BED0DXI7jKVi/0nCrFjnL8UqobS
zms3p9KM8XT6nq260gez2+MqdCptBlHFplVojmoz/q8dxJz41nqID8ei0mALaA/0m8KXTvGhvXQN
CxM1ev7KopRMhzbH8BtenALvNUFdodq5aaor7C3YgZyAPkbJW2Btw4Gg8BE8FNIlL7RoX3W2hf/I
xeOi/V2biz0sv/n6LjxdAR88sTBAUI+YTqs/kKl2ssxjF+YB+/X389/Dee8uvns0lXSvYVphKIWF
zKuE36BJbMpDm2owIolbQZFb3oaf+nrwTAyLI+qm+jq8a/rc/6656xaBnbnZ3e3N3T/75tJA993N
L0M04DBPE+JBNeOtwA7rAleMJ7qoYDhlqT9IfrcTznSHVrgPjClhwAQosanG3mjNdTJ3v2OFzD5f
7+oedRzU1Z1p985+djn+IYqWqwHwuT39TCUeC82B7DfSfV1TLhqcyqsrNU3wrrgpBRtU4NLzIo37
+o6u+pKJ2hqvEy9UARCGm3QpolttDIwBAQ3fWcv1Ic7NGYKGpipKpyxTpQvOIGkXF8DFnDmi/iYz
yXWVo0xiwk81VVlBVDDSN5ty4cJQrWcL1CQy1om6NqibHhN90SUOwdUy5ngk56s40vCoA4TgU1PO
tU1cqDyd2nfAL8/aY+DpxDKEzJu1rJK6vQLF3yZNxXfOCHQoFhfYSVW0ktnhFBex1PKHgxQmC+z3
r7ST7QUZd5z9Hlut93C2oh46BfaYY+WO7THcnN7aK9Dcq3cWdGGua+Rts5b77LUvsBTmPi/SlTp3
wG/1HUN8cyVnNtFNcPgI5N49kuaX51q1xk6KRcN55iqG/qUyeKqZbPHQXXE9LujfCtdx9O34vt6w
zNILDXY0tlTUrtWg4mlHG7cRNVbS3RNR+9XSj4yoPfgPjKj1zX5gcDQ+Wh8M1k/fE3qzmnCvyWsZ
AfpMgUi4s9e5ZM2YzMitRoawN70d2WtqWWc6R5yMmUCO7N+fRCD4Ojzllm5611WZcYciWl+66PH3
Zx9eH58RLabnx2/+8/h7qlbB9HHHZj045ZAX+0ztfa8u1k0/6AqDocFbbAfuneTDHRpC731vc3YA
wvBBnqEF7Soy9/WuDr0DEf1OgPjd0+5A3aWyByH3/DNdfO/WFXQKWAP9lKsNzS9ny9Y8MjsXLA7t
zoR53yaTtYz2cm27Fs6p++urE+236psKd+QBx7b6lFYAc8jIXzaFbI4S2EQlOyrd/3kAlcziMSxz
ywdI4Vw6t83RRXMMqvb/LwUVKLsE98HYYZzYG3+pHafLlb3KGvfC5jI2BPHOQY3683OFfSGzHVQI
AlZ4+i41RsToP73BZLdjnyhxsU8nLvdR2VzaX7hm2sn9e4qbrrW9k0hx5QZvO0HjZZO5G6m2T68D
OX+UnS+WTok/aL4DoHMrngrYG30mVoizrQghkNQbhlg1SHTUF4o5yKPddLA3tHom9nedx3PPownx
fHfDRefIm+7xgnuoe3qoxpx6ciwwlq/tOmgnviPIvL0j6BIiz/nAPUV99y18vbl4fmiTrcjv+NpR
JFRmM3IM+4VTpnbnxXdOd2KWakJ1TBizOcc0dYtLByr7BLtinF6t/o44yOz7MqSR9364yMf08C70
HnUxtax3CFMS0RM1pmk5pxs07vbJuD/dVm31gfBJjQcA6alAgIVgerrRqZzbcvlr9ExHhbOGrgx1
M+6hIxVUReNzBPcwvl+LX7c7nbB8UHdG0fTnBl0O1EsOws2+A7caeymR3SahO/WWD3a4AHxYdbj/
8wf079d32e4v7vKrbauXgwek2JfFkkCslOiQyDyOwciA3oxIW2MduRF0vJ+jpaPLUO3ckC/Q8aMy
Q7wQmAIMcman2gOwRiH4P2ts6wE=
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
eJytVVFvokAQfudXTLEP2pw1fW3jg01NNGm1KV4vd22zrDDIJrhrYJHay/33m0VEKGpyufIg7s63
M9/OfDO0YBaKBAIRISzTRMMcIU3Qh0zoEOxEpbGHMBeyxz0t1lyjDRdBrJYw50l4YbVgo1LwuJRK
Q5xKEBp8EaOno41l+bg7Be0O/LaAnhbEmKAGFfmAci1iJZcoNax5LPg8wiRHiQBeoCvBPmfT+zv2
PH6afR/cs8fBbGTDG9yADlHmSPOY7f4haInA95WKdQ4s91JpeDQO5fZAnKTxczaaTkbTh+EhMqWx
QWl/rEGsNJ2kV0cRySKleRGTUKWUVB81pT+vD3Dpw0cSfoMsFF4IIV8jcHqRyVPLpTHrkOu89IUr
EoDHo4gkoBUsiAFVlP4FKjaLFSeNFEeTS4AfJBOV6sKshVwUbmpAkyA4N8kFL+RygQlkpDfum58N
GO1QWNLFipij/yn1twOHit5V29UvZ8Seh0/OeDo5kPz8at24lp5jRXSuDlXPuWqUjYCNejlXJwtV
mHcUtpCddTh53hM7I15EpA+2VNLHRMep6Rn8xK0FDkYB7ABnn6J3jWnXbLvQfyzqz61dxDFGVP1a
o1Xasx7bsipU+zZjlSVjtlUkoXofq9FHlMZtDxaLCrrH2O14wiaDhyFj1wWs2qIl773iTbZohyza
iD0TUQQBF5HZr6ISgzKKNZrD5UpvgO5FwoT2tgkIMec+tcYm45sO+fPytqGpBy75aufpTG/gmhRb
+u3AjQtC5l1l7QV1dBAcadt+7UhFGpXONprZRviAWtbY3dgZ3N4P2ePT9OFxdjJiruJSuLk7+31f
x60HKiWc9eH9SBc04XuPGCVYce1SXlDyJcJrjfKr7ebSNpEaQVpg+l3wiAYOJZ9GCAxoR9JMWAiv
+IyoWBSfhOIIIoRar657vSzLLj9Q0xRZX9Kk6SUq0BmPsceNl179Mi8Vii65Pkj21XXf4MAlSy/t
Exft7A8WX4/iVRkZprZfNK2/YFL/55T+9wm9m86Uhr8A0Hwt
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

##file activate.ps1
ACTIVATE_PS = convert("""
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
QastYw==
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
eJyNU01v2zAMvetXEB4K21jmDOstQA4dMGCHbeihlyEIDMWmG62yJEiKE//7kXKdpN2KzYBt8euR
fKSyLPs8wiEo8wh4wqZTGou4V6Hm0wJa1cSiTkJdr8+GsoTRHuCotBayiWqQEYGtMCgfD1KjGYBe
5a3p0cRKiAe2NtLADikftnDco0ko/SFEVgEZ8aRC5GLux7i3BpSJ6J1H+i7A2CjiHq9z7JRZuuQq
siwTIvpxJYCeuWaBpwZdhB+yxy/eWz+ZvVSU8C4E9FFZkyxFsvCT/ZzL8gcz9aXVE14Yyp2M+2W0
y7n5mp0qN+avKXvbsyyzUqjeWR8hjGE+2iCE1W1tQ82hsCZN9UzlJr+/e/iab8WfqsmPI6pWeUPd
FrMsd4H/55poeO9n54COhUs+sZNEzNtg/wanpjpuqHJaxs76HtZryI/K3H7KJ/KDIhqcbJ7kI4ar
XL+sMgXnX0D+Te2Iy5xdP8yueSlQB/x/ED2BTAtyE3K4SYUN6AMNfbO63f4lBW3bUJPbTL+mjSxS
PyRfJkZRgj+VbFv+EzHFi5pKwUEepa4JslMnwkowSRCXI+m5XvEOvtuBrxHdhLalG0JofYBok6qj
YdN2dEngUlbC4PG60M1WEN0piu7Nq7on0mgyyUw3iV1etLo6r/81biWdQ9MWHFaePWZYaq+nmp+t
s3az+sj7eA0jfgPfeoN1
""")

if __name__ == '__main__':
    main()

## TODO:
## Copy python.exe.manifest
## Monkeypatch distutils.sysconfig
