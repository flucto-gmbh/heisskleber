"""Sphinx configuration."""


project = "glue"
author = "Felix Weiler"
copyright = f"2023, {author}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]
autodoc_mock_imports = ["RPi.GPIO", "picamera2", "smbus"]

# html_static_path = ["_static"]
html_theme = "sphinx_rtd_theme"
