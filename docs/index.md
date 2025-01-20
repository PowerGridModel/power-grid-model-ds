<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Power Grid Model DS

```{image} https://github.com/PowerGridModel/.github/raw/main/artwork/svg/color.svg
:alt: pgm_logo
:width: 300px
:align: right
```

The Power Grid Model DS project extends the capabilities of the [power-grid-model](https://github.com/PowerGridModel/power-grid-model) calculation engine with a modelling and simulation interface. This is aimed at building data science software applications related to or using the power-grid-model project, such as network analyses and simulations. It defines a ``Grid`` dataclass which manages the consistency of the complete network and allows for extensions of the Power Grid Model datastructure.

```{note}
Do you wish to be updated on the latest news and releases? Subscribe to the Power Grid Model mailing list by sending an (empty) email to: powergridmodel+subscribe@lists.lfenergy.org
```

## Install from PyPI

You can directly install the package from PyPI.

```
pip install power-grid-model-ds
```

## Install from Conda

If you are using `conda`, you can directly install the package from `conda-forge` channel.

```
conda install -c conda-forge power-grid-model-ds
```


```{toctree}
:caption: "User Manual"
:maxdepth: 2

quick_start
model_structure
model_interface
examples/index
advanced_documentation/index
```

```{toctree} 
:caption: API Reference
:maxdepth: 2

api_reference/power_grid_model_ds
```

```{toctree}
:caption: "Contribution"
:maxdepth: 2
contribution/CODE_OF_CONDUCT.md
contribution/CONTRIBUTING.md
contribution/GOVERNANCE.md
```

```{toctree}
:caption: "Release and Support"
:maxdepth: 2
release_and_support/RELEASE.md
release_and_support/SUPPORT.md
release_and_support/SECURITY.md
release_and_support/CITATION.md
```
