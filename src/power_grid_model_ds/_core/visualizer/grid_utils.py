from dataclasses import dataclass
from typing import Type

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays.base.array import FancyArray


def extend_grid_dynamically(base_grid, extra_dataset: dict[str, np.ndarray]) -> Type[Grid]:
    """Add extra attributes to the grid's component arrays based on the provided dataset,
    and return a new Grid class with the extended schema."""
    grid_annotations = {}
    for grid_attr in base_grid.__annotations__:
        base_class = getattr(base_grid, grid_attr).__class__
        if issubclass(base_class, FancyArray) and grid_attr in ComponentType and grid_attr in extra_dataset:
            class_dict = _get_class_dict(base_class, grid_attr, extra_dataset)
            grid_annotations[grid_attr] = type(f"Dynamic{base_class.__name__}", (base_class,), class_dict)
        else:
            grid_annotations[grid_attr] = base_class

    DynamicGridClass = type("DynamicDynamicGrid", (Grid,), {"__annotations__": grid_annotations})

    return dataclass(DynamicGridClass)


def _get_class_dict(base_class: FancyArray, grid_attr: str, extra_dataset: dict):
    """Get the class dictionary for the dynamically created array class, including new annotations and defaults."""
    extra_array_dtype = extra_dataset[ComponentType(grid_attr)].dtype
    if not extra_array_dtype.fields:
        raise ValueError(f"Expected a structure numpy array got {extra_array_dtype}")

    extra_array_defaults = {}
    extra_array_types = {}
    for attr in extra_array_dtype.fields:
        if attr in base_class.__annotations__:
            continue

        dtype = extra_array_dtype.fields[attr][0]
        # For 3 phase arrays, the dtype will be something like (f8, (3,))
        scalar_dtype = dtype.subdtype[0] if dtype.subdtype is not None else dtype

        # Set defaults
        if np.issubdtype(scalar_dtype, np.floating):
            extra_array_defaults[attr] = np.nan
        elif np.issubdtype(scalar_dtype, np.integer):
            extra_array_defaults[attr] = np.iinfo(scalar_dtype).min
        else:
            raise ValueError(f"Unsupported dtype {scalar_dtype} for column {attr} in component {grid_attr}")

        extra_array_types[attr] = NDArray[scalar_dtype]

    return {
        "__annotations__": {**getattr(base_class, "__annotations__", {}), **extra_array_types},
        "_defaults": {**getattr(base_class, "_defaults", {}), **extra_array_defaults},
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
    """Find the data for the given component type, attribute, and pgm_id from the dataset."""
    # Find dataset type, empty value, and column data for the given group and column
    id_data = dataset[comp_type]["id"]
    column_data = dataset[comp_type][attr]

    # No batch data found in dataset for this column or id
    if np.issubdtype(column_data.dtype, np.floating):
        empty_val = np.nan
    elif np.issubdtype(column_data.dtype, np.integer):
        empty_val = np.iinfo(column_data.dtype).min
    else:
        raise ValueError(f"Unsupported dtype {column_data.dtype} for column {attr} in component {comp_type}")

    if np.all(column_data == empty_val) or pgm_id not in id_data:
        return None

    # Find the index of the selected element corresponding to pgm_id
    element_idx = np.nonzero(id_data[0] == pgm_id)[0][0]
    return column_data[:, element_idx]
