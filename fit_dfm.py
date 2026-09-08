"""Estimate the dynamic factor model by EM and cache the parameters.

    python fit_dfm.py

Reads cache/panel.pkl (written by run.py when it builds the panel) and writes
cache/dfm_params.npz. run.py invokes this as a subprocess when the cache is missing or
stale; run it directly to re-estimate without regenerating the report.

This runs in its own process on purpose: see the note in dfm_spec.py.
"""
import sys, time, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dfm_spec

CACHE = HERE / "cache"


def main():
    panel = CACHE / dfm_spec.PANEL_FILE
    if not panel.exists():
        sys.exit(f"{panel} not found: run run.py once so it can write the panel.")
    X, blocks, end = dfm_spec.load_panel(panel)
    stamp = dfm_spec.stamp_of(X, end)
    print(f"panel {X.shape[0]} months x {X.shape[1]} variables through {end:%Y-%m}")

    mod = dfm_spec.build(X, blocks)
    print(f"{mod.k_states} states, {len(mod.param_names)} parameters; EM up to {dfm_spec.MAXITER} iterations")
    t0 = time.time()
    res = mod.fit(maxiter=dfm_spec.MAXITER, tolerance=dfm_spec.TOL, disp=10)
    el = time.time() - t0

    it = res.mle_retvals["iterations"]
    conv = bool(res.mle_retvals.get("converged", False))
    print(f"{'converged' if conv else 'STOPPED AT CAP, NOT CONVERGED'} after {it} iterations, "
          f"{el:.0f}s ({el / max(it, 1):.1f}s per iteration), llf {res.llf:.1f}")
    if not conv:
        print("WARNING: parameters are being cached anyway; the report will say 'not converged'.")

    np.savez(CACHE / dfm_spec.PARAMS_FILE, params=np.asarray(res.params), stamp=stamp,
             iterations=it, converged=conv, llf=res.llf)
    print(f"wrote {CACHE / dfm_spec.PARAMS_FILE}")


if __name__ == "__main__":
    main()
