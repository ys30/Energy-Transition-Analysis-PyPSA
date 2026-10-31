"""Attach validated hourly bus demand to an existing PyPSA Network.

No topology is generated. Network buses and snapshots must already exist.
"""
import numpy as np
import pandas as pd


def attach_bus_loads(network, load_matrix, *, prefix="demand_", allow_existing_bus_loads=False):
    """Create one Load per mapped bus, matching network snapshots exactly.

    Return added Load IDs. Refuse overwrites and incomplete snapshots.
    """
    if not isinstance(load_matrix, pd.DataFrame) or load_matrix.empty:
        raise ValueError("load_matrix must be a nonempty DataFrame")
    if load_matrix.index.has_duplicates or load_matrix.columns.has_duplicates:
        raise ValueError("duplicate snapshots or buses")
    if not isinstance(load_matrix.index, pd.DatetimeIndex) or load_matrix.index.tz is None:
        raise ValueError("load_matrix needs timezone-aware snapshots")
    if str(load_matrix.index.tz) != "UTC":
        raise ValueError("load_matrix snapshots must be UTC")
    if not isinstance(network.snapshots, pd.DatetimeIndex):
        raise ValueError("network snapshots must be a DatetimeIndex")
    # PyPSA requires timezone-naive snapshots. They are interpreted as UTC
    # only at this boundary, after the upstream matrix has proven UTC awareness.
    expected = (load_matrix.index.tz_localize(None)
                if network.snapshots.tz is None else load_matrix.index)
    if not expected.equals(network.snapshots):
        raise ValueError("load snapshots must exactly match network snapshots")
    missing = set(load_matrix.columns) - set(network.buses.index)
    if missing:
        raise ValueError(f"mapped buses absent from network: {sorted(missing)}")
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in load_matrix.dtypes):
        raise ValueError("load matrix must be numeric")
    values = load_matrix.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("nonfinite or negative demand")
    names = [prefix + str(bus) for bus in load_matrix.columns]
    if len(set(names)) != len(names) or set(names) & set(network.loads.index):
        raise ValueError("load IDs collide with existing network loads")
    if not allow_existing_bus_loads and not network.loads.empty:
        if "bus" not in network.loads.columns:
            raise ValueError("existing network loads require bus assignments")
        occupied = set(network.loads["bus"].dropna()) & set(load_matrix.columns)
        if occupied:
            raise ValueError(f"existing bus loads would double-count demand: {sorted(occupied)}")
    # Validate all inputs before mutating the network.
    for bus, name in zip(load_matrix.columns, names):
        values_for_network = pd.Series(load_matrix[bus].to_numpy(), index=network.snapshots)
        network.add("Load", name, bus=bus, p_set=values_for_network)
    return names
