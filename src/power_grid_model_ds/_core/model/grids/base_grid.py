# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Experimental annotation-based grid definition, independent of the existing Grid.

Define only the arrays needed by an application, without a dataclass decorator::

    class MyGrid(BaseGrid):
        node: NodeArray
        line: LineArray

    grid = MyGrid(node=NodeArray(id=[1, 2], u_rated=[10_000, 10_000]))
    empty_grid = MyGrid.empty()

Omitted arrays are initialized independently for each instance. Subclasses can
override array types or add arrays. Array attributes retain their annotated
types, but constructor keywords are not yet checked statically against the schema.

This proof of concept does not provide graph synchronization, ID tracking,
reference validation, serialization, or the existing Grid's mutation methods.
"""

from collections.abc import Iterator
from typing import ClassVar, Self, get_origin, get_type_hints

from power_grid_model_ds._core.model.arrays.base.array import FancyArray


class BaseGrid:
    """An empty grid schema populated by array annotations on subclasses."""

    _array_types: ClassVar[dict[str, type[FancyArray]]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        array_types: dict[str, type[FancyArray]] = {}
        for name, array_type in get_type_hints(cls).items():
            if name.startswith("_") or get_origin(array_type) is ClassVar:
                continue
            if name in dir(BaseGrid):
                raise TypeError(f"Array name '{name}' conflicts with a BaseGrid method.")
            if not isinstance(array_type, type) or not issubclass(array_type, FancyArray):
                raise TypeError(f"Grid field '{name}' must be annotated with a FancyArray subclass.")
            array_types[name] = array_type
        cls._array_types = array_types

    def __init__(self, **arrays: FancyArray) -> None:
        unknown = arrays.keys() - self._array_types.keys()
        if unknown:
            raise TypeError(f"Unknown arrays for {type(self).__name__}: {sorted(unknown)}")

        for name, array_type in self._array_types.items():
            array = arrays[name] if name in arrays else array_type()
            if not isinstance(array, array_type):
                raise TypeError(f"Array '{name}' must be a {array_type.__name__}, got {type(array).__name__}.")
            setattr(self, name, array)

    @classmethod
    def empty(cls) -> Self:
        """Create an instance with an independent empty array for each field."""
        return cls()

    def all_arrays(self) -> Iterator[FancyArray]:
        """Iterate over declared arrays in schema order."""
        for name in self._array_types:
            yield getattr(self, name)

    def __repr__(self) -> str:
        arrays = ", ".join(f"{name}={getattr(self, name)!r}" for name in self._array_types)
        return f"{type(self).__name__}({arrays})"
