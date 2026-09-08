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
    specs = sys.argv[1:] or list(dfm_spec.SPECS)
    panel = CACHE / dfm_spec.PANEL_FILE
    if not panel.exists():
        sys.exit(f"{panel} not found: run run.py once so it can write the panel.")
    X, blocks, end = dfm_spec.load_panel(panel)
    stamp = dfm_spec.stamp_of(X, end)
    print(f"panel {X.shape[0]} months x {X.shape[1]} variables through {end:%Y-%m}")

    for spec in specs:
        fit_one(X, blocks, stamp, spec)


def fit_one(X, blocks, stamp, spec):
    print(f"\n--- {spec}: {dfm_spec.SPEC_LABEL[spec]}")
    mod = dfm_spec.build(X, blocks, spec)
    print(f"{mod.k_states} states, {len(mod.param_names)} parameters; EM up to {dfm_spec.MAXITER} iterations")
    t0 = time.time()
    res = mod.fit(maxiter=dfm_spec.MAXITER, tolerance=dfm_spec.TOL, disp=10)
    el = time.time() - t0

    # Save the parameters before anything else can raise: the fit is the expensive part and
    # must never be lost to a bookkeeping error.
    out = CACHE / dfm_spec.params_file(spec)
    params = np.asarray(res.params)
    np.savez(out, params=params, stamp=stamp, iterations=-1, converged=False, llf=res.llf)

    # statsmodels' EM path stores a Bunch with 'iter' (not 'iterations') and no convergence
    # flag; it stops early only when the criterion is met, so iter < maxiter means converged.
    rv = getattr(res, "mle_retvals", None)
    it = int(getattr(rv, "iter", -1)) if rv is not None else -1
    conv = 0 <= it < dfm_spec.MAXITER
    np.savez(out, params=params, stamp=stamp, iterations=it, converged=conv, llf=res.llf)

    per = f"{el / it:.1f}s per iteration" if it > 0 else "iteration count unavailable"
    print(f"{'converged' if conv else 'STOPPED AT CAP, NOT CONVERGED'} after {it} iterations, {el:.0f}s ({per}), llf {res.llf:.1f}")
    if not conv:
        print("WARNING: parameters cached anyway; the report will say 'not converged'.")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
