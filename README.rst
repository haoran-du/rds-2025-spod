RdS 2025: SPOD and boundary-layer scale interaction
==================================================

Independent Python tools for Du, Perret & Savory (2025), Boundary-Layer
Meteorology, https://doi.org/10.1007/s10546-025-00922-z.
No MATLAB runtime or installation of another RdS repository is required.

Install and run
---------------

From this repository directory, with Python 3.10 or newer::

    python -m venv .venv
    # Linux/macOS: source .venv/bin/activate
    # Windows PowerShell: .venv\Scripts\Activate.ps1
    python -m pip install -e ".[test]"
    python -m pytest -q
    rds2025 recover --data-root "/path/to/DATA" --output outputs/spod
    rds2025 recover --data-root "/path/to/DATA" --output outputs/spod_verified --verify-projection

``python -m rds2025.cli`` is an equivalent entry point. Inputs remain
external and read-only, in their original DATA directory layout.

Scope and limitations
---------------------

This implements Sieber-type correlation-filtered SPOD, not frequency-domain
Welch SPOD. The kernel exposes normalization, spatial weights, Gaussian
filter width, temporal boundary conditions, centering and a memory guard.
Small synthetic tests verify the mathematics; they are not a full-data
9995-by-9995 eigensolve.

The recovery workflow selectively reads saved eigenvalues and the first
12 coefficient histories from large HDF5 MAT cells. It regenerates energy
curves and phase portraits corresponding to Figs. 5–6. Optional projection
checks use raw YZ fields, demeaning all 19994 frames before selecting the
9995 analysis frames, and verify zero-lag spatial modes in all five cases.

The retained full-projection baseline contains 39 passes and one failed
POD-label check: the 2b file named POD embeds a nonzero SPOD filter width.
That file is explicitly excluded from the ordinary-POD comparison. The
command returns status 1 for this known inconsistency; it does not silently
turn the check green. See ``docs/AUDIT_FINDINGS.rst``.

The complete eigensolve, time-lagged modes and all later scale-interaction
figures have not yet been independently recomputed. No claim of complete
paper reproduction is made. See ``docs/SPLIT_VERIFICATION.rst`` for tests
performed after repository extraction.

Contents and provenance
-----------------------

``src/rds2025`` contains only this paper's recovery workflow, POD/SPOD and
third-order kernels, and local helpers. It does not import the 2023
statistics pipeline or the 2024 LSE package. CI uses synthetic tests.

The local ``archive/matlab`` preserves the associated MATLAB source and
development variants, including original attribution. Only its hash index
is public; arrays, MATLAB originals and publisher PDFs are excluded.
See ``THIRD_PARTY.rst`` and ``CITATION.cff``.
