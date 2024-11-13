"""Sphinx configuration."""

from __future__ import annotations

import importlib.metadata
from typing import Any

project = "Heisskleber"
author = "Felix Weiler-Detjen"
copyright = "2023, Flucto GmbH"

version = release = importlib.metadata.version("heisskleber")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

autodoc_typehints = "description"  # or 'signature' or 'both'

autodoc_type_aliases = {
    "T": "heisskleber.core.T",
    "T_co": "heisskleber.core.T_co",
    "T_contra": "heisskleber.core.T_contra",
}

# If you're using typing.TypeVar in your code:
nitpicky = True
nitpick_ignore = [
    ("py:class", "T"),
    ("py:class", "T_co"),
    ("py:class", "T_contra"),
    ("py:data", "typing.Any"),
]
autodoc_default_options: dict[str, Any] = {
    "special-members": "__call__",
}

source_suffix = [".rst", ".md"]

exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"

html_theme_options: dict[str, Any] = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/flucto-gmbh/heisskleber",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": "https://github.com/flucto-gmbh/heisskleber",
    "source_branch": "main",
    "source_directory": "docs/",
}
nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]

always_document_param_types = True
