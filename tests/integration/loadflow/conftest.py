import pytest
from power_grid_model import BranchSide, LoadGenType, WindingType

from power_grid_model_ds import Grid
from power_grid_model_ds._core.model.arrays import LineArray, NodeArray, SourceArray, SymLoadArray, TransformerArray


@pytest.fixture
def simple_loadflow_grid(grid: Grid) -> Grid:
    nodes = NodeArray.zeros(2)
    nodes.id = [0, 1]
    nodes.u_rated = [10_500] * 2

    lines = LineArray.zeros(1)
    lines.id = [2]
    lines.from_node = [0]
    lines.to_node = [1]
    lines.from_status = [1]
    lines.to_status = [1]
    lines.r1 = [0.1]
    lines.x1 = [0.01]

    sources = SourceArray.zeros(1)
    sources.id = [3]
    sources.node = [0]
    sources.status = [1]
    sources.u_ref = [1]

    loads = SymLoadArray.zeros(1)
    loads.id = [4]
    loads.node = [1]
    loads.status = [1]
    loads.type = [LoadGenType.const_power]
    loads.p_specified = [250_000]
    loads.q_specified = [50_000]

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)
    return grid


@pytest.fixture
def loadflow_grid_with_transformer(grid: Grid) -> Grid:
    nodes = NodeArray.zeros(3)
    nodes.id = [0, 1, 2]
    nodes.u_rated = [10_500] * 2 + [3_000]

    lines = LineArray.zeros(1)
    lines.id = 3
    lines.from_node = 0
    lines.to_node = 1
    lines.from_status = 1
    lines.to_status = 1
    lines.r1 = 0.1
    lines.x1 = 0.01

    sources = SourceArray.zeros(1)
    sources.id = 4
    sources.node = 0
    sources.status = 1
    sources.u_ref = 1

    loads = SymLoadArray.zeros(2)
    loads.id = [5, 6]
    loads.node = [1, 2]
    loads.status = [1, 1]
    loads.p_specified = [25_000] * 2
    loads.q_specified = [5_000] * 2

    transformers = TransformerArray(
        id=[7],
        from_node=[1],
        to_node=[2],
        from_status=[1],
        to_status=[1],
        u1=[10_500],
        u2=[3_000],
        sn=[30e6],
        clock=[12],
        tap_size=[2.5e3],
        uk=[0.203],
        pk=[100e3],
        i0=[0.0],
        p0=[0.0],
        winding_from=[WindingType.wye.value],
        winding_to=[WindingType.wye.value],
        tap_side=[BranchSide.from_side.value],
        tap_pos=[0],
        tap_min=[-11],
        tap_max=[9],
        tap_nom=[0],
    )

    grid.append(nodes)
    grid.append(lines)
    grid.append(sources)
    grid.append(loads)
    grid.append(transformers)

    return grid
