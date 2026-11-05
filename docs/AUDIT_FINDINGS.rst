2025 paper: conventions and audit findings
=================================================

1. Coordinate/component conventions
----------------------------------

XZ Dantec U,V,W columns map to physical U,W,-V; the vertical calibration
offset is +155 mm. YZ columns map to physical V,W,U, with +175 mm offset.
Python arrays use (time,z,horizontal[,component]) and physical U,V,W order.
MATLAB v7.3/HDF5 storage dimensions are reversed; explicit transposes are
tested. The YZ coordinate named x_contour in old files is physically y.

6. Mislabeled POD cache in the 2025 directory
-------------------------------------------

``POD_LSE_2024_copy1_export_2b.mat`` embeds [48,0,9994], not a zero filter
width. It is excluded from the ordinary-POD comparison. Valid B1h/B6h POD
controls embed Nf=0. The main five SPOD cases embed Nf=48,48,24,24,24.
All use 9995 snapshots after removal of the mean over all 19994 frames.

The SPOD method is Sieber correlation-filtered SPOD, not Welch/frequency-
domain SPOD. The archived kernel uses a normalized Gaussian diagonal
filter and periodic temporal boundary conditions. The projection reader
verifies zero-lag spatial modes; time-lagged modes are not substituted by
ordinary spatial orthogonality assertions.

