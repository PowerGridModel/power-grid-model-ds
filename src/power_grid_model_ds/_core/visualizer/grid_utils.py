from dataclasses import dataclass
from typing import Type

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.constants import empty
from power_grid_model_ds._core.model.dtypes.typing import NDArray3


def extend_grid_dynamically(base_grid_class: Type[Grid], extra_dataset: dict[str, np.ndarray]) -> Type[Grid]:
    """Add extra attributes to the grid's component arrays based on the provided dataset,
    and return a new Grid class with the extended schema."""
    grid_annotations = {}
    for grid_attr, base_class in base_grid_class.__annotations__.items():
        if issubclass(base_class, FancyArray) and grid_attr in ComponentType and grid_attr in extra_dataset:
            class_dict = _get_class_dict(base_class, grid_attr, extra_dataset)
            grid_annotations[grid_attr] = type(f"Dynamic{base_class.__name__}", (base_class,), class_dict)
        else:
            grid_annotations[grid_attr] = base_class

    DynamicGridClass = type("DynamicDynamicGrid", (Grid,), {"__annotations__": grid_annotations})

    return dataclass(DynamicGridClass)


def _get_class_dict(base_class: Type[FancyArray], grid_attr: str, extra_dataset: dict):
    """Get the class dictionary for the dynamically created array class, including new annotations and defaults."""
    extra_array_dtype = extra_dataset[ComponentType(grid_attr)].dtype
    if not extra_array_dtype.fields:
        raise ValueError(f"Expected a structure numpy array got {extra_array_dtype}")

    extra_array_types = {}
    for attr in extra_array_dtype.fields:
        if attr in base_class.__annotations__:
            continue

        dtype = extra_array_dtype.fields[attr][0]
        if dtype.subdtype is not None and dtype.subdtype[1] == (3,):
            extra_array_types[attr] = NDArray3[dtype.subdtype[0]]
        else:
            extra_array_types[attr] = NDArray[dtype]

    return {
        "__annotations__": {**getattr(base_class, "__annotations__", {}), **extra_array_types},
        "_defaults": getattr(base_class, "_defaults", {}),
    }


def dynamic_grid_obj_from_grid(dynamic_grid_class: Type[Grid], grid: Grid):
    """Create new object of dynamic_grid_class type using data from grid object."""
    dynamic_grid_obj = dynamic_grid_class.empty()
    for grid_attr in grid.__annotations__:
        array = getattr(grid, grid_attr)
        if not isinstance(array, FancyArray):
            continue

        dynamic_grid_array = getattr(dynamic_grid_obj, grid_attr).__class__.zeros(array.shape)
        for array_attr in array.columns:
            setattr(dynamic_grid_array, array_attr, getattr(array, array_attr))
        setattr(dynamic_grid_obj, grid_attr, dynamic_grid_array)

    return dynamic_grid_obj


def get_attr_data_from_dataset(dataset: dict, comp_type: ComponentType, attr: str, pgm_id: int) -> np.ndarray | None:
    """Find the data for the given component type, attribute, and pgm_id from a batch dataset across all scenarios.
    Only returns if there is valid data (not all empty values) for the given pgm_id for all scenarios of dataset."""
    # Find dataset type, empty value, and column data for the given group and column
    id_data = dataset[comp_type]["id"]
    column_data = dataset[comp_type][attr]

    # No batch data found in dataset for this column or id
    element_idx = np.nonzero(id_data[0] == pgm_id)[0][0]
    if np.any(id_data[:, element_idx] != pgm_id) and np.any(column_data == empty(column_data.dtype)):
        return None

    # Find the index of the selected element corresponding to pgm_id
    return column_data[:, element_idx]
