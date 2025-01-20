<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Build Guide

This document explains how you can build this library from source.

## Building the Library from source

Example Setup for Ubuntu 22.04 (in WSL or physical/virtual machine)

It is recommended to create a virtual environment. 

```shell
git clone https://github.com/PowerGridModel/power-grid-model-ds.git
cd power-grid-model-ds
python3.11 -m venv .venv
source ./.venv/bin/activate
```

Install from source in develop mode.

```
pip install -e .[dev]
```

Then you can run the tests.

```
pytest
```

## Building Documentation

To build the documentation locally execute the following commands
```
pip install -e .[docs]

# build the docs
cd docs
make clean #clean the build folder
make html
```
This will generate a webpage in the `build` folder with an `index.html` file. Open this file in a browser to view the documentation.
