"""Sphinx configuration."""
project = "Heisskleber"
author = "Felix Weiler"
copyright = "2023, Felix Weiler"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
