# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass, fields
from typing import Any

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType
from power_grid_model.data_types import BatchDataset

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.dtypes.typing import NDArray3


def extend_grid_dynamically(base_grid_class: type[Grid], extra_dataset: BatchDataset) -> type[Grid]:
    """Add extra attributes to the grid's component arrays based on the provided dataset,
    and return a new Grid class with the extended schema."""
    grid_annotations = {}
    for field in fields(base_grid_class):
        grid_attr = field.name
        base_class = field.type
        if (
            isinstance(base_class, type)
            and issubclass(base_class, FancyArray)
            and grid_attr in ComponentType
            and grid_attr in extra_dataset
        ):
            class_dict = _get_class_dict(base_class, grid_attr, extra_dataset)
            grid_annotations[grid_attr] = type(f"Dynamic{base_class.__name__}", (base_class,), class_dict)
        else:
            grid_annotations[grid_attr] = base_class

    DynamicGridClass = type("DynamicDynamicGrid", (base_grid_class,), {"__annotations__": grid_annotations})

    return dataclass(DynamicGridClass)


def _get_class_dict(base_class: type[FancyArray], grid_attr: str, extra_dataset: BatchDataset) -> dict[str, Any]:
    """Get the class dictionary for the dynamically created array class, including new annotations and defaults."""
    extra_array_dtype = extra_dataset[ComponentType(grid_attr)].dtype
    if not extra_array_dtype.fields:
        raise ValueError(f"Expected a structure numpy array got {extra_array_dtype}")

    extra_array_types: dict[str, Any] = {}
    for attr in extra_array_dtype.fields:
        if attr in base_class.__annotations__:
            continue

        dtype = extra_array_dtype.fields[attr][0]
        if dtype.subdtype is not None and dtype.subdtype[1] == (3,):
            extra_array_types[attr] = NDArray3[dtype.subdtype[0]]  # type: ignore
        else:
            extra_array_types[attr] = NDArray[dtype]  # type: ignore

    return {
        "__annotations__": {**getattr(base_class, "__annotations__", {}), **extra_array_types},
        "_defaults": getattr(base_class, "_defaults", {}),
    }


def dynamic_grid_obj_from_grid(dynamic_grid_class: type[Grid], grid: Grid):
    """Create new object of dynamic_grid_class type using data from grid object."""
    dynamic_grid_obj = dynamic_grid_class.empty()

    for field in fields(grid.__class__):
        grid_attr = field.name
        array = getattr(grid, grid_attr)
        if not isinstance(array, FancyArray):
            continue

        dynamic_grid_array = getattr(dynamic_grid_obj, grid_attr).__class__.empty(array.shape)
        for array_attr in array.columns:
            setattr(dynamic_grid_array, array_attr, getattr(array, array_attr))
        setattr(dynamic_grid_obj, grid_attr, dynamic_grid_array)

    return dynamic_grid_obj


def get_attr_data_from_dataset(
    dataset: BatchDataset,
    comp_type: ComponentType,
    attr: str,
    pgm_id: int,
    grid: Grid | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract an attribute for one component across batch scenarios.

    When a base grid is supplied, missing attribute values are replaced
    with the corresponding base-grid value.

    Scenarios without the requested component are excluded.
    """
    component_data = dataset[comp_type]
    array_mask = component_data["id"] == pgm_id

    scenario_indices, _ = np.nonzero(array_mask)
    match_data = component_data[attr][array_mask].copy()

    if grid is None:
        return scenario_indices, match_data

    base_component = getattr(grid, comp_type.value)
    base_matches = base_component.id == pgm_id

    if not np.any(base_matches) or attr not in base_component.columns:
        return scenario_indices, match_data

    base_value = getattr(base_component, attr)[base_matches][0]
    empty_value = empty(component_data.dtype.fields[attr][0])

    if isinstance(empty_value, float) and np.isnan(empty_value):
        missing_mask = np.isnan(match_data)
    else:
        missing_mask = match_data == empty_value

    match_data = np.where(missing_mask, base_value, match_data)

    return scenario_indices, match_data
