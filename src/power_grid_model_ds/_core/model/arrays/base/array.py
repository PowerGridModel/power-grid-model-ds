# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC
from collections import namedtuple
from copy import copy
from functools import lru_cache
from typing import Any, Iterable, Literal, Type, TypeVar

import numpy as np
from numpy.typing import ArrayLike, NDArray

from power_grid_model_ds._core.model.arrays.base._build import build_array
from power_grid_model_ds._core.model.arrays.base._filters import apply_exclude, apply_filter, apply_get, get_filter_mask
from power_grid_model_ds._core.model.arrays.base._modify import check_ids, re_order, update_by_id
from power_grid_model_ds._core.model.arrays.base._optional import pandas
from power_grid_model_ds._core.model.arrays.base._string import convert_array_to_string
from power_grid_model_ds._core.model.arrays.base.errors import ArrayDefinitionError
from power_grid_model_ds._core.model.constants import EMPTY_ID, empty
from power_grid_model_ds._core.utils.misc import get_inherited_attrs

# pylint: disable=missing-function-docstring, too-many-public-methods

_RESERVED_COLUMN_NAMES: set = set(dir(np.array([]))).union({"data"})
_DEFAULT_STR_LENGTH: int = 50

Column = NDArray

Self = TypeVar("Self", bound="FancyArray")


