#!/usr/bin/env python
## WARNING: This file is generated
#!/usr/bin/env python
"""Create a "virtual" Python installation
"""

virtualenv_version = "1.5.1"

import sys
import os
import optparse
import re
import shutil
import logging
import tempfile
import distutils.sysconfig
try:
    import subprocess
except ImportError, e:
    if sys.version_info <= (2, 3):
        print 'ERROR: %s' % e
        print 'ERROR: this script requires Python 2.4 or greater; or at least the subprocess module.'
        print 'If you copy subprocess.py from a newer version of Python this script will probably work'
        sys.exit(101)
    else:
        raise
try:
    set
except NameError:
    from sets import Set as set

join = os.path.join
py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])

is_jython = sys.platform.startswith('java')
is_pypy = hasattr(sys, 'pypy_version_info')

if is_pypy:
    expected_exe = 'pypy-c'
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

if sys.version_info[:2] >= (2, 6):
    REQUIRED_MODULES.extend(['warnings', 'linecache', '_abcoll', 'abc'])
if sys.version_info[:2] >= (2, 7):
    REQUIRED_MODULES.extend(['_weakrefset'])
if sys.version_info[:2] <= (2, 3):
    REQUIRED_MODULES.extend(['sets', '__future__'])
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

def mkdir(path):
    if not os.path.exists(path):
        logger.info('Creating %s', path)
        os.makedirs(path)
    else:
        logger.info('Directory %s already exists', path)

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
    if symlink and hasattr(os, 'symlink'):
        logger.info('Symlinking %s', dest)
        os.symlink(os.path.abspath(src), dest)
    else:
        logger.info('Copying to %s', dest)
        if os.path.isdir(src):
            shutil.copytree(src, dest, True)
        else:
            shutil.copy2(src, dest)

def writefile(dest, content, overwrite=True):
    if not os.path.exists(dest):
        logger.info('Writing %s', dest)
        f = open(dest, 'wb')
        f.write(content)
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
            f.write(content)
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
        oldmode = os.stat(fn).st_mode & 07777
        newmode = (oldmode | 0555) & 07777
        os.chmod(fn, newmode)
        logger.info('Changed mode of %s to %s', fn, oct(newmode))

def _find_file(filename, dirs):
    for dir in dirs:
        if os.path.exists(join(dir, filename)):
            return join(dir, filename)
    return filename

def _install_req(py_executable, unzip=False, distribute=False):
    if not distribute:
        setup_fn = 'setuptools-0.6c11-py%s.egg' % sys.version[:3]
        project_name = 'setuptools'
        bootstrap_script = EZ_SETUP_PY
        source = None
    else:
        setup_fn = None
        source = 'distribute-0.6.14.tar.gz'
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

    search_dirs = file_search_dirs()

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
            os.chdir(os.path.dirname(source))
            # in this case, we want to be sure that PYTHONPATH is unset (not
            # just empty, really unset), else CPython tries to import the
            # site.py that it's in virtualenv_support
            remove_from_env.append('PYTHONPATH')
        else:
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

def install_setuptools(py_executable, unzip=False):
    _install_req(py_executable, unzip)

def install_distribute(py_executable, unzip=False):
    _install_req(py_executable, unzip, distribute=True)

_pip_re = re.compile(r'^pip-.*(zip|tar.gz|tar.bz2|tgz|tbz)$', re.I)
def install_pip(py_executable):
    filenames = []
    for dir in file_search_dirs():
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
        logger.info('Installing pip from network...')
    else:
        logger.info('Installing %s' % os.path.basename(filename))
    logger.indent += 2
    def _filter_setup(line):
        return filter_ez_setup(line, 'pip')
    try:
        call_subprocess(cmd, show_stdout=False,
                        filter_stdout=_filter_setup)
    finally:
        logger.indent -= 2

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
        print 'You must provide a DEST_DIR'
        parser.print_help()
        sys.exit(2)
    if len(args) > 1:
        print 'There must be only one argument: DEST_DIR (you gave %s)' % (
            ' '.join(args))
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
                       use_distribute=options.use_distribute,
                       prompt=options.prompt)
    if 'after_install' in globals():
        after_install(options, home_dir)

def call_subprocess(cmd, show_stdout=True,
                    filter_stdout=None, cwd=None,
                    raise_on_returncode=True, extra_env=None,
                    remove_from_env=None):
    cmd_parts = []
    for part in cmd:
        if len(part) > 40:
            part = part[:30]+"..."+part[-5:]
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
    except Exception, e:
        logger.fatal(
            "Error %s while executing command %s" % (e, cmd_desc))
        raise
    all_output = []
    if stdout is not None:
        stdout = proc.stdout
        while 1:
            line = stdout.readline()
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
                       prompt=None):
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
        install_distribute(py_executable, unzip=unzip_setuptools)
    else:
        install_setuptools(py_executable, unzip=unzip_setuptools)

    install_pip(py_executable)

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
                print 'Error: the path "%s" has a space in it' % home_dir
                pass
                print '  http://sourceforge.net/projects/pywin32/'
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
        inc_dir = join(home_dir, 'include', py_version)
        bin_dir = join(home_dir, 'bin')
    return home_dir, lib_dir, inc_dir, bin_dir


