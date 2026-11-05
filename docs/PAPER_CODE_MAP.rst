Paper-to-code map
=================

Paths below are DATA-relative and retained in the local archive.

2025: SPOD in the YZ plane
-------------------------

* ``2024_SPOD/SPOD_LSE_2024_copy1.m`` is the main saved-output producer.
  Directory year 2024 refers to development, not publication year.
* ``2024_SPOD/SPOD.m`` is the Sieber routine, modified to expose extra
  outputs. Preserve author/version information; check redistribution rights.
* MATLAB Y_cut=23:150, Z_cut=14:77; all-frame demeaning precedes the
  analysis time window 6:10000 (9995 snapshots).
* Gaussian half-widths: 48,48,24,24,24 for 1b,2b,3b,6b,ca; periodic BC.
* ``POSTPROCESSING/2024_SPOD_ALLTOGETHER/SPOD_ALLTOGETHER.m`` consumes
  cell-array exports: Ui, lambda, a, horizontal, z, Wi, Vi, parameters.
* ``2024_SPOD/*copy2.m``, ``*copy3.m`` and ``POSTPROCESSING/2024_SPOD_LSE``
  include cross-plane prediction/exploration; not every branch is established
  as belonging to the published 2025 manuscript.

Python: see this repository's ``src/rds2025`` package.

