# Heisskleber

[![PyPI](https://img.shields.io/pypi/v/heisskleber.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/heisskleber.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/heisskleber)][pypi status]
[![License](https://img.shields.io/pypi/l/heisskleber)][license]

[![Read the documentation at https://heisskleber.readthedocs.io/](https://img.shields.io/readthedocs/heisskleber/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/flucto-gmbh/heisskleber/workflows/Tests/badge.svg)][tests]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/heisskleber/
[read the docs]: https://heisskleber.readthedocs.io/
[tests]: https://github.com/flucto-gmbh/heisskleber/actions?workflow=Tests
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _Heisskleber_ via [pip] from [PyPI]:

```console
$ pip install heisskleber
```

Configuration files for zmq, mqtt and other heisskleber related settings should be placed in the user's config directory, usually `$HOME/.config`. Config file templates can be found in the `config`
directory of the package.

## Development

1. Install poetry

```
curl -sSL https://install.python-poetry.org | python3 -
```

2. clone repository

```
git clone https://github.com/flucto-gmbh/heisskleber.git
cd heisskleber
```

3. setup

```
make install
```

## License

Distributed under the terms of the [MIT license][license],
_Heisskleber_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

[pip]: https://pip.pypa.io/
[file an issue]: https://github.com/flucto-gmbh/heisskleber/issues
[pypi]: https://pypi.org/

<!-- github-only -->

[license]: https://github.com/flucto-gmbh/heisskleber/blob/main/LICENSE
[contributor guide]: https://github.com/flucto-gmbh/heisskleber/blob/main/CONTRIBUTING.md
[command-line reference]: https://heisskleber.readthedocs.io/en/latest/usage.html