def change_prefix(filename, dst_prefix):
    prefixes = [sys.prefix]
    if hasattr(sys, 'real_prefix'):
        prefixes.append(sys.real_prefix)
    prefixes = map(os.path.abspath, prefixes)
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
        print 'Please use the *system* python to run this script'
        return

    if clear:
        rmtree(lib_dir)
        # pyutilib.virtualenv: ignoring comment
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
                if fn != 'site-packages' and os.path.splitext(fn)[0] in REQUIRED_FILES:
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
        stdinc_dir = join(prefix, 'include', py_version)
    if os.path.exists(stdinc_dir):
        copyfile(stdinc_dir, inc_dir)
    else:
        logger.debug('No include dir %s' % stdinc_dir)

    if sys.exec_prefix != prefix:
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
        # pyutilib.virtualenv: ignoring comment
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
    cmd = [py_executable, '-c', 'import sys; print sys.prefix']
    logger.info('Testing executable with %s %s "%s"' % tuple(cmd))
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE)
    proc_stdout, proc_stderr = proc.communicate()
    proc_stdout = os.path.normcase(os.path.abspath(proc_stdout.strip()))
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
    # pyutilib.virtualenv: ignoring comment
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
    # pyutilib.virtualenv: ignoring comment
    ## there's a local distutils.cfg with a prefix setting?
    home_dir = os.path.abspath(home_dir)
    # pyutilib.virtualenv: ignoring comment
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
        sys.exit(3)
    return exe

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
    # pyutilib.virtualenv: ignoring comment

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
    if using_subversion:
        output = commands.getoutput('svn ls '+svndir)
        if output=="":
            return None
        #print output
        versions = []
# This allows for parsing version with the syntax:
#   9.3.2
#   8.28.rc1
#
def guess_release(svndir):
    if using_subversion:
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
    pip_path = ["pip"]
    python = "python"
    svn = "svn"
    dev = []

    def __init__(self, name, root=None, trunk=None, stable=None, release=None, tag=None, pyname=None, pypi=None, dev=False, username=None, install=True, rev=None, local=None):
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
                if using_subversion:
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
                    self.run(self.easy_install_path + ['-q', self.pypi], dir=os.path.dirname(dir))
            elif preinstall: 
                if not os.path.exists(dir):
                    self.run(self.easy_install_path + ['-q', '--exclude-scripts', '--always-copy', '--editable', '--build-directory', '.', self.pypi], dir=os.path.dirname(dir))
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
        self.run(self.easy_install_path + ['-q', '--upgrade', self.pypi])

    def run(self, cmd, dir=None):
        cwd=os.getcwd()
        if not dir is None:
            os.chdir(dir)
            cwd=dir
        print "Running command '%s' in directory %s" % (" ".join(cmd), cwd)
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
        verbosity = options.verbose - options.quiet
        self.logger = Logger([(Logger.level_for_integer(2-verbosity), sys.stdout)])
        logger = self.logger
        #
        # Determine if the subversion command is available
        #
        global using_subversion
        try:
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
            self.read_config_file(fp=fp)
            fp.close()
        if not self.config_file is None and (len(options.config_files) == 0 or options.keep_config):
            self.read_config_file(file=self.config_file)
        for file in options.config_files:
            self.read_config_file(file=file)
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
        elif sys.platform.startswith('win'):
            Repository.python = os.path.abspath(join(bindir, 'pythonw'))
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
            call_subprocess(cmd, filter_stdout=filter_python_develop,show_stdout=True)

    def read_config_file(self, file=None, fp=None):
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
        if 'localize' in sections:
            for option, value in parser.items('localize'):
                self.add_dos_cmd(option)
        for sec in sections:
            if sec in ['installer', 'localize']:
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

def install_setuptools(py_executable, unzip=False):
    try:
        if install_setuptools.use_default:
            default_install_setuptools(py_executable, unzip)
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




##file site.py
SITE_PY = """
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
""".decode("base64").decode("zlib")

##file ez_setup.py
EZ_SETUP_PY = """
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
178BYnMUkw==
""".decode("base64").decode("zlib")

##file distribute_setup.py
DISTRIBUTE_SETUP_PY = """
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
""".decode("base64").decode("zlib")

##file activate.sh
ACTIVATE_SH = """
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
""".decode("base64").decode("zlib")

