
import os
from setuptools import setup, find_packages
import sys

sys.path.insert( 0, os.path.abspath( '.' ) )
import gwn.phone

setup(
    name = gwn.phone.__title__,
    version = gwn.phone.__version__,
    description = gwn.phone.__description__,
    author = gwn.phone.__author__,
    author_email = gwn.phone.__author_email__,
    license = gwn.phone.__copyright__,
    packages = find_packages( exclude = [ 'sphinx', 'tests' ] ),
    namespace_packages = [ gwn.phone.__namespace__ ],
    entry_points = {
        'console_scripts': [
            'gwn-phone = gwn.phone.cli:main',
            'gwn-phone-conf-watch = gwn.phone.conf_watch:main',
        ],
    }
)

