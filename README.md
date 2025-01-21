<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

[![](https://github.com/PowerGridModel/.github/blob/main/artwork/svg/color.svg)](#)

# Power Grid Model Data Science (DS)

The Power Grid Model DS project extends the capabilities of the `power-grid-model` calculation core with a modelling and simulation interface. This is aimed at building data science software applications related to or using the power-grid-model project. It defines a `Grid` dataclass which manages the consistency of the complete network.

Some highlighted features:

- Using a model definition that corresponds to the power-grid-model, through
  which it is easy to do efficient grid calculations.
- The extended numpy model provides features which make development more
  pleasant and easy.
- Using the graph representation of the network, graph algorithms in rustworkx
  can be used to analyze the network.
- An interface to model network mutations which is useful in
  simulation use-cases.

See the [power-grid-model-ds documentation](https://power-grid-model-ds.readthedocs.io/en/stable/) for more information.

## Installation

### Pip

```
pip install power-grid-model-ds
```
## License

This project is licensed under the Mozilla Public License, version 2.0 - see [LICENSE](https://github.com/PowerGridModel/power-grid-model-ds/blob/main/LICENSE) for details.

## Licenses third-party libraries

This project includes third-party libraries, 
which are licensed under their own respective Open-Source licenses.
SPDX-License-Identifier headers are used to show which license is applicable. 
The concerning license files can be found in the [LICENSES](https://github.com/PowerGridModel/power-grid-model-ds/tree/main/LICENSES) directory.

## Contributing

Please read [CODE_OF_CONDUCT](https://github.com/PowerGridModel/.github/blob/main/CODE_OF_CONDUCT.md) and [CONTRIBUTING](https://github.com/PowerGridModel/.github/blob/main/CONTRIBUTING.md) for details on the process 
for submitting pull requests to us.

## Contact

Please read [SUPPORT](https://github.com/PowerGridModel/.github/blob/main/SUPPORT.md) for how to connect and get into contact with the Power Grid Model project.

