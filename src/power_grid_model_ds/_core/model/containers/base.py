# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Stores the FancyArrayContainer class"""

import dataclasses
import inspect
import logging
from dataclasses import dataclass
from typing import Type, TypeVar

import numpy as np

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.constants import EMPTY_ID

Self = TypeVar("Self", bound="FancyArrayContainer")


@dataclass
class FancyArrayContainer:
    """
    Base class for ArrayContainers.
    Contains general functionality that is nonspecific to the type of array being stored.
    """

    _id_counter: int

    @property
    def id_counter(self):
        """Returns the private _id_counter field (as read-only)"""
        return self._id_counter

    @classmethod
    def empty(cls: Type[Self]) -> Self:
        """Create an empty grid"""
        empty_fields = cls._get_empty_fields()
        return cls(**empty_fields)

    def all_arrays(self):
        """Returns all arrays in the container."""

        for field in dataclasses.fields(self):
            attribute = getattr(self, field.name)
            if isinstance(attribute, FancyArray):
                yield attribute

    @classmethod
    def find_array_field(cls, array_type: Type[FancyArray]) -> dataclasses.Field:
        """Find the Field that holds an array of type array_type.

        Args:
            array_type(type[FancyArray]): FancyArray subclass.

        Raises:
            TypeError: if no field with the given `array_type` is found or if multiple fields are found.

        Returns:
            a Field instance.
        """
        fields = [
            field
            for field in dataclasses.fields(cls)
            if inspect.isclass(field.type) and issubclass(field.type, array_type)
        ]
        if (nr_fields := len(fields)) != 1:
            raise TypeError(
                f"Expected to find 1 array with type '{array_type.__name__}' in {cls.__name__} ({nr_fields} found)"
            )
        return fields[0]

    @property
    def max_id(self) -> int:
        """Returns the max id across all arrays within the container."""
        max_per_array = [np.max(array.id) if array.size > 0 else 0 for array in self.all_arrays()]
        return int(max(max_per_array))

    def check_ids(self, check_between_arrays: bool = True, check_within_arrays: bool = True) -> None:
        """Checks for duplicate id values across all arrays in the container.

        Args:
            check_between_arrays(bool): whether to check for duplicate ids across arrays
            check_within_arrays(bool): whether to check for duplicate ids within each array

        Raises:
            ValueError: if duplicates are found.
        """

        id_arrays = [array for array in self.all_arrays() if hasattr(array, "id")]
        if not id_arrays:
            return  # no arrays to check

        duplicates_between_arrays = self._get_duplicates_between_arrays(
            id_arrays, check=check_between_arrays
        )  # if check_between_arrays else []
        arrays_with_duplicates = self._get_arrays_with_duplicates(id_arrays, check=check_within_arrays)

        if not any(duplicates_between_arrays) and not any(arrays_with_duplicates):
            return

        if any(duplicates_between_arrays):
            logging.warning(f"The following ids occur in multiple arrays: {duplicates_between_arrays}!")
        for array_class in arrays_with_duplicates:
            logging.warning(f"{array_class.__name__} contains duplicates!")

        raise ValueError(f"Duplicates found within {self.__class__.__name__}!")

    def append(self, array: FancyArray, check_max_id: bool = True) -> None:
        """Append the given asset_array to the corresponding field of ArrayContainer and generate ids.

        Args:
            array(FancyArray): the asset_array to be appended (e.g. a NodeArray instance).
            check_max_id(bool): whether to check max(array.id) with the id counter

        Returns:
            None
        """
        self._append(array=array, check_max_id=check_max_id)

    def attach_ids(self, array: FancyArray) -> FancyArray:
        """Generate and attach ids to the given FancyArray. Also updates _id_counter.

        Args:
            array(FancyArray): the array of which the id column is set.

        Returns:
            FancyArray: initial array with updated `id` column.
        """
        if not array.size:
            return array

        if (id_set := set(array.id)) != {array.get_empty_value("id")}:
            raise ValueError(f"Cannot attach ids to array that contains non-empty ids: {id_set}")

        start = self._id_counter + 1
        end = start + len(array)
        array.id = np.arange(start, end)
        self._id_counter = max(self._id_counter, end - 1)

        return array

    def search_for_id(self, record_id: int) -> list[FancyArray]:
        """Attempts to find a record across all id-arrays within the container.

        This method is only intended for debugging purposes since it is very inefficient.
        In normal circumstances you should use ``get`` or ``filter`` to find records within a specific array.

        Args:
            record_id(int): the id of the record to be found.

        Returns:
         list[FancyArray]:a list of arrays that contain the given record_id.
         Each array within the list contains all records with the given array.
        """

        logging.warning("Using search_for_id(). Make sure to use only while debugging!")

        arrays_with_record = []

        id_arrays = [array for array in self.all_arrays() if "id" in array.dtype.names]
        for id_array in id_arrays:
            matching_records = id_array.filter(id=record_id)
            if matching_records.size:
                arrays_with_record.append(matching_records)

        if arrays_with_record:
            return arrays_with_record
        raise RecordDoesNotExist(f"record id '{record_id}' not found in {self.__class__.__name__}")

    def _append(self, array: FancyArray, check_max_id: bool = True) -> None:
        """
        Append the given asset_array to the corresponding field of Grid and generate ids.
        Args:
            array: the asset_array to be appended (e.g. a KabelArray instance).
            check_max_id: whether to check max(array.id) with the id counter
        Returns: None.
        """
        if array.size == 0:
            return

        array_field = self.find_array_field(array.__class__)

        if hasattr(array, "id"):
            self._update_id_counter(array, check_max_id)

        # Add the given asset_array to the corresponding array in the Grid.
        array_attr = getattr(self, array_field.name)
        appended = fp.concatenate(array_attr, array)
        setattr(self, array_field.name, appended)

    @classmethod
    def _get_empty_fields(cls) -> dict:
        empty_fields = {}

        empty_fields.update(cls._get_empty_arrays())
        empty_fields.update({"_id_counter": 0})
        return empty_fields

    @classmethod
    def _get_empty_arrays(cls) -> dict:
        return {
            field.name: field.type()
            for field in dataclasses.fields(cls)
            if inspect.isclass(field.type) and issubclass(field.type, FancyArray)
        }

    def _update_id_counter(self, array, check_max_id: bool = True):
        if np.all(array.id == EMPTY_ID):
            array = self.attach_ids(array)
        elif np.any(array.id == EMPTY_ID):
            raise ValueError(f"Cannot append: array contains empty [{EMPTY_ID}] and non-empty ids.")
        elif check_max_id and self.id_counter > 0:
            # Only check for overlaps when array has prescribed (non-empty) IDs
            # Check if any incoming ID might overlap with existing IDs
            # This prevents overlaps since counter tracks the highest used ID
            new_min_id = np.min(array.id)
            if new_min_id <= self._id_counter:
                raise ValueError(
                    f"Cannot append: minimum id {new_min_id} is not greater than "
                    f"the current id counter {self._id_counter}"
                )

        new_max_id = np.max(array.id)
        # Update _id_counter
        self._id_counter = max(self._id_counter, new_max_id)

    @staticmethod
    def _get_duplicates_between_arrays(id_arrays: list[FancyArray], check: bool) -> np.ndarray:
        if not check:
            return np.array([])
        unique_ids_per_array = [np.unique(array.id) for array in id_arrays]

        all_ids = np.concatenate(unique_ids_per_array)

        unique_ids, counts = np.unique(all_ids, return_counts=True)
        duplicate_mask = counts > 1
        return unique_ids[duplicate_mask]

    @staticmethod
    def _get_arrays_with_duplicates(id_arrays: list[FancyArray], check: bool) -> list:
        arrays_with_duplicates: list[Type] = []
        if not check:
            return arrays_with_duplicates
        for id_array in id_arrays:
            duplicates: np.ndarray = id_array.check_ids(return_duplicates=True)
            if duplicates.size > 0:
                arrays_with_duplicates.append(id_arrays.__class__)
        return arrays_with_duplicates
