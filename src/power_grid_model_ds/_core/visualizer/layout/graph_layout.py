from enum import Enum


class LayoutOptions(Enum):
    """Cytoscape layout options."""

    RANDOM = "random"
    CIRCLE = "circle"
    CONCENTRIC = "concentric"
    GRID = "grid"
    COSE = "cose"
    BREADTHFIRST = "breadthfirst"
    PRESET = "preset"

    def layout_with_config(self) -> dict:
        """Get the layout options for the selected layout."""
        if self == LayoutOptions.BREADTHFIRST:
            return {"name": self.value, "roots": 'node[group = "source_ghost_node"]'}
        return {"name": self.value}

    @staticmethod
    def dropdown_layouts() -> list[str]:
        """Get a list of available layout options for the dropdown."""
        return [option.value for option in LayoutOptions if option != LayoutOptions.PRESET]