##file activate.fish
ACTIVATE_FISH = """
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
""".decode("base64").decode("zlib")

##file activate.csh
ACTIVATE_CSH = """
eJx9U11vmzAUffevOCVRu+UB9pws29Kl0iq1aVWllaZlcgxciiViItsQdb9+xiQp+dh4QOB7Pu49
XHqY59IgkwVhVRmLmFAZSrGRNkdgykonhFiqSCRW1sJSmJg8wCDT5QrucRCyHn6WFRKhVGmhKwVp
kUpNiS3emup3TY6XIn7DVNQyJUwlrgthJD6n/iCNv72uhCzCpFx9CRkThRQGKe08cWXJ9db/yh/u
pvzl9mn+PLnjj5P5D1yM8QmXlzBkSdXwZ0H/BBc0mEo5FE5qI2jKhclHOOvy9HD/OO/6YO1mX9vx
sY0H/tPIV0dtqel0V7iZvWyNg8XFcBA0ToEqVeqOdNUEQFvN41SumAv32VtJrakQNSmLWmgp4oJM
yDoBHgoydtoEAs47r5wHHnUal5vbJ8oOI+9wI86vb2d8Nrm/4Xy4RZ8R85E4uTZPB5EZPnTaaAGu
E59J8BE2J8XgrkbLeXMlVoQxznEYFYY8uFFdxsKQRx90Giwx9vSueHP1YNaUSFG4vTaErNSYuBOF
lXiVyXa9Sy3JdClEyK1dD6Nos9mEf8iKlOpmqSNTZnYjNEWiUYn2pKNB3ttcLJ3HmYYXy6Un76f7
r8rRsC1TpTJj7f19m5sUf/V3Ir+x/yjtLu8KjLX/CmN/AcVGUUo=
""".decode("base64").decode("zlib")

##file activate.bat
ACTIVATE_BAT = """
eJyFUkEKgzAQvAfyhz0YaL9QEWpRqlSjWGspFPZQTevFHOr/adQaU1GaUzI7Mzu7ZF89XhKkEJS8
qxaKMMsvboQ+LxxE44VICSW1gEa2UFaibqoS0iyJ0xw2lIA6nX5AHCu1jpRsv5KRjknkac9VLVug
sX9mtzxIeJDE/mg4OGp47qoLo3NHX2jsMB3AiDht5hryAUOEifoTdCXbSh7V0My2NMq/Xbh5MEjU
ZT63gpgNT9lKOJ/CtHsvT99re3pX303kydn4HeyOeAg5cjf2EW1D6HOPkg9NGKhu
""".decode("base64").decode("zlib")

##file deactivate.bat
DEACTIVATE_BAT = """
eJxzSE3OyFfIT0vj4spMU0hJTcvMS01RiPf3cYkP8wwKCXX0iQ8I8vcNCFHQ4FIAguLUEgWIgK0q
FlWqXJpcICVYpGzx2BAZ4uHv5+Hv6wq1BWINXBTdKriEKkI1DhW2QAfhttcxxANiFZCBbglQSJUL
i2dASrm4rFz9XLgAwJNbyQ==
""".decode("base64").decode("zlib")

