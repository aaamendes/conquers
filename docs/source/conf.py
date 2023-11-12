# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'conquers'
copyright = '2023, Albert Johannes Mendes'
author = 'Albert Johannes Mendes'
release = '0.1 (beta)'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo'
]

todo_include_todos = True

templates_path = ['_templates']
exclude_patterns = ['_build', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_logo = "https://cdn.amendes.me/conquers/logo.svg"
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# medecaj css
html_css_files = [
    'css/medecaj.css'
]
