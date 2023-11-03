"""Sphinx configuration."""
project = "Heisskleber"
author = "Felix Weiler"
copyright = "2023, Felix Weiler"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]  # , "autodoc2"
# autodoc2_packages = ["../heisskleber"]
autodoc_typehints = "description"
html_theme = "furo"
