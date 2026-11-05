"""Selective recovery of 2025 SPOD outputs; no multi-GB cell-array load."""
from pathlib import Path
import json
import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .io import CASES, instantaneous_mat
from .common import comparison, savefig, COLORS, LABELS


def recover_spod(root: Path, output: Path, verify_projection=False, modes=12):
    root, output = root.resolve(strict=True), output.resolve()
    if root == output or root in output.parents:
        raise ValueError("Output cannot be in source data")
    output.mkdir(parents=True, exist_ok=True)
    folder = root / "POSTPROCESSING/2024_SPOD_ALLTOGETHER"
    checks, rows, series = [], [], {}
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for kind in ("SPOD", "POD"):
        for case, color, legend in zip(CASES, COLORS, LABELS):
            path = folder / f"{kind}_LSE_2024_copy1_export_{case}.mat"
            if not path.exists():
                continue
            with h5py.File(path, "r") as f:
                refs = f["SPOD_LSE_2024_copy1_export"][()].ravel()
                energy = f[refs[1]][()].ravel()
                coeff = f[refs[2]][:modes, :].T
                params = f[refs[7]][()].ravel()
                n = len(coeff)
                expected_nf = (48 if case in ("1b", "2b") else 24) if kind == "SPOD" else 0
                check = comparison(f"{kind}/{case}/filter_half_width", params[0], expected_nf)
                checks.append(check)
                if not check["pass"]:
                    rows.append({"file": path.name, "status": "excluded: filename/embedded filter mismatch", "parameters": params.tolist()})
                    continue
                checks.append(comparison(f"{kind}/{case}/coefficient_orthogonality", coeff.T@coeff/n,
                                         np.diag(energy[:modes]), atol=1e-11, rtol=1e-10))
                checks.append({"name": f"{kind}/{case}/energy_sorted_nonnegative", "pass": bool(np.all(np.diff(energy) <= 1e-14) and energy.min() >= -1e-12)})
                series[(kind, case)] = (coeff, energy)
                if kind == "SPOD" or case in ("1b", "6b"):
                    ax.semilogx(np.arange(1, len(energy)+1), np.cumsum(energy)/energy.sum(), color=color,
                                ls="-" if kind == "SPOD" else "--", label=f"{legend} {kind}")
                row = {"file": path.name, "parameters": params.tolist(), "snapshots": n,
                       "leading_mode_count_loaded": coeff.shape[1], "total_energy": float(energy.sum()),
                       "energy_fraction_20": float(energy[:20].sum()/energy.sum())}
                if verify_projection and kind == "SPOD":
                    for component, cell in (("u", 0), ("w", 5), ("v", 6)):
                        saved_modes = f[refs[cell]][:modes, :, :].transpose(1, 2, 0)
                        projection = np.zeros_like(saved_modes)
                        with h5py.File(instantaneous_mat(root, case, component, "YZ"), "r") as raw:
                            dataset = raw[f"{component}_contour"]
                            total = np.zeros((64, 128))
                            for start in range(0, dataset.shape[0], 100):
                                total += dataset[start:start+100, 13:77, 22:150].sum(axis=0)
                            mean = total / dataset.shape[0]
                            for start in range(0, n, 100):
                                stop = min(n, start+100)
                                # MATLAB selected 6:10000 after all-frame demeaning.
                                data = dataset[start+5:stop+5, 13:77, 22:150]-mean
                                projection += np.einsum("tzy,tm->zym", data, coeff[start:stop], optimize=True)
                        projection /= (n*energy[:modes])
                        checks.append(comparison(f"SPOD/{case}/{component}/zero-lag-mode-from-raw", projection,
                                                 saved_modes, atol=1e-9, rtol=1e-9))
                    row["raw_projection_verified"] = all(c["pass"] for c in checks[-3:])
                rows.append(row)
            print(f"{kind} {case}: recovered {len(energy)} eigenvalues and {coeff.shape[1]} coefficient histories", flush=True)
    ax.axhline(.2, color=".5", ls=":")
    ax.axhline(.15, color=".5", ls=":")
    ax.set(xlabel="Number of modes", ylabel="Cumulative energy fraction", ylim=(0, 1.03))
    ax.legend(fontsize=8, ncol=2)
    savefig(fig, output, "fig06_recovered_SPOD_POD_energy")
    fig = plt.figure(figsize=(10, 8), layout="constrained")
    for i, key in enumerate((("POD", "1b"), ("POD", "6b"), ("SPOD", "1b"), ("SPOD", "6b")), 1):
        a, e = series[key]
        ax = fig.add_subplot(2, 2, i, projection="3d")
        ax.plot(a[:500, 0]/np.sqrt(e[0]), np.arange(1, 501)/14.8*5.8/.975,
                a[:500, 1]/np.sqrt(e[1]), lw=.7)
        ax.set(xlabel=r"$\tilde{b}_1$", ylabel=r"$tU_e/\delta$", zlabel=r"$\tilde{b}_2$", title=f"{key[0]} {key[1]}")
    savefig(fig, output, "fig05_recovered_phase_portraits")
    report = {"status": "recovered saved eigenpairs; full eigensolve not rerun", "checks": checks,
              "files": rows, "raw_projection_requested": verify_projection,
              "note": "Zero-lag spatial modes only; time-lagged spatio-temporal modes and later scale-interaction figures are separate."}
    (output / "validation.json").write_text(json.dumps(report, indent=2))
    return {"passed": sum(c["pass"] for c in checks), "failed": [c for c in checks if not c["pass"]]}
