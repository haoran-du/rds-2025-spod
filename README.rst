Investigation of Boundary Layer Scale Interactions Over Realistic Morphology Influenced by An Upstream Tall Building Using the SPOD Method
==========================================================================================================================================

Authors: Haoran Du, Laurent Perret, and Eric Savory

Affiliations:

* Haoran Du and Eric Savory: Department of Mechanical and Materials Engineering,
  University of Western Ontario, London, Ontario, Canada.
* Laurent Perret: Nantes Universite, Ecole Centrale de Nantes, CNRS, LHEEA,
  UMR 6598, Nantes, France.

Corresponding author: Haoran Du, hdu59@uwo.ca

Published in Boundary-Layer Meteorology (2025).
Article: https://doi.org/10.1007/s10546-025-00922-z

Code Repository
---------------

This repository contains Python routines for the SPOD analysis of flow
over the Rue des Suisses (RdS) morphology. It includes the correlation-filtered
SPOD formulation used in the study and routines for reading saved modal
results and plotting their energy distributions and temporal coefficients.

This is a code-only release. Experimental data, processed arrays and
generated figures are supplied or produced separately.

Repository layout
-----------------

* ``src/rds2025/analysis.py``: recovery and plotting of saved POD/SPOD results.
* ``src/rds2025/decomposition.py``: POD, correlation-filtered SPOD and third-order moments.
* ``src/rds2025/io.py``: measurement-file readers and array conventions.
* ``data/README.rst``: expected inputs and directory layout.
* ``tests/``: automated tests for the Python routines.
* ``docs/``: implementation and processing notes.

Setup
-----

Use Python 3.10 or later. From the repository directory::

    python -m venv .venv

Activate the environment on Linux/macOS::

    source .venv/bin/activate

Or in Windows PowerShell::

    .\.venv\Scripts\Activate.ps1

Then install the package::

    python -m pip install -e .

Run order
---------

1. Obtain the external POD/SPOD results listed in ``data/README.rst``.
   Keep their original directory layout.
2. Recover the saved modal energy distributions and phase portraits::

       rds2025 recover --data-root "/path/to/DATA" --output outputs/spod

3. If the original YZ velocity fields are available, the zero-lag spatial
   projections can also be recomputed::

       rds2025 recover --data-root "/path/to/DATA" --output outputs/spod_projection --verify-projection

All generated files are written to the selected output directory. ``outputs/``
is ignored by Git. ``python -m rds2025.cli`` is an alternative to ``rds2025``.

Processing scope
----------------

SPOD here denotes the correlation-filtered formulation, not frequency-domain
Welch SPOD. The recovery workflow reads saved eigenpairs and the first twelve
coefficient histories to generate the plots corresponding to Figs. 5–6.

The full experimental-data eigensolve, time-lagged spatial modes and later
scale-interaction figures are not yet included in the recovery workflow.
Implementation details are provided in ``docs/``.

Data and citation
-----------------

Input files are external to this repository; their expected layout is given
in ``data/README.rst``. Please cite the article linked above when using this
code. Citation metadata are also provided in ``CITATION.cff``.
