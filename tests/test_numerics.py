import numpy as np
import pytest
from rds2025.decomposition import pod, third_order_split, diagonal_filter, gaussian_weights, spod

@pytest.mark.parametrize("boundary", ["zero", "periodic"])
@pytest.mark.parametrize("nf", [0, 1, 3])
def test_diagonal_filter_independent_reference(boundary, nf):
    r = np.arange(49).reshape(7, 7)
    expected = np.zeros((7, 7))
    for i in range(7):
        for j in range(7):
            for k, w in zip(range(-nf, nf+1), gaussian_weights(nf)):
                if boundary == "periodic":
                    expected[i, j] += w*r[(i+k)%7, (j+k)%7]
                elif 0 <= i+k < 7 and 0 <= j+k < 7:
                    expected[i, j] += w*r[i+k, j+k]
    np.testing.assert_allclose(diagonal_filter(r, nf, boundary), expected, atol=1e-13)


def test_spod_zero_filter_reconstructs_and_has_correct_normalization():
    x = np.random.default_rng(3).normal(size=(40, 7, 3))
    result = spod(x, 0)
    recovered = np.einsum("pcm,tm->tpc", result.modes, result.coefficients)+result.mean
    np.testing.assert_allclose(recovered, x, atol=1e-12)
    np.testing.assert_allclose(result.coefficients.T@result.coefficients/len(x), np.diag(result.energy), atol=1e-12)
    np.testing.assert_allclose(result.mode_norm, 1, atol=1e-12)
    assert result.energy.sum() == pytest.approx(np.mean(np.sum((x-x.mean(0))**2, axis=2)))


def test_spod_periodic_filter_preserves_trace():
    x = np.random.default_rng(5).normal(size=(36, 4, 2))
    a, b = spod(x, 0), spod(x, 3)
    assert a.energy.sum() == pytest.approx(b.energy.sum())


def test_pod_reconstruction():
    x = np.random.default_rng(9).normal(size=(25, 4, 3))
    p = pod(x)
    np.testing.assert_allclose(np.einsum("pcm,tm->tpc", p.modes, p.coefficients)+p.mean, x, atol=1e-12)


def test_third_moment_closure():
    l, s = np.random.default_rng(8).normal(size=(2, 100, 8))
    np.testing.assert_allclose(third_order_split(l, s).sum(0), np.mean((l+s)**3, axis=0), atol=1e-14)


def test_spod_memory_limit():
    with pytest.raises(MemoryError):
        spod(np.ones((100, 1, 1)), 0, max_matrix_bytes=100)
