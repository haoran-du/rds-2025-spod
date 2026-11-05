"""Paper-specific decomposition kernels; no MATLAB runtime."""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import eigh

@dataclass
class Decomposition:
    modes: np.ndarray
    coefficients: np.ndarray
    energy: np.ndarray
    mean: np.ndarray
    mode_norm: np.ndarray


def gaussian_weights(half_width):
    if not isinstance(half_width, (int, np.integer)) or half_width < 0:
        raise ValueError("half_width must be a nonnegative integer")
    g = np.exp(-np.linspace(-2.285, 2.285, 2*half_width+1)**2)
    return g / g.sum()


def diagonal_filter(correlation, half_width, boundary="periodic"):
    r = np.asarray(correlation, dtype=float)
    if r.ndim != 2 or r.shape[0] != r.shape[1] or not np.isfinite(r).all():
        raise ValueError("Expected finite square temporal correlation")
    if boundary not in ("periodic", "zero"):
        raise ValueError("boundary must be periodic or zero")
    weights = gaussian_weights(half_width)
    n = len(r)
    s = np.zeros_like(r)
    for shift, weight in zip(range(-half_width, half_width+1), weights):
        if boundary == "periodic":
            s += weight*np.roll(r, (shift, shift), axis=(0, 1))
        elif abs(shift) < n:
            dest = slice(max(shift, 0), min(n, n+shift))
            src = slice(max(-shift, 0), min(n, n-shift))
            s[dest, dest] += weight*r[src, src]
    return s


def spod(data, half_width, n_modes=None, weights=None, boundary="periodic", center=True, max_matrix_bytes=1_000_000_000):
    """data=(time,points,components); spatial modes=(points,components,modes).

    Mean removal is explicit. For historical 2025 reproduction the mean was
    obtained using all 19994 frames BEFORE selecting the 9995 analysis frames;
    pass those pre-centered fluctuations with center=False.
    """
    x = np.asarray(data, float)
    if x.ndim != 3 or min(x.shape) < 1 or not np.isfinite(x).all():
        raise ValueError("Expected finite (time,points,components) data")
    n, p, c = x.shape
    if n_modes is not None and (not isinstance(n_modes, int) or not 1 <= n_modes <= n):
        raise ValueError("n_modes must be between 1 and number of snapshots")
    if 4*n*n*8 > max_matrix_bytes:
        raise MemoryError("Dense SPOD exceeds configured correlation-matrix memory budget")
    w = np.ones(p) if weights is None else np.asarray(weights, float)
    if w.shape != (p,) or not np.isfinite(w).all() or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("Expected nonnegative spatial weights with positive sum")
    mean = x.mean(axis=0) if center else np.zeros((p, c))
    fluct = x - mean
    weighted = (fluct*np.sqrt(w)[None, :, None]).reshape(n, p*c)
    r = (weighted @ weighted.T) / (n*w.sum())
    s = diagonal_filter(r, half_width, boundary)
    kwargs = {"subset_by_index": [n-n_modes, n-1]} if n_modes is not None else {}
    energy, vectors = eigh(s, **kwargs)
    energy, vectors = energy[::-1], vectors[:, ::-1]
    keep = energy > np.spacing(max(energy[0], 0))*max(n, p*c)
    energy, vectors = energy[keep], vectors[:, keep]
    coefficients = vectors*np.sqrt(n*energy)
    modes = np.einsum("tpc,tm->pcm", fluct, vectors/np.sqrt(n*energy))
    norm = np.sqrt(np.einsum("pcm,p,pcm->m", modes, w, modes)/w.sum())
    return Decomposition(modes, coefficients, energy, mean, norm)


def pod(data, n_modes=None):
    """Ordinary unweighted POD: first dimension is time, other axes arbitrary."""
    x = np.asarray(data, float)
    if x.ndim < 2 or not np.isfinite(x).all():
        raise ValueError("Expected finite time-first data")
    shape, mean = x.shape, x.mean(axis=0)
    u, s, vh = np.linalg.svd((x-mean).reshape(len(x), -1), full_matrices=False)
    k = len(s) if n_modes is None else n_modes
    if not isinstance(k, int) or not 1 <= k <= len(s):
        raise ValueError("Invalid mode count")
    return Decomposition(vh[:k].T.reshape(*shape[1:], k), u[:, :k]*s[:k], s[:k]**2/len(x), mean, np.ones(k))


def third_order_split(large, small, axis=0):
    """u'^3 = uL^3 + 3 uL^2 uS + 3 uL uS^2 + uS^3, unnormalized."""
    large, small = np.asarray(large), np.asarray(small)
    if large.shape != small.shape:
        raise ValueError("Scale arrays must have identical shapes")
    return np.stack([np.mean(large**3, axis=axis), 3*np.mean(large**2*small, axis=axis),
                     3*np.mean(large*small**2, axis=axis), np.mean(small**3, axis=axis)])
