#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://wwoods.github.io/2016/06/09/easy-sphinx-documentation-without-the-boilerplate/
# was immensely helpful *and should be the fucking out-of-the-box default experience* when
# turning on autodoc and autosummary

# http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
# for API docstring formatting

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert( 0, os.path.abspath( '..' ) )

import gwn.phone

language = None

project = gwn.phone.__title__
copyright = gwn.phone.__copyright__
author = gwn.phone.__author__
version = gwn.phone.__version__
release = version

templates_path = [ '_templates' ]
source_suffix = '.rst'
master_doc = project

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [ '_templates' ]

pygments_style = 'sphinx'
todo_include_todos = False


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon'
]

# the class description is both the class's docstring and its
# __init__'s docstring together
# one and not the other are 'class' and 'init'
autoclass_content = 'class'
# alphabetical is the default
# groupwise is by member type
# bysource is by source order
autodoc_member_order = 'bysource'
autodoc_default_flags = [
    'members', # include non-private members
    'undoc-members', # include members without a docstring
    #'private-members', # include _private and __private
    #'special-members', # include __special__ members
    #'inherited-members', # include members inherited from the base class
    'show-inheritance', # include the inheritance hierarchy of a class
]
# a list of modules to be mocked up, such as to prevent import errors if
# runtime dependencies cannot be met at build time
autodoc_mock_imports = [
    'gwn.helpers',
    'gwn.helpers.dbus',
    'gwn.helpers.dbus.dbuscast',
    'gwn.helpers.logger',
    'gwn.helpers.logger.logger',
    'dbus',
    'dbus.mainloop.glib',
    'dbus.mainloop.glib.DBusGMainLoop',
    'dbus.service',
    'gi.repository',
    'gi.repository.GObject',
    'systemd.journal.JournalHandler'
]

autosummary_generate = True

napoleon_numpy_docstring = False  # Force consistency, leave only Google
napoleon_use_rtype = False    # More legible



# -- Options for HTML output ----------------------------------------------

#html_theme = 'bizstyle'
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.    For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

#html_static_path = ['_static']

