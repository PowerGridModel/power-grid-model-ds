# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# pylint: skip-file

project = "power-grid-model-ds"
copyright = "Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>"
author = "Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # allow for google style docstrings
]
templates_path = ["_templates"]
exclude_patterns: list[str] = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".txt": "markdown",
}

# -- sphinx.ext.intersphinx config -------------------------------------------
# For linking to power-grid-model's documentation.
intersphinx_mapping = {"power-grid-model": ("https://power-grid-model.readthedocs.io/en/stable/", None)}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for autodoc ---------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "member-order": "bysource",
    "show-inheritance": True,
    "special-members": "__init__",
    "exclude-members": "__weakref__",
}