##file distutils-init.py
DISTUTILS_INIT = """
eJytV92L4zYQf9dfMU0ottuse/TeFkKh3MvC0Ydy0IdlMVpbTtR1JCMpm+T++s5Y/pBs53oPZ1hQ
pPnSb34zo5WnVhsH2jLpV/Y2Li/cKKkOFoYN3Za6ErAdFtKC0g44vEvjzrwR6h1Oujo3YgdWw0VA
yRWcLUo6cBpqqSpwRwHWVY18ZRB9W3jq3HDlfoIvqK7NG2gF7a297VANvZ3O1sGrQI/eDe5yB0ZY
WQkLUpHxhVX09NDe3FGr31BL1lJUD9f8ln+FShpROm1ujOFS8ZOAPUKRt9wd836Hjqw7O9nYgvYD
iX+1VOlMPPXQ5EVRy0YURbaDZDSQZEzWo7rS5kSLNHaQwX4RRLrQGe1nj92Fh1zltEhHDDZfEO0g
O6MraHn5xg8IpYOfLfC2FdxYShLC64EES4A0uuROYhq49Zs368RpMvTHJmOiscKHUXRXKIpcKiuM
Sz/sYHa7TkxcRYkkEhN8HZaxKCJXFFJJh+baW5JluRG8SjM20JHEA9qWWtXywBjbbvF2rjzC61k2
VSGuDibTUGlhVeLgTekLHPEP73wQrrscUsUGrPCGjkTCC1JXXyw8EJWP3FSUZY8IiSCCRp97dnfO
RUUx5a0RtbxSzLX/3XBXYxIpyQka/fh74pGrjQ5QzUt9OnFV5dMV+otOG5gQjctxozNTNtzaSSiN
JHqu0FeJmsqRN/KrKHRLGbaQWtHUgRB9FDfu5giN4eZWIDqWCv8vrcTjrNZgRXQPzy+RmGjQpLRI
EKz0UqQLlR28ciusM8jn7PtcLPZy2zbSDeyyos0iO+ybBgPyRvSk/CEFm8IndQebz8iXTRbbjhDP
5xh7iJfBrKd/Nenjj6Jvgp2B+W7AnP102BXH5IZWPV3tI2MUOvXowpdS12IIXhLLP0lKyeuZrpEv
pFhPqHg3JFTd1cceVp0EsPgGU0wFO2u4iyYRoFYfEm9kG/RZcUUBm87t9mFtx9iCtC9kx4Rt4R8a
OdgzSt40vtyFecAZZ8BfCOhCrC8djMGPFaz2Vlt5TSZCk053+37wbLDLRXfZ+F45NtdVpVWdudSC
xgODI8EsiLoTl5aO0lhoigX7GHZDHAY4LxoMIu1gXPYPksmFquxF4uRKZhEnKzXu82HESb+LlNQz
Fh/RvFJVuhK+Ee5slBdj30FcRGdJ5rhKxtkyKxWcGoV/WOCYKqkNDYJ5fNQVx3g400tpJBS2FSU+
Tco9ss8nZ08dtscGQfSby87b73fOw+4UgrEMNnY6uMzYvSDxPVPpsij6+l0/ZPfuH0Iz010giY34
HpL0ZLyLJB4ukaQRU+GwptO7yIZCQE33B0K9iCqO6X+AR4n7wAeH68DPkJzpTsD3x+/cj9LIVHC2
An1wmv7CzWHoqR02vb0VL73siP+3nkX0YbQ0l9f6WDyOm24cj3rxO2MMip6kpcu6VCefn/789PR3
0v0fg21sFIp70rj9PCi8YDRDXFucym/43qN+iENh1Jy/dIIIqF3OIkDvBMsdx+huWv8Kz73vl8g5
WQ3JOGqwu3lb4dfKKbvLigXDQsb8B/xt39Q=
""".decode("base64").decode("zlib")

##file distutils.cfg
DISTUTILS_CFG = """
eJxNj00KwkAMhfc9xYNuxe4Ft57AjYiUtDO1wXSmNJnK3N5pdSEEAu8nH6lxHVlRhtDHMPATA4uH
xJ4EFmGbvfJiicSHFRzUSISMY6hq3GLCRLnIvSTnEefN0FIjw5tF0Hkk9Q5dRunBsVoyFi24aaLg
9FDOlL0FPGluf4QjcInLlxd6f6rqkgPu/5nHLg0cXCscXoozRrP51DRT3j9QNl99AP53T2Q=
""".decode("base64").decode("zlib")

##file activate_this.py
ACTIVATE_THIS = """
eJyNUlGL2zAMfvevEBlHEujSsXsL9GGDvW1jD3sZpQQ3Ua7aJXawnbT595Ocpe0dO5ghseVP+vRJ
VpIkn2cYPZknwAvWLXWYhRP5Sk4baKgOWRWNqtpdgTyH2Y5wpq5Tug406YAgKEzkwqg7NBPwR86a
Hk0olPopaK0NHJHzYQPnE5rI0o8+yBUwiBfyQcT8mMPJGiAT0A0O+b8BY4MKJ7zPcSSzHaKrSpJE
qeDmUgGvVbPCS41DgO+6xy/OWbfAThMn/OQ9ukDWRCSLiKzk1yrLjWapq6NnvHUoHXQ4bYPdrsVX
4lQMc/q6ZW975nmSK+oH6wL42a9H65U6aha342Mh0UVDzrD87C1bH73s16R5zsStkBZDp0NrXQ+7
HaRnMo8f06UBnljKoOtn/YT+LtdvSyaT/BtIv9KR60nF9f3qmuYKO4//T9ItJMsjPfgUHqKwCZ3n
xu/Lx8M/UvCLTxW7VULHxB1PRRbrYfvWNY5S8it008jOjcleaMqVBDnUXcWULV2YK9JEQ92OfC96
1Tv4ZicZZZ7GpuEpZbbeQ7DxquVx5hdqoyFSSmXwfC90f1Dc7hjFs/tK99I0fpkI8zSLy4tSy+sI
3vMWehjQNJmE5VePlZbL61nzX3S93ZcfDqznnkb9AZ3GWJU=
""".decode("base64").decode("zlib")

if __name__ == '__main__':
    main()

# pyutilib.virtualenv: ignoring comment
## Copy python.exe.manifest
## Monkeypatch distutils.sysconfig