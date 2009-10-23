#
# A Python module used to build a virtualenv bootstrap script that uses 
# *.ini config files to define the packages that are installed.
#
# Note that the configure() function is not needed, since the ConfigInstaller
# config file logic configures the installer.
#

import ConfigParser

class ConfigInstaller(Installer):
    """
    This class extends the logic in the Installer class to add a
    command-line option and support initialization with INI config files.
    """
       
    def modify_parser(self, parser):
        """
        Extend the parser to include the --config option.
        """    
        Installer.modify_parser(self, parser)

        parser.add_option('--config',
            help='Add INI config files that specify the packages used in this installation.',
            action='append',
            dest='config_files',
            default=[])

    def adjust_options(self, options, args): 
        """
        Process the list of INI config files.
        """
        Installer.adjust_options(self, options, args)

        for file in options.config_files:
            self.read_config_file(file)

    def read_config_file(self, file):
        """
        Read a config file.
        """
        parser = ConfigParser.ConfigParser()
        if not file in parser.read(file):
            raise IOError, "Error while parsing file %s." % file 
        for option, value in parser.items('installer'):
            setattr(self, option, value)
        for option, value in parser.items('dos_cmd'):
            self.add_dos_cmd(option)
        for sec in parser.sections():
            if sec in ['installer', 'dos_cmd']:
                continue
            if sec.startswith('auxdir_'):
                auxdir = sec[7:]
                for option, value in parser.items(sec):
                    self.add_auxdir(auxdir, option, value)
            else:
                options = {}
                for option, value in parser.items(sec):
                    options[option]=value
                self.add_repository(sec, **options)
               

def create_installer():
    """
    Allocate a ConfigInstaller class instead of the Installer
    class.
    """
    return ConfigInstaller()

