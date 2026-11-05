"""Paper-specific MAT locations and readers."""
from pathlib import Path
import numpy as np
import h5py
from scipy.io import loadmat, whosmat

CASES = {"1b": "1block", "2b": "2block", "3b": "3block", "6b": "6block", "ca": "cathedral"}


def one_mat(path: Path) -> np.ndarray:
    """Small single-variable MAT only; refuse ambiguous variables."""
    if path.stat().st_size > 100_000_000:
        raise ValueError(f"Use a streaming reader for large MAT file: {path.name}")
    if h5py.is_hdf5(path):
        with h5py.File(path, "r") as f:
            keys = [k for k in f if not k.startswith("#")]
            if len(keys) != 1:
                raise ValueError(f"Expected one variable in {path.name}: {keys}")
            d = f[keys[0]]
            if d.size * d.dtype.itemsize > 100_000_000:
                raise ValueError("Array too large for small MAT reader")
            return d[()].T
    info = whosmat(path)
    if any(np.prod(shape)*8 > 100_000_000 for _, shape, _ in info):
        raise ValueError("Decompressed array too large for small MAT reader")
    values = [v for k, v in loadmat(path).items() if not k.startswith("__")]
    if len(values) != 1:
        raise ValueError(f"Expected one variable in {path.name}")
    return values[0]


def instantaneous_mat(root: Path, case: str, component: str, plane: str = "XZ") -> Path:
    folder = root / "ORIGINAL" / f"RdS_PIV_{plane}_ORIGINAL" / CASES[case]
    middle = "" if case == "1b" and plane == "XZ" else f"_{plane}"
    return folder / f"{component}_contour_PIV{middle}_{case}.mat"
