Expected inputs
===============

Pass the original DATA directory to ``--data-root``. Saved results are read from
``POSTPROCESSING/2024_SPOD_ALLTOGETHER/`` using the names
``SPOD_LSE_2024_copy1_export_<case>.mat`` and
``POD_LSE_2024_copy1_export_<case>.mat``. These are HDF5/MATLAB v7.3 files
containing the saved modal arrays, eigenvalues, coefficients and parameters.
The historical folder name is retained although this repository accompanies
the 2025 article.

The case identifiers are ``1b``, ``2b``, ``3b``, ``6b`` and ``ca``. The recovery
reads the first twelve coefficient histories. Filter parameters are read
from each file, rather than inferred solely from its name; incompatible
entries are excluded and identified in the generated processing report.

The optional ``--verify-projection`` calculation additionally needs the
original YZ instantaneous velocity arrays under ``ORIGINAL/``, as read by
``src/rds2025/io.py``. It demeans all available frames before selecting
MATLAB frames 6:10000 and projects the selected fields onto the saved
temporal coefficients.

Inputs are read-only. Output paths must be outside the input data tree.
