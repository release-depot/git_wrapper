# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../git_wrapper'))



# -- Project information -----------------------------------------------------

project = 'git_wrapper'
copyright = '2021, Jason Joyce, Julie Pichon'
author = 'Jason Joyce, Julie Pichon'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
              'sphinx.ext.napoleon', 'myst_parser']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ['.rst', '.md']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Custom tooling ----------------------------------------------------------
import os
import subprocess

def setup(app):
    app.connect('builder-inited', build_changelog)

def build_changelog(app):
    docs_dir = os.getcwd()
    os.chdir('../')
    root_dir = os.getcwd()
    cmd = ['bash', f"{root_dir}/tooling/build_changelog", root_dir]
    change_proc = subprocess.run(cmd, capture_output=True, text=True)
    print(f"change stderr returns: {change_proc.stderr}")
    print(f"change stdout returns: {change_proc.stdout}")
    os.chdir(docs_dir)
