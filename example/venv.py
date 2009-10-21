
def configure(installer):
    installer.default_dirname = 'venv'
    #
    # Add repositories
    #
    installer.add_repository('virtualenv', pypi='virtualenv')
    installer.add_repository('nose', pypi='nose')
    #
    # Return the modified installer
    #
    return installer

