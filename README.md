# Heisskleber

[![PyPI](https://img.shields.io/pypi/v/heisskleber.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/heisskleber)][pypi status]
[![License](https://img.shields.io/pypi/l/heisskleber)][license]

[![Read the documentation at https://heisskleber.readthedocs.io/](https://img.shields.io/readthedocs/heisskleber/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/flucto-gmbh/heisskleber/workflows/Tests/badge.svg)][tests]
[![codecov](https://codecov.io/gh/flucto-gmbh/heisskleber/graph/badge.svg?token=U5TH74MOLO)](https://codecov.io/gh/flucto-gmbh/heisskleber)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Format](https://img.shields.io/badge/code%20style-ruff-purple.svg)][ruff]

[pypi status]: https://pypi.org/project/heisskleber/
[read the docs]: https://heisskleber.readthedocs.io/
[tests]: https://github.com/flucto-gmbh/heisskleber/actions?workflow=Tests
[pre-commit]: https://github.com/pre-commit/pre-commit
[ruff]: https://astral.sh/ruff

🇩🇪Heißkleber _m_: "hot glue".

Heisskleber is a versatile library designed to seamlessly "glue" together various data producers and consumers across a multitude of protocols including zmq, mqtt, udp, serial, influxdb, and cmdline. With the ambition to extend into REST API interactions and file operations, Heisskleber offers both synchronous and asynchronous interfaces to cater to a wide range of IoT connectivity needs.

## Features

- Multiple Protocol Support: Easy integration with zmq, mqtt, udp, serial, influxdb, and cmdline. Future plans include REST API and file operations.
- Custom Data Handling: Customizable "unpack" and "pack" functions allow for the translation of any data format (e.g., ascii encoded, comma-separated messages from a serial bus) into dictionaries for easy manipulation and transmission.
- Synchronous & Asynchronous Versions: Cater to different programming needs and scenarios with both sync and async interfaces.
- Extensible: Designed for easy extension with additional protocols and data handling functions.

## Installation

You can install _Heisskleber_ via [pip] from [PyPI]:

```console
$ pip install heisskleber
```

Configuration files for zmq, mqtt and other heisskleber related settings should be placed in the user's config directory, usually `$HOME/.config`. Config file templates can be found in the `config`
directory of the package.

## Quick Start

Here's a simple example to demonstrate how Heisskleber can be used to connect a zmq source to an mqtt sink:

```python
"""
A simple forwarder that takes messages from
"""

from heisskleber.serial import SerialSubscriber, SerialConf
from heisskleber.mqtt import MqttPublisher, MqttConf

source = SerialSubscriber(config=SerialConf(port="/dev/ACM0"))
sink = MqttPublisher(config=MqttConf(host="127.0.0.1", port=1883, user="", password=""))

while True:
    topic, data = source.receive()
    sink.send(data, topic="/hostname/" + topic)
```

All sources and sinks come with customizable "unpack" and "pack" functions, making it simple to work with various data formats.

It is also possible to do configuration via yaml files, placed at `$HOME/.config/heisskleber` and named according to the protocol in question.

See the [documentation][read the docs] for detailed usage.

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