class FancyArray(ABC):
    """Base class for all arrays.

    You can create your own array by subclassing FancyArray.
    Array-columns can be defined by adding class attributes with the column name and the numpy dtype.

    Example:
        >>> class MyArray(FancyArray):
        >>>     id: NDArray[np.int64]
        >>>     name: NDArray[np.str_]
        >>>     value: NDArray[np.float64]

    Note on string-columns:
        The default length for string columns is stored in _DEFAULT_STR_LENGTH.
        To change this, you can set the _str_lengths class attribute.

    Example:
        >>> class MyArray(FancyArray):
        >>>     name: NDArray[np.str_]
        >>>     _str_lengths = {"name": 100}

    Extra note on string-columns:
        Where possible, it is recommended use IntEnum's instead of string-columns to reduce memory usage.
    """

    _data: NDArray = np.ndarray([])
    _defaults: dict[str, Any] = {}
    _str_lengths: dict[str, int] = {}

    def __init__(self: Self, *args, data: NDArray | None = None, **kwargs):
        if data is None:
            self._data = build_array(*args, dtype=self.get_dtype(), defaults=self.get_defaults(), **kwargs)
        else:
            self._data = data

    @property
    def data(self: Self) -> NDArray:
        return self._data

    @classmethod
    @lru_cache
    def get_defaults(cls) -> dict[str, Any]:
        return get_inherited_attrs(cls, "_defaults")["_defaults"]

    @classmethod
    @lru_cache
    def get_dtype(cls):
        annotations = get_inherited_attrs(cls, "_str_lengths")
        str_lengths = annotations.pop("_str_lengths")
        dtypes = {}
        for name, dtype in annotations.items():
            if len(dtype.__args__) > 1:
                # regular numpy dtype (i.e. without shape)
                dtypes[name] = dtype.__args__[1].__args__[0]
            elif hasattr(dtype, "__metadata__"):
                # metadata annotation contains shape
                # define dtype using a (type, shape) tuple
                # see: #1 in https://numpy.org/doc/stable/user/basics.rec.html#structured-datatype-creation
                dtype_type = dtype.__args__[0].__args__[1].__args__[0]
                dtype_shape = dtype.__metadata__[0].__args__
                dtypes[name] = (dtype_type, dtype_shape)
            else:
                raise ValueError(f"dtype {dtype} not understood or supported")

        if not dtypes:
            raise ArrayDefinitionError("Array has no defined Columns")
        if reserved := set(dtypes.keys()) & _RESERVED_COLUMN_NAMES:
            raise ArrayDefinitionError(f"Columns cannot be reserved names: {reserved}")

        dtype_list = []
        for name, dtype in dtypes.items():
            if dtype is np.str_:
                string_length = str_lengths.get(name, _DEFAULT_STR_LENGTH)
                dtype_list.append((name, np.dtype(f"U{string_length}")))
            elif dtype is tuple:
                dtype_list.append((name, *dtype))
            else:
                dtype_list.append((name, dtype))
        return np.dtype(dtype_list)

    def __repr__(self: Self) -> str:
        try:
            data = getattr(self, "data")
            if data.size > 3:
                return f"{self.__class__.__name__}([{data[:3]}]... + {data.size - 3} more rows)"
            return f"{self.__class__.__name__}([{data}])"
        except AttributeError:
            return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return self.as_table()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self: Self):
        for record in self._data:
            yield self.__class__(data=np.array([record]))

    def __getattr__(self: Self, attr):
        if attr == "__array_interface__":
            # prevent unintended usage of numpy functions. np.unique/np.sort give wrong results.
            raise TypeError(
                "Cannot use numpy functions directly on FancyArray. "
                "Instead, you can use (fancypy) fp.unique/fp.sort or np.unique/np.sort on array.data"
            )
        if attr.startswith("__"):  # prevent unintended usage of numpy magic methods
            raise AttributeError(f"Cannot get attribute {attr} on {self.__class__.__name__}")

        if attr in self.get_dtype().names:
            return self._data[attr]
        return getattr(self._data, attr)

    def __setattr__(self: Self, attr: str, value: object) -> None:
        if attr in ["_data", "_defaults"]:
            super().__setattr__(attr, value)
            return
        try:
            self._data[attr] = value  # type: ignore[call-overload]
        except (AttributeError, ValueError) as error:
            raise AttributeError(f"Cannot set attribute {attr} on {self.__class__.__name__}") from error

    def __getitem__(self: Self, item):
        """Used by for-loops, slicing [0:3], column-access ['id'], row-access [0], multi-column access.
        Note: If a single item is requested, return a named tuple instead of a np.void object.
        """

        result = self._data.__getitem__(item)

        if isinstance(item, (list, tuple)) and (len(item) == 0 or np.array(item).dtype.type is np.bool_):
            return self.__class__(data=result)
        if isinstance(item, (str, list, tuple)):
            return result
        if isinstance(result, np.void):
            return self.__class__(data=np.array([result]))
        return self.__class__(data=result)

    def __setitem__(self: Self, key, value):
        if isinstance(value, FancyArray):
            value = value.data
        return self._data.__setitem__(key, value)

    def __contains__(self: Self, item: Self) -> bool:
        if isinstance(item, FancyArray):
            return item.data in self._data
        return False

    def __hash__(self: Self):
        return hash(f"{self.__class__} {self}")

    def __eq__(self: Self, other):
        return self._data.__eq__(other.data)

    def __copy__(self: Self):
        return self.__class__(data=copy(self._data))

    def copy(self: Self):
        """Return a copy of this array including its data"""
        return copy(self)

    @classmethod
    def zeros(cls: Type[Self], num: int, empty_id: bool = True) -> Self:
        """Construct an array filled with zeros.

        If 'empty_id' is True, the 'id' column will be filled with EMPTY_ID values.
        """
        dtype = cls.get_dtype()
        zeros_array = np.zeros(num, dtype=dtype)
        if empty_id and "id" in dtype.names:
            zeros_array["id"] = EMPTY_ID  # type: ignore[call-overload]
        return cls(data=zeros_array)

    @classmethod
    def empty(cls: Type[Self], num: int, use_defaults: bool = True) -> Self:
        """Construct an array filled with 'empty' values.

        'empty' values differs per dtype:
            string: "" (empty string)
            float: np.nan
            integer: minimum value

        if 'use_defaults' is True, the default values will be used instead where possible.
        """
        array_dtype = cls.get_dtype()
        array = np.zeros(num, dtype=array_dtype)

        defaults = cls.get_defaults()
        for column in array_dtype.names:
            if use_defaults and column in defaults and defaults[column] is not empty:
                array[column] = defaults[column]
            else:
                array[column] = empty(array_dtype[column])
        return cls(data=array)

    def is_empty(self, column: str) -> NDArray[np.bool_]:
        """Check if a column is filled with 'empty' values."""
        empty_value = self.get_empty_value(column)
        if empty_value is np.nan:
            return np.isnan(self._data[column])
        return np.isin(self._data[column], empty_value)

    def get_empty_value(self, column: str) -> float | int | str | bool:
        array_dtype = self.get_dtype()
        return empty(array_dtype[column])

    def set_empty(self, column: str):
        """Set a column to its 'empty' value."""
        array_dtype = self.get_dtype()
        self._data[column] = empty(array_dtype[column])  # type: ignore[call-overload]

    @property
    def columns(self) -> list[str]:
        return list(self.get_dtype().names)

    @property
    def record(self):
        """Return a named tuple of the first record in the array."""
        if self.size != 1:
            raise ValueError(f"Cannot return record of array with size {self.size}")

        class_name = self.__class__.__name__
        tpl_cls = namedtuple(f"{class_name}Record", self.dtype.names)
        if isinstance(self._data, np.void):
            return tpl_cls(*self._data)
        return tpl_cls(*self._data[0])

    def filter(
        self: Self,
        *args: int | Iterable[int] | np.ndarray,
        mode_: Literal["AND", "OR"] = "AND",
        **kwargs: Any | list[Any] | np.ndarray,
    ) -> Self:
        return self.__class__(data=apply_filter(*args, array=self._data, mode_=mode_, **kwargs))

    def exclude(
        self: Self,
        *args: int | Iterable[int] | np.ndarray,
        mode_: Literal["AND", "OR"] = "AND",
        **kwargs: Any | list[Any] | np.ndarray,
    ) -> Self:
        return self.__class__(data=apply_exclude(*args, array=self._data, mode_=mode_, **kwargs))

    def get(
        self: Self,
        *args: int | Iterable[int] | np.ndarray,
        mode_: Literal["AND", "OR"] = "AND",
        **kwargs: Any | list[Any] | np.ndarray,
    ) -> Self:
        return self.__class__(data=apply_get(*args, array=self._data, mode_=mode_, **kwargs))

    def filter_mask(
        self: Self,
        *args: int | Iterable[int] | np.ndarray,
        mode_: Literal["AND", "OR"] = "AND",
        **kwargs: Any | list[Any] | np.ndarray,
    ) -> np.ndarray:
        return get_filter_mask(*args, array=self._data, mode_=mode_, **kwargs)

    def exclude_mask(
        self: Self,
        *args: int | Iterable[int] | np.ndarray,
        mode_: Literal["AND", "OR"] = "AND",
        **kwargs: Any | list[Any] | np.ndarray,
    ) -> np.ndarray:
        return ~get_filter_mask(*args, array=self._data, mode_=mode_, **kwargs)

    def re_order(self: Self, new_order: ArrayLike, column: str = "id") -> Self:
        return self.__class__(data=re_order(self._data, new_order, column=column))

    def update_by_id(self: Self, ids: ArrayLike, allow_missing: bool = False, **kwargs) -> None:
        try:
            _ = update_by_id(self._data, ids, allow_missing, **kwargs)
        except ValueError as error:
            raise ValueError(f"Cannot update {self.__class__.__name__}. {error}") from error

    def get_updated_by_id(self: Self, ids: ArrayLike, allow_missing: bool = False, **kwargs) -> Self:
        try:
            mask = update_by_id(self._data, ids, allow_missing, **kwargs)
            return self.__class__(data=self._data[mask])
        except ValueError as error:
            raise ValueError(f"Cannot update {self.__class__.__name__}. {error}") from error

    def check_ids(self: Self, return_duplicates: bool = False) -> NDArray | None:
        return check_ids(self._data, return_duplicates=return_duplicates)

    def as_table(self: Self, column_width: int | str = "auto", rows: int = 10) -> str:
        return convert_array_to_string(self, column_width=column_width, rows=rows)

    def as_df(self: Self):
        """Convert to pandas DataFrame"""
        if pandas is None:
            raise ImportError("pandas is not installed")
        return pandas.DataFrame(self._data)

    @classmethod
    def from_extended(cls: Type[Self], extended: Self) -> Self:
        """Create an instance from an extended array."""
        if not isinstance(extended, cls):
            raise TypeError(f"Extended array must be of type {cls.__name__}, got {type(extended).__name__}")
        dtype = cls.get_dtype()
        return cls(data=np.array(extended[list(dtype.names)], dtype=dtype))
