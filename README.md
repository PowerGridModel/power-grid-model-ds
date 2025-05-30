<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

[![PyPI version](https://badge.fury.io/py/power-grid-model-ds.svg?no-cache)](https://badge.fury.io/py/power-grid-model-ds)
[![License: MIT](https://img.shields.io/badge/License-MPL2.0-informational.svg)](https://github.com/PowerGridModel/power-grid-model-ds/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/power-grid-model-ds)](https://pepy.tech/project/power-grid-model-ds)
[![Downloads](https://static.pepy.tech/badge/power-grid-model-ds/month)](https://pepy.tech/project/power-grid-model-ds)

[![CI Build](https://github.com/PowerGridModel/power-grid-model-ds/actions/workflows/ci.yml/badge.svg)](https://github.com/PowerGridModel/power-grid-model-ds/actions/workflows/ci.yml)
[![docs](https://readthedocs.org/projects/power-grid-model-ds/badge/)](https://power-grid-model-ds.readthedocs.io/en/stable/)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=PowerGridModel_power-grid-model-ds&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=PowerGridModel_power-grid-model-ds)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=PowerGridModel_power-grid-model-ds&metric=coverage)](https://sonarcloud.io/summary/new_code?id=PowerGridModel_power-grid-model-ds)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=PowerGridModel_power-grid-model-ds&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=PowerGridModel_power-grid-model-ds)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=PowerGridModel_power-grid-model-ds&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=PowerGridModel_power-grid-model-ds)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=PowerGridModel_power-grid-model-ds&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=PowerGridModel_power-grid-model-ds)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=PowerGridModel_power-grid-model-ds&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=PowerGridModel_power-grid-model-ds)

[![Nightly build](https://github.com/PowerGridModel/power-grid-model-ds/actions/workflows/nightly.yml/badge.svg)](https://github.com/PowerGridModel/power-grid-model-ds/actions/workflows/nightly.yml)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14825565.svg)](https://zenodo.org/record/14825565)

[![Power Grid Model logo](https://github.com/PowerGridModel/.github/blob/main/artwork/svg/color.svg)](#)

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
- Visualization for easy exploration and debugging.

<img width="40%" alt="Grid Visualisation" src="docs/_static/grid-force-directed.png" />

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

## Citations

If you are using Power Grid Model DS in your research work, please consider citing our library using the following references.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14825565.svg)](https://zenodo.org/record/14825565)

```bibtex
@software{Schouten_PowerGridModel_power-grid-model-ds,
  author = {Schouten, Jaap and Baaijen, Thijs and Koppen, Vincent and van der Voort, Sven and {Contributors to the LF Energy project Power Grid Model}},
  doi = {10.5281/zenodo.14825565},
  license = {MPL-2.0},
  title = {{PowerGridModel/power-grid-model-ds}},
  url = {https://github.com/PowerGridModel/power-grid-model-ds}
}
@software{Xiang_PowerGridModel_power-grid-model,
  author = {Xiang, Yu and Salemink, Peter and van Westering, Werner and Bharambe, Nitish and Govers, Martinus G.H. and van den Bogaard, Jonas and Stoeller, Bram and Wang, Zhen and Guo, Jerry Jinfeng and Figueroa Manrique, Santiago and Jagutis, Laurynas and Wang, Chenguang and van Raalte, Marc and {Contributors to the LF Energy project Power Grid Model}},
  doi = {10.5281/zenodo.8054429},
  license = {MPL-2.0},
  title = {{PowerGridModel/power-grid-model}},
  url = {https://github.com/PowerGridModel/power-grid-model}
}
@inproceedings{Xiang2023,
  author = {Xiang, Yu and Salemink, Peter and Stoeller, Bram and Bharambe, Nitish and van Westering, Werner},
  booktitle={27th International Conference on Electricity Distribution (CIRED 2023)},
  title={Power grid model: a high-performance distribution grid calculation library},
  year={2023},
  volume={2023},
  number={},
  pages={1089-1093},
  keywords={},
  doi={10.1049/icp.2023.0633}
}
```

## Contact

Please read [SUPPORT](https://github.com/PowerGridModel/.github/blob/main/SUPPORT.md) for how to connect and get into contact with the Power Grid Model project.
