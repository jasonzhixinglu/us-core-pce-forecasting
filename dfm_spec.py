"""Shared specification of the dynamic factor model.

run.py and fit_dfm.py both build the model through `build()`, so the estimated parameters
in the cache always correspond to the model that consumes them.

The fit is memory-hungry: the Kalman smoother holds 147x147x499 state covariance arrays and
EM keeps several copies per iteration. Running it inside run.py, which is already holding the
raw series, the five block panels and the figures, pushes the process into paging and cuts
throughput to roughly a quarter. fit_dfm.py therefore does the fit in a separate process that
holds nothing but the panel, and run.py only ever smooths with the cached parameters.
"""
import pickle
import numpy as np

PARAMS_FILE = "dfm_params.npz"
PANEL_FILE = "panel.pkl"
MAXITER = 250
TOL = 1e-5


def stamp_of(X, end):
    """Fingerprint of the panel; a cached fit is only reused if this still matches."""
    return f"{X.shape[0]}x{X.shape[1]}@{end:%Y-%m}"


def build(X, blocks):
    """The model: two global factors plus one per block, joint VAR(1), AR(1) idiosyncratic."""
    from statsmodels.tsa.statespace.dynamic_factor_mq import DynamicFactorMQ
    Xf = X.copy()
    Xf.columns = [c for _, c in X.columns]
    blk_of = {c: b for b, c in X.columns}
    names = ["Global"] + list(blocks)
    return DynamicFactorMQ(
        Xf,
        factors={c: ["Global", blk_of[c]] for c in Xf.columns},
        factor_multiplicities={"Global": 2},
        factor_orders={tuple(names): 1},
        idiosyncratic_ar1=True,
        standardize=True,
    )


def save_panel(path, X, blocks, end):
    with open(path, "wb") as f:
        pickle.dump({"X": X, "blocks": list(blocks), "end": end}, f)


def load_panel(path):
    with open(path, "rb") as f:
        d = pickle.load(f)
    return d["X"], d["blocks"], d["end"]


def load_params(path, stamp):
    """Cached parameters, or None if absent or fitted on a different panel."""
    if not path.exists():
        return None
    z = np.load(path, allow_pickle=False)
    if str(z["stamp"]) != stamp:
        return None
    return z["params"]
