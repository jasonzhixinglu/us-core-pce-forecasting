"""US inflation signals: agreement, disagreement, and forecasting.

Sequential script. Downloads FRED data (cached), builds five predictor blocks, extracts
global and block factors, forecasts core PCE, decomposes the forecast (current signals and
pseudo-real-time news), measures disagreement, finds analogs, cuts by supply/demand regime,
and writes a report (report.md + report.html, figures in figures/) that answers the 15
questions directly.

    python research/us_inflation_signals/run.py [--refresh]

Data: latest-vintage FRED (CSV endpoint, no key). Non-FRED, flagged: SPF individual CPI
forecasts (Philadelphia Fed) and the Gilchrist-Zakrajsek excess bond premium (Federal
Reserve). Not a real-time evaluation; swap fred() for an ALFRED loader to go real-time.
"""
import io, sys, time, warnings, html, subprocess, pickle
from pathlib import Path
import numpy as np, pandas as pd, requests
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.ar_model import AutoReg
from scipy import stats
warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.3, "font.size": 9})

HERE = Path(__file__).resolve().parent; CACHE = HERE / "cache"; FIG = HERE / "figures"
sys.path.insert(0, str(HERE)); from text import TEXT, READING, BLOCK_PROSE, SECTION2, BLOCK_FACTOR   # editable prose lives in text.py
import dfm_spec   # shared DFM specification, so the cached fit matches the model used here
for d in (CACHE, FIG): d.mkdir(exist_ok=True)
REFRESH = "--refresh" in sys.argv; REFIT = "--refit" in sys.argv; RECOMPUTE = "--recompute" in sys.argv   # --refit re-runs the DFM EM (slow); otherwise cached parameters are reused
START = "1985-01-01"; OOS_START = "2000-01-01"; H = [3, 6, 12, 24]
UA = {"User-Agent": "Mozilla/5.0"}
t0 = time.time()

# =============================================================================== report
class Report:
    def __init__(self): self.items = []; self.summary_at = None
    def h(self, level, text): self.items.append(("h", level, text))
    def p(self, text): self.items.append(("p", text))
    def note(self, text): self.items.append(("note", text))
    def bullets(self, lines): self.items.append(("ul", list(lines)))
    def summary_slot(self): self.summary_at = len(self.items)
    def summary(self, lines): self.items.insert(self.summary_at, ("summary", list(lines)))
    def table(self, df, caption="", fmt="{:.2f}", small=False):
        df = df.copy()
        cell = lambda v: ("" if pd.isna(v) else fmt.format(v)) if isinstance(v, (float, np.floating)) else ("" if v is None else str(v))
        for c in df.columns: df[c] = df[c].astype(object).map(cell)
        self.items.append(("table", df, caption, small))
    def fig(self, fig, name, caption=""):
        path = FIG / f"{name}.png"; fig.savefig(path, bbox_inches="tight"); plt.close(fig); self.items.append(("fig", f"figures/{name}.png", caption))
    def write(self, stem):
        md, hb, toc = [], [], []
        for it in self.items:
            k = it[0]
            if k == "h":
                lvl, txt = it[1], it[2]; md.append(f"\n{'#'*lvl} {txt}\n"); aid = f"s{len(toc)}"
                if lvl == 2: toc.append((aid, txt))
                hb.append(f"<h{lvl} id='{aid}'>{html.escape(txt)}</h{lvl}>")
            elif k == "p": md.append(it[1] + "\n"); hb.append(f"<p>{html.escape(it[1])}</p>")
            elif k == "note": md.append(f"> {it[1]}\n"); hb.append(f"<div class='note'>{html.escape(it[1])}</div>")
            elif k == "ul": md += [f"- {l}" for l in it[1]] + [""]; hb.append("<ul>" + "".join(f"<li>{html.escape(l)}</li>" for l in it[1]) + "</ul>")
            elif k == "summary": md += ["**Summary**\n"] + [f"- {l}" for l in it[1]] + [""]; hb.append("<div class='summary'><b>Summary</b><ul>" + "".join(f"<li>{html.escape(l)}</li>" for l in it[1]) + "</ul></div>")
            elif k == "table":
                df, cap, small = it[1], it[2], it[3]; idx = df.index.name or ""
                cols = [str(idx)] + [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in df.columns]
                if cap: md.append(f"*{cap}*\n")
                md.append("| " + " | ".join(cols) + " |"); md.append("|" + "---|" * len(cols))
                for i, r in df.iterrows(): md.append("| " + " | ".join([str(i)] + [str(v) for v in r.values]) + " |")
                md.append(""); hb.append("<div class='tbl'>" + (f"<div class='cap'>{html.escape(cap)}</div>" if cap else "") + df.to_html(border=0, classes="t small" if small else "t") + "</div>")
            elif k == "fig":
                md.append(f"![{it[2]}]({it[1]})\n" + (f"*{it[2]}*\n" if it[2] else "")); hb.append(f"<figure><img src='{it[1]}'><figcaption>{html.escape(it[2])}</figcaption></figure>")
        (HERE / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")
        css = ("body{font-family:Georgia,'Times New Roman',serif;font-size:14px;line-height:1.5;max-width:1000px;margin:36px auto;padding:0 24px;color:#1a1a1a}"
               "h1{font-size:26px;margin-bottom:4px} h2{font-size:19px;border-bottom:1px solid #bbb;padding-bottom:3px;margin-top:40px} h3{font-size:15px;margin-top:22px;color:#333}"
               "p{margin:8px 0 10px} .summary{background:#f4f6f9;border-left:4px solid #1f3b5c;padding:10px 16px;margin:16px 0} .summary ul{margin:6px 0 0 16px;padding:0} .summary li{margin:4px 0}"
               ".note{background:#fbf7ea;border-left:4px solid #d4a017;padding:8px 14px;margin:12px 0;font-size:13px} .toc{font-size:13px;columns:2;margin:10px 0 20px} .toc a{text-decoration:none;color:#1f3b5c}"
               ".tbl{margin:12px 0 18px;overflow-x:auto} .cap{font-size:12px;color:#555;font-style:italic;margin-bottom:4px} table.t{border-collapse:collapse;font-family:Helvetica,Arial,sans-serif;font-size:12px}"
               ".t th,.t td{padding:3px 9px;border-bottom:1px solid #e3e3e3;text-align:right;white-space:nowrap} .t th{background:#f0f0f0;font-weight:600} .t td:first-child,.t th:first-child{text-align:left}"
               ".t.small{font-size:11px} figure{margin:14px 0 20px} img{max-width:100%;border:1px solid #eee} figcaption{font-size:12px;color:#555;font-style:italic;margin-top:4px} ul{margin:6px 0 10px 20px} li{margin:4px 0}")
        toc_html = "<div class='toc'>" + "<br>".join(f"<a href='#{a}'>{html.escape(t)}</a>" for a, t in toc) + "</div>"
        body = "".join(hb); first_h2 = body.index("<h2"); body = body[:first_h2] + toc_html + body[first_h2:]
        (HERE / f"{stem}.html").write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>US inflation signals</title><style>{css}</style></head><body>{body}</body></html>", encoding="utf-8")
R = Report()

# =============================================================================== stage cache
# Expensive intermediates that do not depend on chart or prose edits are pickled under a key that
# changes when their inputs do. A chart tweak then reruns in well under a minute. --recompute
# forces every stage; a stage also recomputes when its key (panel fingerprint, parameters) changes.
STAGES = CACHE / "stages"; STAGES.mkdir(exist_ok=True)
def stage(name, fn, key):
    f = STAGES / f"{name}.pkl"
    if f.exists() and not RECOMPUTE:
        d = pickle.load(open(f, "rb"))
        if d["key"] == key: print(f"[stage] {name}: cached"); return d["value"]
    t = time.time(); v = fn(); pickle.dump({"key": key, "value": v}, open(f, "wb"))
    print(f"[stage] {name}: computed in {time.time() - t:.0f}s"); return v

# =============================================================================== helpers
def fred(sid):
    """Latest-vintage FRED series (cached). Replace with an ALFRED/vintage loader to go real-time."""
    f = CACHE / f"{sid}.csv"
    if f.exists() and not REFRESH:
        s = pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
    else:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=1900-01-01", timeout=60)
        if r.status_code != 200 or not r.text.startswith(("observation_date", "DATE")): raise ValueError(f"FRED {sid}: HTTP {r.status_code}")
        d = pd.read_csv(io.StringIO(r.text)); d.columns = ["date", sid]
        s = pd.Series(pd.to_numeric(d[sid], errors="coerce").values, index=pd.to_datetime(d["date"]), name=sid).dropna(); s.to_csv(f)
    return s[s.index >= "1950-01-01"].rename(sid)

def to_monthly(s, how="mean"):
    s = s.dropna(); fd = np.median(np.diff(s.index.values).astype("timedelta64[D]").astype(int)) if len(s) > 3 else 30
    if fd < 25: return s.resample("MS").mean() if how == "mean" else s.resample("MS").last()
    s.index = s.index.to_period("M").to_timestamp(); return s
def q_to_m(s):
    s = s.dropna(); s.index = s.index.to_period("Q").to_timestamp(how="start"); return s.resample("MS").ffill()
def ann(x, h): return 1200.0 / h * (np.log(x) - np.log(x).shift(h))
def dlog(x, h): return 100.0 * (np.log(x) - np.log(x).shift(h))
def pct_rank(s, v=None):
    s = s.dropna()
    if s.empty: return np.nan
    v = s.iloc[-1] if v is None else v; return 100 * (s < v).mean()
def ordinal(x): x = int(round(x)); return f"{x}{'th' if 10 <= x % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(x % 10, 'th')}"
def zscore(df): return (df - df.mean()) / df.std()
def pca(Z, k):
    """PCA on a standardized panel with missing values via iterative imputation. Returns scores, loadings, explained shares, imputed panel."""
    A = Z.values.copy(); mask = np.isnan(A); A[mask] = 0.0
    for _ in range(50 if mask.any() else 0):
        U, sv, Vt = np.linalg.svd(A, full_matrices=False); fit = (U[:, :k] * sv[:k]) @ Vt[:k]
        if np.abs(A[mask] - fit[mask]).max() < 1e-6: A[mask] = fit[mask]; break
        A[mask] = fit[mask]
    U, sv, Vt = np.linalg.svd(A, full_matrices=False)
    scores = pd.DataFrame(U[:, :k] * sv[:k], index=Z.index, columns=[f"PC{i+1}" for i in range(k)])
    return scores, pd.DataFrame(Vt[:k].T, index=Z.columns, columns=scores.columns), sv[:k] ** 2 / (sv ** 2).sum(), pd.DataFrame(A, index=Z.index, columns=Z.columns)
def ols(y, Xm, hac=None):
    r = sm.OLS(y, sm.add_constant(Xm), missing="drop"); return r.fit(cov_type="HAC", cov_kwds={"maxlags": hac}) if hac else r.fit()
def oos_forecast(D, target, cols, h, start=OOS_START):
    """Expanding-window direct forecasts; at origin t the training set uses only targets known by t."""
    fc = pd.Series(index=D.index, dtype=float)
    for t in D.index[D.index >= start]:
        tr = D.loc[:t].iloc[:-h].dropna(subset=[target] + cols)
        if len(tr) < 60: continue
        b = np.linalg.lstsq(np.column_stack([np.ones(len(tr)), tr[cols].values]), tr[target].values, rcond=None)[0]
        x = D.loc[t, cols].values.astype(float)
        if not np.isnan(x).any(): fc[t] = b[0] + x @ b[1:]
    return fc
def vname(c): return c[1] if isinstance(c, tuple) else c
META = []
def reg(block, short, name, source, transform): META.append(dict(block=block, shorthand=short, indicator=name, source=source, transformation=transform))
def meta_table(block):
    d = pd.DataFrame([m_ for m_ in META if m_["block"] == block]).drop(columns="block").set_index("shorthand"); return d

# =============================================================================== data
FRED_IDS = {
 "CPIAUCSL": "CPI headline", "CPILFESL": "CPI core", "PCEPI": "PCE headline", "PCEPILFE": "PCE core",
 "MEDCPIM158SFRBCLE": "Median CPI 1m ann.", "MEDCPIM159SFRBCLE": "Median CPI 12m", "TRMMEANCPIM158SFRBCLE": "Trimmed-mean CPI 1m ann.", "TRMMEANCPIM159SFRBCLE": "Trimmed-mean CPI 12m",
 "PCETRIM1M158SFRBDAL": "Trimmed-mean PCE 1m ann.", "PCETRIM12M159SFRBDAL": "Trimmed-mean PCE 12m", "STICKCPIM157SFRBATL": "Sticky CPI 1m ann.", "STICKCPIM159SFRBATL": "Sticky CPI 12m",
 "CORESTICKM157SFRBATL": "Core sticky CPI 1m ann.", "CORESTICKM159SFRBATL": "Core sticky CPI 12m", "FLEXCPIM157SFRBATL": "Flexible CPI 1m ann.", "FLEXCPIM159SFRBATL": "Flexible CPI 12m",
 "COREFLEXCPIM157SFRBATL": "Core flexible CPI 1m ann.", "COREFLEXCPIM159SFRBATL": "Core flexible CPI 12m", "CUSR0000SASLE": "CPI services ex energy", "DSERRG3M086SBEA": "PCE services prices",
 "MICH": "Michigan 1y expectations", "EXPINF1YR": "Cleveland Fed 1y expectations", "EXPINF10YR": "Cleveland Fed 10y expectations", "T5YIE": "5y breakeven", "T10YIE": "10y breakeven", "T5YIFR": "5y5y breakeven",
 "UNRATE": "Unemployment rate", "UNEMPLOY": "Unemployed", "PAYEMS": "Payrolls", "ICSA": "Initial claims", "JTSJOL": "Job openings", "JTSQUR": "Quits rate", "AHETPI": "Avg hourly earnings", "ECIWAG": "ECI wages (q)",
 "W209RC1": "Compensation of employees", "DPCERA3M086SBEA": "Real PCE", "RRSFS": "Real retail sales", "INDPRO": "Industrial production", "TCU": "Capacity utilization", "GPDIC1": "Real private investment (q)",
 "GDPC1": "Real GDP (q)", "UMCSENT": "Michigan sentiment",
 "FEDFUNDS": "Fed funds", "DGS2": "2y Treasury", "DGS10": "10y Treasury", "DFII10": "10y TIPS", "NFCI": "NFCI", "ANFCI": "Adjusted NFCI", "VIXCLS": "VIX", "BAA10Y": "Baa minus 10y",
 "NASDAQCOM": "Nasdaq", "DTWEXBGS": "Broad dollar (2006-)", "TWEXBMTH": "Broad dollar (1973-2019)", "WTISPLC": "WTI oil", "PPIACO": "PPI all commodities", "THREEFYTP10": "10y term premium",
 "DRTSCILM": "SLOOS C&I standards (q)", "MORTGAGE30US": "30y mortgage rate"}
CPI_COMPONENTS = {   # 34 CPI expenditure categories, SA, chosen so that no category nests another
 "CUSR0000SAF111": "Cereals & bakery", "CUSR0000SAF112": "Meats, poultry, fish, eggs", "CUSR0000SEFJ": "Dairy", "CUSR0000SAF113": "Fruits & vegetables", "CUSR0000SAF114": "Other food at home",
 "CUSR0000SEFV": "Food away from home", "CUSR0000SAF116": "Alcoholic beverages", "CUSR0000SETB01": "Gasoline", "CUSR0000SEHE": "Fuel oil", "CUSR0000SEHF01": "Electricity", "CUSR0000SEHF02": "Utility gas",
 "CUSR0000SAA1": "Men's & boys' apparel", "CUSR0000SAA2": "Women's & girls' apparel", "CUSR0000SEAE": "Footwear", "CUSR0000SEAF": "Infants' apparel", "CUSR0000SETA01": "New vehicles", "CUSR0000SETA02": "Used vehicles",
 "CUSR0000SETC": "Motor vehicle parts", "CUSR0000SAM1": "Medical care commodities", "CUSR0000SAH3": "Household furnishings & operations", "CUSR0000SEGA": "Tobacco", "CUSR0000SERA": "Recreation commodities",
 "CUSR0000SEEA": "Educational books", "CUSR0000SEHA": "Rent of primary residence", "CUSR0000SEHC": "Owners' equivalent rent", "CUSR0000SEHB": "Lodging away from home", "CUSR0000SEHG": "Water, sewer, trash",
 "CUSR0000SEMC": "Professional medical services", "CUSR0000SEMD": "Hospital services", "CUSR0000SETD": "Vehicle maintenance & repair", "CUSR0000SETG": "Public transportation", "CUSR0000SEEB": "Tuition & childcare",
 "CUSR0000SEGD": "Personal care services", "CUSR0000SAS367": "Other services"}
RAW, ver = {}, []
for sid, desc in {**FRED_IDS, **CPI_COMPONENTS}.items():
    try: s = fred(sid); RAW[sid] = s; ver.append(dict(id=sid, desc=desc, first=s.index[0].date(), last=s.index[-1].date(), status="ok"))
    except Exception as e: ver.append(dict(id=sid, desc=desc, first=None, last=None, status=f"FAILED: {e}"))
VER = pd.DataFrame(ver).set_index("id"); VER["flag"] = np.where(VER["status"] != "ok", "FAILED", np.where(pd.to_datetime(VER["first"]) > "1995-01-01", "short history", ""))
VER.to_csv(CACHE / "series_verification.csv")

SPF_BASE = "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/data-files/files/"
def load_spf():
    f = CACHE / "spf_individual_cpi.parquet"
    if f.exists() and not REFRESH: ind = pd.read_parquet(f)
    else:
        ind = pd.read_excel(io.BytesIO(requests.get(SPF_BASE + "Individual_CPI.xlsx", headers=UA, timeout=60).content))
        m10 = pd.read_excel(io.BytesIO(requests.get(SPF_BASE + "Median_CPI10_Level.xlsx", headers=UA, timeout=60).content))
        ind = ind.merge(m10, on=["YEAR", "QUARTER"], how="left"); ind.to_parquet(f)
    ind["date"] = pd.PeriodIndex(ind["YEAR"].astype(int).astype(str) + "Q" + ind["QUARTER"].astype(int).astype(str), freq="Q").to_timestamp(how="start")
    ind["cpi_4q"] = ind[["CPI2", "CPI3", "CPI4", "CPI5"]].mean(axis=1, skipna=False); g = ind.groupby("date")
    return pd.DataFrame({"spf_cpi_4q": g["cpi_4q"].median(), "spf_cpi_4q_iqr": g["cpi_4q"].quantile(.75) - g["cpi_4q"].quantile(.25), "spf_cpi_4q_sd": g["cpi_4q"].std(),
                         "spf_n": g["cpi_4q"].count(), "spf_cpi_10y": g["CPI10"].first()})
SPF_Q = load_spf()
def load_ebp():
    f = CACHE / "ebp.csv"
    if not f.exists() or REFRESH: f.write_text(requests.get("https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv", headers=UA, timeout=60).text)
    d = pd.read_csv(f); d.index = pd.to_datetime(d["date"]); return d[["gz_spread", "ebp"]]
EBP = load_ebp()
m = lambda sid, how="mean": to_monthly(RAW[sid], how)

R.h(1, "US inflation signals: agreement, disagreement, and forecasting")
R.summary_slot()
R.h(2, "Introduction")
R.p(TEXT["p07_we_ask_what_the_current_config"])
R.p(TEXT["p07b_the_motivation_is_the_current"])
R.p(TEXT["p01_all_of_these_are_treated_as_po"])
R.h(2, "1. The five blocks")
# ------------------------------------------------------------------ block EDA
import re
GROUPS = {"infl": [("short-horizon rate (1m/3m)", r"_(1|3)m$"), ("6m rate", r"_6m$"), ("12m rate", r"_12m$")],
          "dist": [("breadth", r"share_gt"), ("breadth momentum", r"share_(accel|decel)"), ("dispersion", r"xs_(sd|iqr|p90|skew)|upper_tail"), ("central tendency", r"xs_median")],
          "exp": [("dispersion", r"_sd|_iqr"), ("households", r"mich"), ("professionals", r"spf"), ("model-based", r"clev"), ("markets", r"bei")],
          "dem": [("wages", r"ahe|eci|comp"), ("labor market", r"unrate|claims|payroll|vu_|quits"), ("activity", r"real_|ip_|capu|gdp"), ("sentiment", r"sentiment")],
          "fin": [("risk pricing", r"vix|baa|gz|ebp|term_premium"), ("conditions indexes", r"nfci"), ("rates", r"fedfunds|dgs|real_10y|mortgage"), ("asset prices", r"equity|usd|oil|ppi"), ("credit supply", r"sloos")]}
def group_of(block, v):
    for g, rx in GROUPS[block]:
        if re.search(rx, v): return g
    return "other"
def describe_factor(block, l, k=8):
    """Which variable groups a factor aligns with, from its top-k |correlations|, split by sign."""
    tp = l.reindex(l.abs().sort_values(ascending=False).index[:k]); pos, neg = tp[tp > 0], tp[tp < 0]
    def side(x): 
        if x.empty: return "none"
        g = pd.Series([group_of(block, vname(c)) for c in x.index]).value_counts(); return ", ".join(f"{k_} ({n})" for k_, n in g.items()) + "; e.g. " + ", ".join(vname(c) for c in x.index[:3])
    return f"aligned positively with {side(pos)}; inverted: {side(neg)}"

BPC = {}; DESC = {}
def block_eda(name, df, ref, flip=False, title=""):
    """Standardize over the panel window, PCA; figure: scree and PC1/PC2 paths; correlations with PC1 and one-factor residuals; correlations with PC2 and two-factor residuals."""
    def compute():   # the PCA with iterative imputation is the slow part; cached per block, keyed on the block's data
        Zb = zscore(df[df.index >= START].dropna(how="all")); Zb = Zb.loc[:, Zb.notna().mean() > 0.5]
        sc, ld, ex, Zf = pca(Zb, min(8, Zb.shape[1]))
        sgn = np.sign(np.corrcoef(sc["PC1"], Zb[ref].fillna(0))[0, 1]) * (-1 if flip else 1)
        f1 = sgn * sc["PC1"]; f1z = (f1 - f1.mean()) / f1.std(); l1 = Zf.corrwith(f1z)
        f2z = (sc["PC2"] - sc["PC2"].mean()) / sc["PC2"].std(); l2 = Zf.corrwith(f2z); s2 = np.sign(l2.loc[l2.abs().idxmax()]); f2z, l2 = s2 * f2z, s2 * l2   # PC2 sign: largest |correlation| positive
        res1 = (Zf - np.outer(f1z, l1)).where(Zb.notna()); res2 = (res1 - np.outer(f2z, l2)).where(Zb.notna())
        return dict(Zb=Zb, ex=ex, f1=f1, f1z=f1z, l1=l1, f2z=f2z, l2=l2, res1=res1, res2=res2)
    dfw = df[df.index >= START]
    key = (name, START, dfw.shape, str(dfw.index[-1].date()), tuple(dfw.columns), ref, flip, float(np.nansum(dfw.values)))
    c_ = stage(f"eda_{name}", compute, key=key)
    Zb, ex, f1, f1z, l1, f2z, l2, res1, res2 = (c_[k] for k in ("Zb", "ex", "f1", "f1z", "l1", "f2z", "l2", "res1", "res2")); BPC[name] = f1
    fig, ax = plt.subplots(3, 2, figsize=(15, 12.5), gridspec_kw={"width_ratios": [1, 1.7], "height_ratios": [0.8, 1, 1]})
    ax[0, 0].bar(range(1, len(ex) + 1), 100 * ex, color="#1e293b"); ax[0, 0].set_title(f"Scree, % of variance (PC1 {100*ex[0]:.0f}%, PC2 {100*ex[1]:.0f}%)"); ax[0, 0].set_xticks(range(1, len(ex) + 1))
    ax[0, 1].plot(f1z.index, f1z, color="k", lw=1.3, label="PC1"); ax[0, 1].plot(f2z.index, f2z, color="k", lw=1, ls="--", label="PC2"); ax[0, 1].axhline(0, color="grey", lw=.6)
    ax[0, 1].set_title(f"Factors, standardized (PC1: + = inflationary; latest {f1z.iloc[-1]:+.1f}, {ordinal(pct_rank(f1))} percentile)"); ax[0, 1].legend(frameon=False)
    KROWS = 30
    def corr_panel(a, l, lab):
        sel = l.abs().sort_values(ascending=False).index[:KROWS]; show = l[sel]; k = len(sel)
        a.barh(np.arange(k) + 0.5, show.abs().values, height=0.8, color=np.where(show.values > 0, "#1e293b", "#7c9cc6")); a.set_ylim(k, 0)
        a.set_yticks(np.arange(k) + 0.5); a.set_yticklabels([f"{vname(c)}{' (inv)' if v < 0 else ''}" for c, v in show.items()], fontsize=6.5 if k > 20 else 7)
        a.set_xlim(0, 1); a.set_title(f"|corr| with {lab}, top {k} of {len(l)} (inv = sign inverted)", fontsize=8.5); return sel
    def heat(a, res, sel, lab):
        last = res[sel].iloc[-3:].mean(); k = len(sel)
        im = a.imshow(res[sel].T.values, aspect="auto", cmap="RdBu_r", vmin=-3, vmax=3, extent=[mdates.date2num(res.index[0]), mdates.date2num(res.index[-1]), k, 0]); a.xaxis_date(); a.grid(False); a.set_ylim(k, 0)
        a.yaxis.tick_right(); a.set_yticks(np.arange(k) + 0.5); a.set_yticklabels([f"{vname(c)} ({last[c]:+.1f})" for c in sel], fontsize=6.5 if k > 20 else 7); a.tick_params(axis="y", length=0)
        a.set_title(f"Residuals, {lab} fit (same rows and order as the bars; red = above the factor fit; label = last-3-month mean, sd)", fontsize=8.5)
        cax = a.inset_axes([0.3, -0.2, 0.4, 0.04]); fig.colorbar(im, cax=cax, orientation="horizontal"); cax.tick_params(labelsize=7)
    heat(ax[1, 1], res1, corr_panel(ax[1, 0], l1, "PC1"), "one-factor"); heat(ax[2, 1], res2, corr_panel(ax[2, 0], l2, "PC2"), "two-factor")
    plt.tight_layout(); R.fig(fig, f"block_{name}", title)
    DESC[(name, 1)] = describe_factor(name, l1); DESC[(name, 2)] = describe_factor(name, l2)
    for para in BLOCK_PROSE[name]: R.p(para)
    # The generated descriptions are no longer printed in the report: the block prose in text.py is
    # written by hand. They go to the console instead, as the check that the prose still fits the data.
    top_res = res1.iloc[-1].dropna(); top_res = top_res.reindex(top_res.abs().sort_values().index[-3:][::-1])
    print(f"[{name}] PC1 {f1z.iloc[-1]:+.2f}z ({ordinal(pct_rank(f1))} pct), PC2 {f2z.iloc[-1]:+.2f}z ({ordinal(pct_rank(f2z))} pct); var {100*ex[0]:.0f}/{100*ex[1]:.0f}/{100*ex[2]:.0f}%")
    print(f"        PC1 {DESC[(name, 1)]}")
    print(f"        PC2 {DESC[(name, 2)]}")
    print(f"        largest residuals: " + ", ".join(f"{vname(c)} ({v:+.1f} sd)" for c, v in top_res.items()))

# ------------------------------------------------------------------ block 1: inflation measures
B1 = {}
IDX = [("CPIAUCSL", "cpi", "CPI, all items", "BLS via FRED"), ("CPILFESL", "cpi_core", "CPI ex food and energy", "BLS via FRED"), ("PCEPI", "pce", "PCE price index", "BEA via FRED"),
       ("PCEPILFE", "pce_core", "PCE ex food and energy", "BEA via FRED"), ("CUSR0000SASLE", "cpi_svc_xe", "CPI services ex energy services", "BLS via FRED"), ("DSERRG3M086SBEA", "pce_svc", "PCE services price index", "BEA via FRED")]
RATES = [("MEDCPIM158SFRBCLE", "MEDCPIM159SFRBCLE", "cpi_median", "Median CPI", "Cleveland Fed via FRED"), ("TRMMEANCPIM158SFRBCLE", "TRMMEANCPIM159SFRBCLE", "cpi_trim", "16% trimmed-mean CPI", "Cleveland Fed via FRED"),
         ("PCETRIM1M158SFRBDAL", "PCETRIM12M159SFRBDAL", "pce_trim", "Trimmed-mean PCE", "Dallas Fed via FRED"), ("STICKCPIM157SFRBATL", "STICKCPIM159SFRBATL", "cpi_sticky", "Sticky-price CPI", "Atlanta Fed via FRED"),
         ("CORESTICKM157SFRBATL", "CORESTICKM159SFRBATL", "cpi_core_sticky", "Core sticky-price CPI", "Atlanta Fed via FRED"), ("FLEXCPIM157SFRBATL", "FLEXCPIM159SFRBATL", "cpi_flex", "Flexible-price CPI", "Atlanta Fed via FRED"),
         ("COREFLEXCPIM157SFRBATL", "COREFLEXCPIM159SFRBATL", "cpi_core_flex", "Core flexible-price CPI", "Atlanta Fed via FRED")]
for sid, tag, name, src in IDX:
    hs = (1, 3, 6, 12, 24) if tag == "pce_core" else (1, 3, 6, 12)   # 24m only for the target: the iterated forecast reads it at t+h
    for h in hs: B1[f"{tag}_{h}m"] = ann(m(sid), h)
    reg(1, f"{tag}_{{{','.join(str(h) for h in hs)}}}m", name, src, f"annualized {'/'.join(str(h) for h in hs)}-month log change of the index")
for m1, m12, tag, name, src in RATES:
    r1, r12 = m(m1), m(m12); B1[f"{tag}_1m"] = r1; B1[f"{tag}_3m"] = r1.rolling(3).mean(); B1[f"{tag}_6m"] = r1.rolling(6).mean(); B1[f"{tag}_12m"] = r12
    reg(1, f"{tag}_{{1,3,6,12}}m", name, src, "published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate")
B1 = pd.DataFrame(B1)
R.h(3, "Block 1: inflation measures")
R.table(meta_table(1), "Block 1 indicators", small=True)
block_eda("infl", B1, "pce_core_12m", title="Block 1, inflation measures")

# ------------------------------------------------------------------ block 2: distribution
P = pd.DataFrame({sid: m(sid) for sid in CPI_COMPONENTS if sid in RAW}).sort_index(); WEIGHTS = None
def breadth_stats(P, h, min_n=20, weights=None):
    pi = 1200.0 / h * (np.log(P) - np.log(P).shift(h)); pi12 = 1200.0 / 12 * (np.log(P) - np.log(P).shift(12)); ref = pi12 if h < 12 else pi12.shift(12)
    n = pi.notna().sum(axis=1); ok = n >= min_n; q = lambda a: pi.quantile(a, axis=1)
    out = pd.DataFrame({"n_cats": n, "share_gt0": (pi > 0).sum(axis=1) / n, "share_gt2": (pi > 2).sum(axis=1) / n, "share_gt3": (pi > 3).sum(axis=1) / n, "share_gt4": (pi > 4).sum(axis=1) / n,
                        "share_gt5": (pi > 5).sum(axis=1) / n, "share_accel": (pi > ref).sum(axis=1) / n, "share_decel": (pi < ref).sum(axis=1) / n, "xs_sd": pi.std(axis=1), "xs_iqr": q(.75) - q(.25),
                        "xs_p90_p10": q(.9) - q(.1), "xs_skew": pi.skew(axis=1), "xs_median": pi.median(axis=1), "upper_tail_share": pi.clip(lower=0).where(pi.gt(q(.9), axis=0), 0).sum(axis=1) / pi.abs().sum(axis=1)})
    if weights is not None:
        w = pd.Series(weights).reindex(pi.columns); ws = pi.notna().mul(w, axis=1).sum(axis=1)
        for th in (0, 2, 3, 4, 5): out[f"wshare_gt{th}"] = (pi > th).mul(w, axis=1).sum(axis=1) / ws
    out.columns = [f"{c}_{h}m" if c != "n_cats" else c for c in out.columns]; return out.where(ok)
B2 = pd.concat([breadth_stats(P, h, weights=WEIGHTS).drop(columns="n_cats") for h in (3, 6, 12)], axis=1); B2.insert(0, "n_cats", breadth_stats(P, 12)["n_cats"])
for short, name, tr in [("share_gt{0,2,3,4,5}", "share of categories with inflation above 0/2/3/4/5 percent", "count divided by categories available"), ("share_accel", "share of categories accelerating", "h-month rate above the 12-month rate (at h = 12: above the 12-month rate a year earlier)"),
                        ("share_decel", "share of categories decelerating", "as above, below"), ("xs_sd", "cross-sectional standard deviation", "across categories"), ("xs_iqr", "interquartile range", "75th minus 25th percentile across categories"),
                        ("xs_p90_p10", "90-10 spread", "90th minus 10th percentile"), ("xs_skew", "cross-sectional skewness", ""), ("xs_median", "median category inflation", ""), ("upper_tail_share", "upper-tail share", "share of the sum of absolute category inflation coming from the top decile")]:
    reg(2, f"{short}_{{3,6,12}}m", name, "34 CPI categories, BLS via FRED", (tr + "; " if tr else "") + "computed on annualized 3/6/12-month category inflation")
R.h(3, "Block 2: price-change distribution")
R.table(pd.DataFrame([[g, c] for g, c in [("Food (7)", "cereals; meats, poultry, fish, eggs; dairy; fruits and vegetables; other food at home; food away from home; alcohol"), ("Energy (4)", "gasoline; fuel oil; electricity; utility gas"),
    ("Core goods (12)", "men's, women's and infants' apparel; footwear; new and used vehicles; vehicle parts; medical commodities; household furnishings; tobacco; recreation commodities; educational books"),
    ("Services (11)", "rent; owners' equivalent rent; lodging away from home; water and sewer; professional medical and hospital services; vehicle maintenance; public transportation; tuition and childcare; personal care; other services")]],
    columns=["Group", "Categories"]).set_index("Group"), "Block 2 universe: 34 CPI expenditure categories (FRED, seasonally adjusted)", small=True)
R.table(meta_table(2), "Block 2 indicators", small=True)
block_eda("dist", B2.drop(columns="n_cats"), "share_gt3_12m", title="Block 2, price-change distribution")

# ------------------------------------------------------------------ block 3: expectations
B3 = pd.DataFrame({"mich_1y": m("MICH"), "clev_1y": m("EXPINF1YR"), "clev_10y": m("EXPINF10YR"), "bei_5y": m("T5YIE"), "bei_10y": m("T10YIE"), "bei_5y5y": m("T5YIFR")}).join(SPF_Q.drop(columns="spf_n").pipe(q_to_m), how="outer")
MICH_LESS_SPF = B3["mich_1y"] - B3["spf_cpi_4q"]     # used in the answers, not in the block
for short, name, src, tr in [("mich_1y", "Michigan 1-year expected inflation, median", "Michigan survey via FRED", "level, percent"), ("clev_1y", "Cleveland Fed 1-year expected inflation", "Cleveland Fed via FRED", "level"), ("clev_10y", "Cleveland Fed 10-year expected inflation", "Cleveland Fed via FRED", "level"),
                             ("bei_5y", "5-year breakeven inflation", "Treasury via FRED", "monthly mean of daily"), ("bei_10y", "10-year breakeven", "Treasury via FRED", "monthly mean"), ("bei_5y5y", "5y5y forward breakeven", "Treasury via FRED", "monthly mean"),
                             ("spf_cpi_4q", "SPF median CPI forecast, next four quarters", "Philadelphia Fed SPF (not on FRED)", "mean of the individual CPI2-CPI5 forecasts, median across forecasters; quarterly spread to months"),
                             ("spf_cpi_4q_iqr", "SPF cross-sectional IQR of the 4-quarter forecast", "Philadelphia Fed SPF", "75th minus 25th percentile across forecasters"), ("spf_cpi_4q_sd", "SPF cross-sectional SD of the 4-quarter forecast", "Philadelphia Fed SPF", "across forecasters"),
                             ("spf_cpi_10y", "SPF median 10-year CPI forecast", "Philadelphia Fed SPF", "quarterly spread to months")]:
    reg(3, short, name, src, tr)
R.h(3, "Block 3: inflation expectations")
R.table(meta_table(3), "Block 3 indicators", small=True)
block_eda("exp", B3, "mich_1y", title="Block 3, expectations")

# ------------------------------------------------------------------ block 4: demand and labor
B4 = pd.DataFrame({"unrate": m("UNRATE"), "payrolls_3m": ann(m("PAYEMS"), 3), "payrolls_12m": ann(m("PAYEMS"), 12), "claims_log": np.log(m("ICSA")),
                   "vu_ratio": m("JTSJOL") / m("UNEMPLOY"), "quits": m("JTSQUR"), "ahe_12m": ann(m("AHETPI"), 12), "ahe_3m": ann(m("AHETPI"), 3),
                   "eci_wages_yoy": q_to_m(RAW["ECIWAG"].pct_change(4) * 100), "comp_12m": ann(m("W209RC1"), 12), "real_pce_6m": ann(m("DPCERA3M086SBEA"), 6), "real_pce_12m": ann(m("DPCERA3M086SBEA"), 12),
                   "real_retail_6m": ann(m("RRSFS"), 6), "ip_6m": ann(m("INDPRO"), 6), "ip_12m": ann(m("INDPRO"), 12), "capu": m("TCU"), "real_inv_yoy": q_to_m(RAW["GPDIC1"].pct_change(4) * 100),
                   "gdp_yoy": q_to_m(RAW["GDPC1"].pct_change(4) * 100), "sentiment": m("UMCSENT")})
for short, name, src, tr in [("unrate", "Unemployment rate", "BLS via FRED", "level, percent"), ("payrolls_3m / payrolls_12m", "Nonfarm payrolls", "BLS via FRED", "annualized 3- and 12-month log growth"), ("claims_log", "Initial claims", "DOL via FRED", "log of the monthly mean of weekly claims"),
                             ("vu_ratio", "Job openings to unemployed", "BLS JOLTS via FRED", "ratio"), ("quits", "Quits rate", "BLS JOLTS via FRED", "level, percent"), ("ahe_3m / ahe_12m", "Average hourly earnings, production workers", "BLS via FRED", "annualized 3- and 12-month log growth"),
                             ("eci_wages_yoy", "ECI wages and salaries", "BLS via FRED", "year-on-year percent, quarterly spread to months"), ("comp_12m", "Compensation of employees", "BEA via FRED", "12-month log growth"), ("real_pce_6m / real_pce_12m", "Real PCE", "BEA via FRED", "annualized 6- and 12-month log growth"),
                             ("real_retail_6m", "Real retail sales", "Census via FRED", "annualized 6-month log growth"), ("ip_6m / ip_12m", "Industrial production", "Fed via FRED", "annualized 6- and 12-month log growth"), ("capu", "Capacity utilization", "Fed via FRED", "level, percent"),
                             ("real_inv_yoy", "Real gross private domestic investment", "BEA via FRED", "year-on-year, quarterly spread to months"), ("gdp_yoy", "Real GDP", "BEA via FRED", "year-on-year, quarterly spread to months"), ("sentiment", "Michigan consumer sentiment", "Michigan via FRED", "level")]:
    reg(4, short, name, src, tr)
R.h(3, "Block 4: demand and labor")
R.table(meta_table(4), "Block 4 indicators", small=True)
block_eda("dem", B4, "payrolls_12m", title="Block 4, demand and labor")

# ------------------------------------------------------------------ block 5: financial
usd_old, usd_new = m("TWEXBMTH"), m("DTWEXBGS"); ov = usd_old.index.intersection(usd_new.index); usd = pd.concat([usd_old[usd_old.index < ov[0]] * (usd_new[ov] / usd_old[ov]).mean(), usd_new])
B5 = pd.DataFrame({"fedfunds": m("FEDFUNDS"), "dgs2": m("DGS2"), "dgs10": m("DGS10"), "real_10y_tips": m("DFII10"), "real_10y_clev": m("DGS10") - m("EXPINF10YR"), "nfci": m("NFCI"), "anfci": m("ANFCI"), "vix": m("VIXCLS"), "baa_spread": m("BAA10Y"), "gz_spread": EBP["gz_spread"], "ebp": EBP["ebp"],
                   "term_premium_10y": m("THREEFYTP10"), "equity_12m_ret": dlog(m("NASDAQCOM"), 12), "equity_3m_ret": dlog(m("NASDAQCOM"), 3), "usd_12m": dlog(usd, 12), "oil_12m": dlog(m("WTISPLC"), 12),
                   "oil_3m": dlog(m("WTISPLC"), 3), "ppi_comm_12m": dlog(m("PPIACO"), 12), "sloos_ci": q_to_m(RAW["DRTSCILM"]), "mortgage30": m("MORTGAGE30US")})
for short, name, src, tr in [("fedfunds", "Effective federal funds rate", "Fed via FRED", "monthly mean, percent"), ("dgs2 / dgs10", "2- and 10-year Treasury yields", "Treasury via FRED", "monthly mean of daily"), ("real_10y_tips", "10-year TIPS yield", "Treasury via FRED", "monthly mean"),
                             ("real_10y_clev", "10-year real rate", "derived", "10-year yield minus Cleveland Fed 10-year expected inflation (the expectation is in block 3, so this is not a within-block difference)"),
                             ("nfci / anfci", "Chicago Fed NFCI and adjusted NFCI", "Chicago Fed via FRED", "monthly mean; positive = tighter"), ("vix", "VIX", "Cboe via FRED", "monthly mean"), ("baa_spread", "Moody's Baa yield minus 10-year Treasury", "FRED (published spread)", "monthly mean"),
                             ("gz_spread / ebp", "Gilchrist-Zakrajsek spread and excess bond premium", "Federal Reserve (not on FRED)", "level"), ("term_premium_10y", "Kim-Wright 10-year term premium", "Fed via FRED", "monthly mean"),
                             ("equity_3m_ret / equity_12m_ret", "Nasdaq composite", "FRED", "3- and 12-month log return (the S&P 500 on FRED covers ten years only)"), ("usd_12m", "Broad dollar index", "Fed via FRED", "12-month log change; 1973-2019 and 2006- indexes spliced at the overlap"),
                             ("oil_3m / oil_12m", "WTI crude oil", "FRED", "3- and 12-month log change"), ("ppi_comm_12m", "PPI all commodities", "BLS via FRED", "12-month log change"), ("sloos_ci", "SLOOS net share tightening C&I standards", "Fed via FRED", "quarterly spread to months"),
                             ("mortgage30", "30-year mortgage rate", "Freddie Mac via FRED", "monthly mean")]:
    reg(5, short, name, src, tr)
R.h(3, "Block 5: financial conditions and risk pricing")
R.table(meta_table(5), "Block 5 indicators", small=True)
block_eda("fin", B5, "nfci", flip=True, title="Block 5, financial conditions (+ = looser)")

# =============================================================================== panel and factors
BLOCKS = {"infl": B1, "dist": B2.drop(columns="n_cats"), "exp": B3, "dem": B4, "fin": B5}
X = pd.concat(BLOCKS, axis=1); X = X[X.index >= START]; X = X.loc[:, (X.notna().mean() > 0.5) & (X.std() > 0)]
END = B1["pce_core_12m"].dropna().index[-1]; X = X[X.index <= END]; Z = zscore(X)
DICT = pd.DataFrame({"block": [b for b, _ in X.columns], "first_obs": [X[c].first_valid_index().date() for c in X.columns]}, index=[c for _, c in X.columns]); DICT.to_csv(CACHE / "data_dictionary.csv")

# =============================================================================== the factor model
R.h(2, "2. A dynamic factor model of the panel")
# Two nested specifications are estimated: global factors only, and global plus block factors.
# Parameters are estimated jointly, so a restricted information set cannot be obtained by
# zeroing factors out of the full fit; each needs its own EM run. Both run in a separate
# process (see dfm_spec) and are cached, keyed by a fingerprint of the panel.
dfm_spec.save_panel(CACHE / dfm_spec.PANEL_FILE, X, BLOCKS, END)
stamp = dfm_spec.stamp_of(X, END)
need = [s for s in dfm_spec.SPECS if REFIT or dfm_spec.load_params(CACHE / dfm_spec.params_file(s), stamp) is None]
if need:
    print(f"estimating the DFM ({', '.join(need)}) via fit_dfm.py; this is the slow step")
    subprocess.run([sys.executable, str(HERE / "fit_dfm.py")] + need, check=True)

REF = {"infl": ("infl", "pce_core_12m"), "dist": ("dist", "share_gt3_12m"), "exp": ("exp", "mich_1y"), "dem": ("dem", "payrolls_12m"), "fin": ("fin", "nfci")}
VARS = [c for _, c in X.columns]; BLK = pd.Series({c: b for b, c in X.columns})
Zfill = Z.fillna(0.0)

def read_fit(spec):
    """Load a cached fit and return its results object, loadings and transition, with the
    factors rescaled to unit standard deviation and signed as inflationary pressure.

    Loadings and dynamics are taken from the model's own estimates rather than re-derived by
    projecting the panel on the smoothed factors: the factors are collinear enough that such a
    projection is unstable (it produced loadings above 4 in standardized units)."""
    par = dfm_spec.load_params(CACHE / dfm_spec.params_file(spec), stamp)
    if par is None: sys.exit(f"no cached parameters for spec '{spec}'; run fit_dfm.py")
    mod = dfm_spec.build(X, BLOCKS, spec); res = mod.smooth(par)
    fac = ["Global.1", "Global.2"] + (list(BLOCKS) if spec == "full" else [])
    P = pd.Series(np.asarray(res.params), index=list(mod.param_names))
    lam = pd.DataFrame(0.0, index=VARS, columns=fac); A = pd.DataFrame(0.0, index=fac, columns=fac)
    for nm, v in P.items():
        if nm.startswith("loading."):
            f, var = nm[len("loading."):].split("->"); lam.loc[var, f] = v
        elif nm.startswith("L1.") and "eps" not in nm:
            src, dst = nm[3:].split("->")
            if src in fac and dst in fac: A.loc[dst, src] = v
    Fr = res.factors.smoothed[fac]
    sg = {"Global.1": np.sign(np.corrcoef(Fr["Global.1"], Z[REF["infl"]].fillna(0))[0, 1]),
          "Global.2": np.sign(np.corrcoef(Fr["Global.2"], Z["dem"].mean(axis=1).fillna(0))[0, 1])}
    for b in (BLOCKS if spec == "full" else []):
        sg[b] = np.sign(np.corrcoef(Fr[b], Z[REF[b]].fillna(0))[0, 1]) * (-1 if b == "fin" else 1)
    d = pd.Series({f: sg[f] * Fr[f].std() for f in fac})       # F = Fr / d, loadings scaled by d
    Fs = (Fr / d).rename(columns={"Global.1": "G1", "Global.2": "G2", **{b: f"B_{b}" for b in (BLOCKS if spec == "full" else [])}})
    lam = lam.mul(d, axis=1); lam.columns = Fs.columns; lam.index = Z.columns
    A = pd.DataFrame(np.diag(1 / d) @ A.values @ np.diag(d), index=Fs.columns, columns=Fs.columns)
    return dict(res=res, mod=mod, F=Fs, LAM=lam, A=A, meta=np.load(CACHE / dfm_spec.params_file(spec)))

FITS = {s: read_fit(s) for s in dfm_spec.SPECS}
FULL = FITS["full"]; dfm_res = FULL["res"]; F = FULL["F"]; Fz = F; LAM = FULL["LAM"]
LG = LAM[["G1", "G2"]]; LB = {b: LAM.loc[LAM.index.get_level_values(0) == b, f"B_{b}"] for b in BLOCKS}
com = lambda cols: pd.DataFrame(F[cols].values @ LAM[cols].values.T, index=Z.index, columns=Z.columns)
r2 = lambda c: (1 - (Zfill - c).var() / Zfill.var()).groupby(level=0).mean()
R2_G, R2_ALL = r2(com(["G1", "G2"])), r2(com(list(F.columns)))
acf1 = F.apply(lambda s_: s_.autocorr())
eig = np.abs(np.linalg.eigvals(FULL["A"].values)).max()
it_full = int(FULL["meta"]["iterations"]); conv_full = bool(FULL["meta"]["converged"])
top = lambda ld, k=3: ", ".join(f"{vname(c)} ({v:+.2f})" for c, v in ld.reindex(ld.abs().sort_values().index[-k:][::-1]).items())
R.p(TEXT["p15_the_factor_model_is_x_lambda"])
R.p(f"The panel has {X.shape[1]} variables from {X.index[0]:%Y-%m} to {END:%Y-%m}. EM converged in {it_full} iterations{'' if conv_full else ' (NOT CONVERGED)'}. "
    f"Averaged over the series in each block, the two global factors account for {', '.join(f'{b} {100*v:.0f}%' for b, v in R2_G.items())} of the variance, "
    f"and all seven factors together for {', '.join(f'{b} {100*v:.0f}%' for b, v in R2_ALL.items())}. Every factor is oriented so that higher = more inflationary pressure "
    f"(financial: looser) and scaled to unit standard deviation. First-order autocorrelation: {', '.join(f'{k} {v:.2f}' for k, v in acf1.items())}; "
    f"the largest eigenvalue of the factor VAR is {eig:.2f}, so the system is stationary.")
LGc = {g: LAM[g] for g in ("G1", "G2")}
def describe_global(l, k=10):
    tp = l.reindex(l.abs().sort_values(ascending=False).index[:k]); pos, neg = tp[tp > 0], tp[tp < 0]
    def side(x):
        if x.empty: return "none"
        g = pd.Series([f"{b_} {group_of(b_, c)}" for b_, c in x.index]).value_counts(); return ", ".join(f"{k_} ({int(n)})" for k_, n in g.items()) + "; e.g. " + ", ".join(vname(c) for c in x.index[:3])
    blk = pd.Series([b_ for b_, _ in tp.index]).value_counts(); return f"drawn from {', '.join(f'{k_} ({int(n)})' for k_, n in blk.items())} among its top-{k} loadings; positive on {side(pos)}; inverted: {side(neg)}"
# The generated descriptions go to the console; the report carries the hand-written reading in text.py.
print(f"[G1] {describe_global(LGc['G1'])}")
print(f"[G2] {describe_global(LGc['G2'])}")
for b in BLOCKS: print(f"[B_{b}] loads on: {top(LB[b], 5)}")
R.p(SECTION2["factors"])
R.p(SECTION2["blocks"])
R.bullets([BLOCK_FACTOR[b] for b in BLOCKS])
fig, axes = plt.subplots(1, 2, figsize=(15, 3.6))
F[["G1", "G2"]].plot(ax=axes[0], lw=1.2, color=["k", "tab:red"]); axes[0].set_title("Global factors (standardized)")
F[[c for c in F if c.startswith("B_")]].plot(ax=axes[1], lw=1); axes[1].set_title("Block-specific factors (standardized)")
for ax in axes: ax.axhline(0, color="grey", lw=.6); ax.legend(ncol=4, fontsize=8, frameon=False)
R.fig(fig, "factors", "Global and block-specific factors.")

# ------------------------------------------------------------------ targets and iterated forecasts
pce_core = m("PCEPILFE"); logp = np.log(pce_core)
Y = pd.DataFrame({f"pi_fut_{h}": 1200 / h * (logp.shift(-h) - logp) for h in H}); pi12 = 1200 / 12 * (logp - logp.shift(12))
for h in H: Y[f"dpi_{h}"] = Y[f"pi_fut_{h}"] - pi12; Y[f"decel_{h}"] = (Y[f"dpi_{h}"] < 0).astype(float).where(Y[f"dpi_{h}"].notna())
D = pd.concat([pd.DataFrame({"pi12": pi12, "pi3": B1["pce_core_3m"], "pi6": B1["pce_core_6m"]}), F, Y], axis=1).loc[F.index]
T = D.index[-1]; HF = [3, 6, 12, 24]
# pce_core_{h}m observed at t+h is exactly the annualized rate over the next h months at t, so the
# iterated h-step forecast of that variable is the forecast of the target, with its own interval.
R.h(3, "Forecasts")
# Forecasts are built from the 3-month rate at non-overlapping quarters: pce_core_3m at t+3, t+6,
# ... covers disjoint windows, so the average of the first k is the annualized rate over 3k months.
# Reading the h-month rate straight off pce_core_{h}m instead would respect no such identity: the
# model carries the overlapping aggregates as separate series, and their mechanical autocorrelation
# is absorbed by idiosyncratic AR(1) terms rising to 0.97 at 24 months, which then drive the
# forecast in place of the factors. Both constructions are evaluated below.
STEP = 3; KS = [1, 2, 4, 8]; HR = [STEP * k for k in KS]
IDX3 = VARS.index("pce_core_3m")

def quarter_paths(fit):
    """Forecast of pce_core_3m at t+3, t+6, ..., from the filtered state at every origin."""
    fr = fit["res"].filter_results
    Zd = np.asarray(fr.design)[:, :, 0]; A = np.asarray(fr.transition)[:, :, 0]
    a = np.asarray(fit["res"].filtered_state)
    mu = np.asarray(fit["mod"]._endog_mean).ravel(); sd = np.asarray(fit["mod"]._endog_std).ravel()
    return pd.DataFrame({k: mu[IDX3] + sd[IDX3] * ((Zd[IDX3] @ np.linalg.matrix_power(A, STEP * k)) @ a)
                         for k in range(1, max(KS) + 1)}, index=X.index)

def accum_paths(fit):
    Q = quarter_paths(fit)
    return {STEP * k: Q[list(range(1, k + 1))].mean(axis=1) for k in KS}

def direct_paths(fit):
    """The earlier construction, kept for comparison: the h-month rate read off its own series."""
    fr = fit["res"].filter_results
    Zd = np.asarray(fr.design)[:, :, 0]; A = np.asarray(fr.transition)[:, :, 0]
    a = np.asarray(fit["res"].filtered_state)
    mu = np.asarray(fit["mod"]._endog_mean).ravel(); sd = np.asarray(fit["mod"]._endog_std).ravel()
    out = {}
    for h in HR:
        i = VARS.index(f"pce_core_{h}m")
        out[h] = pd.Series(mu[i] + sd[i] * ((Zd[i] @ np.linalg.matrix_power(A, h)) @ a), index=X.index)
    return out

# The reported object is the 12-month rate at each future date, the measure most people know.
# For h < 12 it is the average of the realized (12-h)-month rate ending today and the forecast
# h-month forward rate; at 12 months it is the forward rate; at 24 months it is forward months
# 13-24. The same map applies to every model, so the comparison across them is like for like.
def twelve_at(fwd):
    r = lambda k: (1200 / k * (logp - logp.shift(k))).reindex(X.index)
    return {3: (9 * r(9) + 3 * fwd[3]) / 12, 6: (6 * r(6) + 6 * fwd[6]) / 12, 12: fwd[12], 24: 2 * fwd[24] - fwd[12]}
REALIZED_MONTHS = {3: 9, 6: 6, 12: 0, 24: 0}
QF = quarter_paths(FULL); TW = twelve_at(accum_paths(FULL))
FC = pd.DataFrame({f"{h}m": {"forecast": v.loc[T], "change vs current 12m": v.loc[T] - D.loc[T, "pi12"]} for h, v in TW.items()}).astype(object)
FC.loc["realized months in window"] = [REALIZED_MONTHS[h] for h in HR]
R.p(f"Core PCE is running at {D.loc[T, 'pi12']:.1f} percent over 12 months and {D.loc[T, 'pi3']:.1f} annualized over the latest 3 months. The model's forecast of the next eight quarters, annualized, is "
    f"{', '.join(f'{QF.loc[T, k]:.2f}' for k in range(1, max(KS) + 1))}. Combined with the months already realized, the 12-month rate is projected at "
    f"{' / '.join(f'{FC.loc['forecast', f'{h}m']:.1f}' for h in HR)} percent {'/'.join(str(h) for h in HR)} months from now. Within a year the window still contains realized months, so the near-term "
    f"path is largely arithmetic: the quarters ending January and April 2026 ran at {B1['pce_core_3m'].loc[T - pd.DateOffset(months=6)]:.1f} and {B1['pce_core_3m'].loc[T - pd.DateOffset(months=3)]:.1f} annualized, and the 12-month rate falls as they roll out.")
R.table(FC, f"Projected 12-month core PCE inflation at each horizon, origin {T:%B %Y} (percent)")
# The history line is the 12-month rate, so the forecast is shown in the same units: the implied
# 12-month rate at each future quarter, which is the average of the four quarters ending there.
# Out to 12 months that window still contains realized quarters; beyond, it is entirely forecast.
qhist = [B1["pce_core_3m"].loc[T - pd.DateOffset(months=3 * j)] for j in (3, 2, 1, 0)]
def implied_path(qf):
    """12-month rate at each future quarter from eight quarterly forecasts plus the realized quarters."""
    qseq = qhist + list(qf)
    impl = pd.Series({T + pd.DateOffset(months=3 * mth): float(np.mean(qseq[mth:mth + 4])) for mth in range(1, max(KS) + 1)})
    return pd.concat([pd.Series({T: D.loc[T, "pi12"]}), impl])
fig, ax = plt.subplots(figsize=(9, 3.6))
hist = pi12.loc["2015":]; ax.plot(hist.index, hist, color="k", lw=1.2, label="core PCE, 12m (realized)")
pth = implied_path([QF.loc[T, k] for k in range(1, max(KS) + 1)]); ax.plot(pth.index, pth.values, "-", color="tab:red", lw=1.4, label="implied 12m rate, forecast")
ax.axvline(T, color="grey", lw=.6, ls=":")
ax.axhline(2, color="grey", ls="--", lw=.7); ax.legend(frameon=False, ncol=2)
ax.set_title("Core PCE inflation, 12-month rate: history and implied forecast path (percent)")
R.fig(fig, "forecast", "Implied 12-month core PCE inflation every three months, to 24 months ahead. Windows ending within a year of the origin still contain realized quarters.")

R.h(3, "Sources of news in the current projection")
TARGET = T + pd.DateOffset(months=12)
Xflat = X.copy(); Xflat.columns = VARS
vintages = [T - pd.DateOffset(months=k) for k in range(12, -1, -1)]
def _stage_news():
    applied = {v: dfm_res.apply(Xflat.loc[:v]) for v in vintages}
    news_rows = {}
    for prev_v, now_v in zip(vintages[:-1], vintages[1:]):
        nw = applied[now_v].news(applied[prev_v], impact_date=TARGET, impacted_variable="pce_core_12m", comparison_type="previous")
        d_ = nw.details_by_impact.reset_index(); d_["block"] = d_["updated variable"].map(BLK)
        news_rows[now_v] = d_.groupby("block")["impact"].sum()
    NEWS = pd.DataFrame(news_rows).T.reindex(columns=list(BLOCKS)).fillna(0.0)
    return NEWS
NEWS = stage("news", _stage_news, key=(stamp, "full", len(vintages), str(TARGET.date())))
fig, ax = plt.subplots(figsize=(9, 3.8)); xpos = np.arange(len(NEWS)); bp, bn = np.zeros(len(NEWS)), np.zeros(len(NEWS))
for b in BLOCKS:
    v = NEWS[b].values; pos, neg = np.clip(v, 0, None), np.clip(v, None, 0)
    ax.bar(xpos, pos, bottom=bp, label=b); ax.bar(xpos, neg, bottom=bn, color=ax.patches[-1].get_facecolor()); bp += pos; bn += neg
ax.plot(xpos, NEWS.sum(axis=1).values, "k.", label="total")
ax.axhline(0, color="grey", lw=.6); ax.set_xticks(xpos); ax.set_xticklabels([d.strftime("%b%y") for d in NEWS.index], fontsize=8)
ax.legend(ncol=6, fontsize=8, frameon=False); ax.set_title(f"News contributions to the {TARGET:%b %Y} core PCE forecast, by block (pp)")
R.fig(fig, "news", "Monthly news contributions to the current 12-month-ahead forecast, by block.")
cum = NEWS.sum().sort_values()
R.p(f"Holding the target date fixed at {TARGET:%B %Y}, each month's data releases revise the 12-month forecast. Over the last {len(NEWS)} months the cumulative revision is "
    f"{NEWS.sum().sum():+.2f} pp: {', '.join(f'{b} {v:+.2f}' for b, v in cum.items())}. News is measured against the previous month's information set with the parameters held fixed.")


R.h(3, "Information sets")
AR_ORDER = min(range(1, 13), key=lambda p_: AutoReg(B1["pce_core_1m"].loc[START:].dropna().rename("y"), lags=p_).fit().aic)
def ar_month_paths():
    """Monthly forecasts 1..24 ahead from every origin, AR(p) on the monthly rate."""
    y = B1["pce_core_1m"].loc[START:].dropna().rename("y"); fit = AutoReg(y, lags=AR_ORDER).fit()   # same 1985+ sample as the panel
    c, phi = fit.params.iloc[0], fit.params.iloc[1:].values; rows = {}
    for t_ in range(AR_ORDER, len(y)):
        hist_ = list(y.iloc[t_ - AR_ORDER + 1:t_ + 1].values[::-1]); path = []
        for _ in range(max(HR)):
            nxt = c + float(np.dot(phi, hist_[:AR_ORDER])); path.append(nxt); hist_ = [nxt] + hist_
        rows[y.index[t_]] = path
    return pd.DataFrame.from_dict(rows, orient="index", columns=range(1, max(HR) + 1)).reindex(X.index)
ARM = ar_month_paths()
AR = {h: ARM[list(range(1, h + 1))].mean(axis=1) for h in HR}
ARQ = pd.DataFrame({k: ARM[[3 * k - 2, 3 * k - 1, 3 * k]].mean(axis=1) for k in range(1, max(KS) + 1)})   # quarterly, like quarter_paths
PATHS = {"M1 time series": twelve_at(AR), "M2 global factors": twelve_at(accum_paths(FITS["global"])), "M3 global + block": twelve_at(accum_paths(FULL))}
DPATHS = {"M1 time series": twelve_at(AR), "M2 global factors": twelve_at(direct_paths(FITS["global"])), "M3 global + block": twelve_at(direct_paths(FULL))}
def rmse_table(paths):
    rows = []
    for h in HR:
        real = X[("infl", "pce_core_12m")].shift(-h)          # the 12-month rate observed h months later
        errs = {k: (real - v[h]).loc[OOS_START:].dropna() for k, v in paths.items()}
        common = None
        for e in errs.values(): common = e.index if common is None else common.intersection(e.index)
        for k, e in errs.items(): rows.append(dict(h=f"{h}m", model=k, RMSE=np.sqrt((e.loc[common] ** 2).mean()), n=len(common)))
    t = pd.DataFrame(rows)
    return t.pivot(index="model", columns="h", values="RMSE").loc[list(paths)][[f"{h}m" for h in HR]], int(t["n"].iloc[0])
OOS, N_OOS = rmse_table(PATHS); OOS_D, _ = rmse_table(DPATHS)
REL = OOS / OOS.loc["M1 time series"]
NOW = pd.DataFrame({f"{h}m": {k: v[h].loc[T] for k, v in PATHS.items()} for h in HR}).loc[list(PATHS)]
PROB = pd.DataFrame({f"{h}m": {"P(lower) model": stats.norm.cdf((D.loc[T, "pi12"] - FC.loc["forecast", f"{h}m"]) / OOS.loc["M3 global + block", f"{h}m"]),
                               "unconditional": D[f"decel_{h}"].mean() if f"decel_{h}" in D else np.nan} for h in HR})
R.p(f"How much of the projection depends on the breadth of the panel? Three nested information sets, all iterated: M1 an AR({AR_ORDER}) on monthly core PCE chosen by AIC; M2 the two global factors; M3 the global and block factors. M2 and M3 are separately "
    f"estimated dynamic factor models, since the parameters of a restricted set cannot be read off the full fit. Forecasts are recursive from {OOS_START[:4]}: at each origin the filtered state uses "
    f"data through that month only, but the parameters are estimated once on the full sample, which is a look-ahead that favours the factor models. Latest-vintage data throughout, so revisions are ignored.")
R.table(NOW, f"Projected 12-month core PCE inflation by information set, origin {T:%B %Y} (percent)")
R.table(pd.concat({"RMSE": OOS, "relative to M1": REL}, axis=1), f"Pseudo-out-of-sample RMSE of the 12-month rate h months ahead, {OOS_START[:4]} onward, {N_OOS} origins at 3m; forecasts accumulated from the 3-month rate. Within a year the window contains realized months, so errors are mechanically smaller at short horizons")
R.table(OOS_D, "The same evaluation reading each h-month rate off its own series instead of accumulating; the gap is the cost of ignoring the accounting identity")

# second forecast figure: the same implied 12-month path under each information set
fig, ax = plt.subplots(figsize=(9, 3.6))
hist = pi12.loc["2015":]; ax.plot(hist.index, hist, color="k", lw=1.2, label="core PCE, 12m (realized)")
for lab, qf, sty in [("M3 global + block", [QF.loc[T, k] for k in range(1, max(KS) + 1)], dict(color="tab:red", lw=1.6)),
                     ("M2 global factors", [quarter_paths(FITS["global"]).loc[T, k] for k in range(1, max(KS) + 1)], dict(color="tab:orange", lw=1.2, ls="--")),
                     ("M1 time series", [ARQ.loc[T, k] for k in range(1, max(KS) + 1)], dict(color="tab:blue", lw=1.2, ls=":"))]:
    pth = implied_path(qf); ax.plot(pth.index, pth.values, label=lab, **sty)
ax.axvline(T, color="grey", lw=.6, ls=":"); ax.axhline(2, color="grey", ls="--", lw=.7); ax.legend(frameon=False, ncol=4, fontsize=8)
ax.set_title("Core PCE inflation, 12-month rate: implied forecast path by information set (percent)")
R.fig(fig, "forecast_sets", "Implied 12-month core PCE inflation under each information set. Paths coincide over the first quarter, where nine of twelve months are realized, and diverge as the forecast share of the window grows.")
# =============================================================================== disagreement
R.h(2, "3. Agreement and disagreement")
Fz7 = Fz.dropna(); D_sd = Fz7.std(axis=1); C1, lamb, exC, _ = pca(Fz7, 1); RESID = Fz7 - pd.DataFrame(np.outer(C1["PC1"], lamb["PC1"]), index=Fz7.index, columns=Fz7.columns); D_res = np.sqrt((RESID ** 2).mean(axis=1))
MEAS = ["cpi", "cpi_core", "pce", "pce_core", "cpi_median", "cpi_trim", "pce_trim", "cpi_sticky", "cpi_core_sticky", "cpi_flex", "cpi_core_flex"]
meas12 = B1[[f"{t}_12m" for t in MEAS]]; meas3 = B1[[f"{t}_3m" for t in MEAS]]; D_infl12 = meas12.std(axis=1); D_infl3 = meas3.std(axis=1)
DIS = pd.DataFrame({"D_sd (A)": D_sd, "D_res (B)": D_res, "D_infl_12m (C)": D_infl12, "D_infl_3m (C)": D_infl3})
R.p(TEXT["p03_do_today_s_indicators_agree_ab"])
R.p(f"A: cross-sectional SD of the seven standardized factors. B: residual RMS after fitting one common factor to the seven signals (it explains {100*exC[0]:.0f}% of their variance): how poorly can today's signals be reconciled by one common state? "
    "C: SD across the eleven alternative inflation measures (pp). D: breadth versus dispersion within the distribution block.")
R.table(pd.DataFrame({"current": DIS.iloc[-1], "percentile": [pct_rank(DIS[c]) for c in DIS], "median": DIS.median(), "p90": DIS.quantile(.9)}), "Disagreement measures, current value and history")
fig, axes = plt.subplots(1, 2, figsize=(15, 3.6)); ax = axes[0]; ax.plot(D_res.index, D_res, color="k", lw=1.1, label="B: one-factor residual RMS"); ax.plot(D_sd.index, D_sd, color="tab:blue", lw=.9, alpha=.7, label="A: SD across factors")
ax.axhline(D_res.median(), color="grey", ls="--", lw=.7); ax.scatter([D_res.index[-1]], [D_res.iloc[-1]], color="red", zorder=5); ax.set_title(f"Disagreement across the seven signals; today at the {ordinal(pct_rank(D_res))} percentile (B)"); ax.legend(frameon=False)
ax = axes[1]; r_now = RESID.iloc[-1].sort_values(); ax.barh(r_now.index, r_now, color=np.where(r_now > 0, "tab:red", "tab:blue")); ax.axvline(0, color="grey", lw=.6); ax.set_title(f"Residual by signal, {RESID.index[-1]:%b %Y} (z; + = more inflationary than the common state implies)")
R.fig(fig, "disagreement", "Cross-block disagreement and the current residual by signal.")
fig, axes = plt.subplots(1, 2, figsize=(15, 3.6)); ax = axes[0]; ax.plot(D_infl12.index, D_infl12, color="k", lw=1, label="12m measures"); ax.plot(D_infl3.index, D_infl3, color="tab:orange", lw=.9, label="3m measures")
ax.scatter([D_infl12.index[-1]], [D_infl12.iloc[-1]], color="red", zorder=5); ax.set_title("C: SD across alternative inflation measures (pp)"); ax.legend(frameon=False)
ax = axes[1]; bsh, dsp = B2["share_gt3_3m"], B2["xs_sd_3m"]; ok = bsh.notna() & dsp.notna(); ax.scatter(bsh[ok], dsp[ok], s=8, color="lightgrey"); ax.scatter(bsh[ok].iloc[-12:], dsp[ok].iloc[-12:], s=14, color="tab:blue", label="last 12 months")
ax.scatter([bsh.iloc[-1]], [dsp.iloc[-1]], s=50, color="red", label=f"{bsh.index[-1]:%b %Y}"); ax.axvline(bsh.median(), color="grey", ls="--", lw=.6); ax.axhline(dsp.median(), color="grey", ls="--", lw=.6)
ax.set_xlabel("share of categories above 3% (3m ann.)"); ax.set_ylabel("cross-sectional SD (3m ann.)"); ax.set_title("D: broad rise (right) vs dispersed relative-price moves (top)"); ax.legend(frameon=False)
R.fig(fig, "disagreement_inflation", "Disagreement among inflation measures, and breadth versus dispersion.")

# =============================================================================== analogs
R.h(2, "4. Historical analogs")
def analogs(V, k=15, exclude_months=24, min_gap=6):
    v0 = V.iloc[-1]; hist = V[V.index <= V.index[-1] - pd.DateOffset(months=exclude_months)].dropna(); dist = np.sqrt(((hist - v0) ** 2).sum(axis=1)).sort_values(); picked = []
    for t in dist.index:
        if all(abs((t - q).days) > min_gap * 30 for q in picked): picked.append(t)
        if len(picked) == k: break
    out = pd.DataFrame({"distance": dist[picked], "core PCE 12m then": pi12.reindex(picked)})
    for h in (3, 6, 12): out[f"next {h}m"] = Y[f"pi_fut_{h}"].reindex(picked)
    out["change 12m ahead"] = out["next 12m"] - out["core PCE 12m then"]; out["D_res then"] = D_res.reindex(picked); out.index = [d.strftime("%Y-%m") for d in out.index]; return out
A1 = analogs(Fz7); A2 = analogs(RESID); a1 = A1["change 12m ahead"]; outc = np.where(a1 < -0.5, "sustained disinflation", np.where(a1 > 0.5, "reacceleration", "mixed/flat"))
R.p(TEXT["p04_when_in_the_past_did_the_confi"])
R.p(f"Nearest neighbors of today's standardized factor vector (Euclidean distance, excluding the last 24 months, at most one match per six-month window). Across the 15 analogs the median subsequent 12m core PCE is {A1['next 12m'].median():.2f} "
    f"(median change {a1.median():+.2f} pp, decelerating in {(a1 < 0).mean():.0%}). Matching on the pattern of disagreement instead gives {', '.join(A2.index[:5])} (median change {A2['change 12m ahead'].median():+.2f}). Not causal.")
R.table(A1, f"Analogs on the factor vector, origin {T:%b %Y}")

# =============================================================================== supply vs demand
R.h(2, "5. Supply-like versus demand-like episodes and disagreement")
hi = lambda s_: s_ > s_.median(); BPCd = pd.DataFrame(BPC); infl_pc, dem_pc = pi12.reindex(BPCd.index), BPCd["dem"]
regime = pd.Series(np.select([hi(infl_pc) & hi(dem_pc), hi(infl_pc) & ~hi(dem_pc), ~hi(infl_pc) & hi(dem_pc)], ["demand-like (infl high, demand high)", "adverse-supply-like (infl high, demand weak)", "favorable-supply-like (infl low, demand strong)"],
                             "weak-demand (infl low, demand weak)"), index=BPCd.index).reindex(D_res.index)
reg_tab = pd.DataFrame({"months": regime.value_counts(), "D_res mean": D_res.groupby(regime).mean(), "D_res median": D_res.groupby(regime).median(), "share D_res > p75": D_res.groupby(regime).apply(lambda s_: (s_ > D_res.quantile(.75)).mean()),
                        "next-12m change, median": Y["dpi_12"].reindex(D_res.index).groupby(regime).median()})
Xc = pd.DataFrame({"headline_core_gap": B1["pce_12m"] - B1["pce_core_12m"], "flex_less_sticky": B1["cpi_flex_12m"] - B1["cpi_sticky_12m"], "xs_sd_3m": B2["xs_sd_3m"], "oil_12m": B5["oil_12m"], "abs_oil_12m": B5["oil_12m"].abs()}).reindex(D_res.index)
corr_rows = {c: {"corr": D_res.corr(Xc[c]), "t (HAC)": ols(D_res, zscore(Xc[[c]]), hac=12).tvalues[c]} for c in Xc.columns}
prow = {}
for h in [3, 6, 12]:
    Xp = pd.DataFrame({"D_res": zscore(D_res), "pi12": pi12, "B_dem": F["B_dem"]}).reindex(D_res.index); r = ols(Y[f"dpi_{h}"].reindex(D_res.index), Xp, hac=h)
    prow[f"{h}m"] = {"beta D_res (pp per sd)": r.params["D_res"], "t": r.tvalues["D_res"], "gamma pi12": r.params["pi12"], "t ": r.tvalues["pi12"], "delta B_dem": r.params["B_dem"], "t  ": r.tvalues["B_dem"], "R2": r.rsquared}
PRED = pd.DataFrame(prow)
R.p(TEXT["p17_hypothesis_disagreement_betwe"])
R.p(f"Regimes from core PCE 12m and the demand block's first PC, each above or below its median. Current regime: {regime.iloc[-1]}. Descriptive only; a sign-restricted VAR or external instruments would be the structural extension.")
R.table(reg_tab, "Disagreement by regime"); R.table(pd.DataFrame(corr_rows).T, "Contemporaneous correlates of disagreement (standardized regressors, HAC t)")
R.table(PRED, "Subsequent change in core PCE on disagreement, current inflation, and the demand factor (HAC t)")

# =============================================================================== additional evidence
R.h(2, "6. Additional evidence")
R.p(TEXT["p05_four_further_pieces_of_evidenc"])
n_dec = int((meas3.loc[T].values < meas12.loc[T].values).sum())   # PROB is built in section 2, from the accumulated forecast and its out-of-sample RMSE
CANDS = {"core PCE 3m": B1["pce_core_3m"], "core PCE 6m": B1["pce_core_6m"], "core PCE 3m-12m": B1["pce_core_3m"] - B1["pce_core_12m"], "core CPI 12m": B1["cpi_core_12m"], "median CPI 12m": B1["cpi_median_12m"], "median CPI 3m": B1["cpi_median_3m"],
         "trimmed PCE 12m": B1["pce_trim_12m"], "trimmed CPI 12m": B1["cpi_trim_12m"], "sticky CPI 12m": B1["cpi_sticky_12m"], "flexible CPI 12m": B1["cpi_flex_12m"], "breadth >3% (3m)": B2["share_gt3_3m"],
         "breadth >3% (12m)": B2["share_gt3_12m"], "xs dispersion (3m)": B2["xs_sd_3m"], "xs median (3m)": B2["xs_median_3m"], "SPF dispersion": B3["spf_cpi_4q_sd"], "Michigan 1y": B3["mich_1y"]}
def _stage_race():
    DC = pd.concat([D[["pi12", "pi3"] + [f"pi_fut_{h}" for h in H] + [f"dpi_{h}" for h in H]], pd.DataFrame(CANDS)], axis=1).loc[D.index]; race = []
    for name in CANDS:
        row = {"measure": name, "corr with core PCE 12m": DC[name].corr(DC["pi12"])}
        for h in [3, 6, 12]:
            base = oos_forecast(DC, f"pi_fut_{h}", ["pi12"], h); alt = oos_forecast(DC, f"pi_fut_{h}", ["pi12", name], h); e0 = (DC[f"pi_fut_{h}"] - base).dropna(); e1 = (DC[f"pi_fut_{h}"] - alt).dropna(); idx = e0.index.intersection(e1.index)
            row[f"rel RMSFE {h}m"] = np.sqrt((e1[idx] ** 2).mean() / (e0[idx] ** 2).mean()); row[f"t {h}m"] = ols(DC[f"dpi_{h}"], DC[["pi12", "pi3", name]], hac=h).tvalues[name]
        race.append(row)
    RACE = pd.DataFrame(race).set_index("measure")
    return RACE
RACE = stage("race", _stage_race, key=(stamp, OOS_START, tuple(CANDS)))
RACE["type"] = np.where((RACE[[f"rel RMSFE {h}m" for h in (3, 6, 12)]] < 0.98).sum(axis=1) >= 2, "forward-looking", np.where(RACE["corr with core PCE 12m"].abs() > 0.8, "contemporaneous", "no gain"))
b12 = B2["share_gt3_12m"].reindex(D.index); hiB = b12 > b12.quantile(.75); loB = b12 < b12.quantile(.25)
cond = pd.DataFrame({k: [msk.sum(), D.loc[msk, "pi12"].mean(), D.loc[msk, "pi_fut_12"].mean(), (D.loc[msk, "pi_fut_12"] > 2.5).mean(), D.loc[msk, "dpi_12"].mean(), (D.loc[msk, "dpi_12"] < 0).mean()]
                     for k, msk in [("high breadth (top quartile)", hiB), ("low breadth (bottom quartile)", loB), ("all", pd.Series(True, index=D.index))]},
                    index=["months", "core PCE 12m then", "core PCE next 12m", "P(next 12m > 2.5%)", "mean change", "P(decelerate)"])
gap = (B1["pce_core_3m"] - B1["pce_core_12m"]).reindex(D.index); events = []
for t in gap[gap < -1.0].index:
    if not events or (t - events[-1]).days > 180: events.append(t)
EV = pd.DataFrame([{"date": t.strftime("%Y-%m"), "core 12m": pi12.loc[t], "gap": gap.loc[t], "12m change ahead": Y["dpi_12"].get(t, np.nan), "turning point": Y["dpi_12"].get(t, np.nan) <= -0.5,
                    "reaccelerated within 6m": bool((B1["pce_core_3m"].loc[t:t + pd.DateOffset(months=6)] > pi12.loc[t]).any())} for t in events]).set_index("date"); ev_hist = EV.dropna(subset=["12m change ahead"])
# Under the iterated forecast a block acts through the factor VAR, not through a coefficient on
# inflation, so its contribution is measured as the M3-minus-M2 difference in the projection.
BLOCK_GAIN = pd.Series({f"{h}m": NOW.loc["M3 global + block", f"{h}m"] - NOW.loc["M2 global factors", f"{h}m"] for h in HF})
drivers = {b: (LB[b] * Z[b].iloc[-1].fillna(0)).sort_values(key=abs, ascending=False).head(5) for b in BLOCKS}
fin_vars = ["fedfunds", "real_10y_clev", "dgs10", "nfci", "vix", "baa_spread", "ebp", "term_premium_10y", "equity_12m_ret", "usd_12m", "mortgage30", "sloos_ci"]; tight_if_high = {"fedfunds", "real_10y_clev", "dgs10", "nfci", "vix", "baa_spread", "ebp", "mortgage30", "sloos_ci", "usd_12m", "term_premium_10y"}
fin_now = pd.DataFrame({"latest": [B5[c].dropna().iloc[-1] for c in fin_vars], "percentile": [pct_rank(B5[c]) for c in fin_vars]}, index=fin_vars); fin_now["side"] = ["tight" if ((c in tight_if_high) == (p > 50)) else "loose" for c, p in zip(fin_vars, fin_now["percentile"])]
B3x = B3.assign(mich_less_spf=MICH_LESS_SPF); ev_ = ["mich_1y", "spf_cpi_4q", "clev_1y", "bei_5y", "bei_5y5y", "spf_cpi_10y", "spf_cpi_4q_sd", "mich_less_spf"]
exp_now = pd.DataFrame({"latest": [B3x[c].dropna().iloc[-1] for c in ev_], "percentile": [pct_rank(B3x[c]) for c in ev_]}, index=ev_)
dem_now = pd.DataFrame({"latest": [B4[c].dropna().iloc[-1] for c in ["unrate", "vu_ratio", "ahe_12m", "real_pce_6m"]], "percentile": [pct_rank(B4[c]) for c in ["unrate", "vu_ratio", "ahe_12m", "real_pce_6m"]]}, index=["unrate", "vu_ratio", "ahe_12m", "real_pce_6m"])
R.table(PROB, "Probability that core PCE inflation is lower over the next h months than the current 12m rate"); R.table(RACE[[f"rel RMSFE {h}m" for h in (3, 6, 12)] + ["corr with core PCE 12m", "type"]], "Horse race: each statistic added to core PCE 12m; relative RMSFE < 1 beats core PCE 12m alone")
R.table(cond, "Conditional history by breadth (share of categories above 3% at 12m)"); R.table(EV, "Spells with core PCE 3m at least 1 pp below 12m")

# =============================================================================== answers
R.h(2, "7. Answers")
z_now = Fz.iloc[-1]; pctF = {c: pct_rank(Fz[c]) for c in F.columns}; h12 = {"forecast": FC.loc["forecast", "12m"], "change": FC.loc["change vs current 12m", "12m"], "current": D.loc[T, "pi12"],
       "direction": "decelerating" if FC.loc["change vs current 12m", "12m"] < 0 else "accelerating"}; lat12 = meas12.loc[T]; common12 = float(lat12.median())
above = [vname(c) for c in lat12.index[lat12 > common12 + 0.25]]; below = [vname(c) for c in lat12.index[lat12 < common12 - 0.25]]
sh = lambda k, h: B2[f"share_gt{k}_{h}m"].dropna().iloc[-1]; b3 = B2["share_gt3_3m"].dropna(); b12s = B2["share_gt3_12m"].dropna(); news_cum = NEWS.sum().sort_values()
rb, rb12, rmed, rtr = RACE.loc["breadth >3% (3m)"], RACE.loc["breadth >3% (12m)"], RACE.loc["median CPI 12m"], RACE.loc["trimmed PCE 12m"]; best = {h: RACE[f"rel RMSFE {h}m"].idxmin() for h in (3, 6, 12)}
p12 = PROB.loc["P(lower) model", "12m"]; rt = reg_tab["D_res mean"]; loose_share = (fin_now["side"] == "loose").mean()
pos_part = ", ".join(f"{k} {v:+.2f}" for k, v in news_cum[news_cum > 0.005].items()) or "none"; neg_part = ", ".join(f"{k} {v:+.2f}" for k, v in news_cum[news_cum < -0.005].items()) or "none"
fc_str = " / ".join(f"{FC.loc['forecast', f'{h}m']:.1f}" for h in HR)          # "2.5 / 2.7 / 2.6 / 2.7"
pl_str = " / ".join(f"{PROB.loc['P(lower) model', f'{h}m']:.0%}" for h in HR)
hs_str = "/".join(str(h) for h in HR)
def qa(title, lines): R.h(3, title); R.bullets(lines)
qa("1. Best estimate of underlying inflation today", [
   f"Core PCE {B1['pce_core_3m'].loc[T]:.1f} / {B1['pce_core_6m'].loc[T]:.1f} / {B1['pce_core_12m'].loc[T]:.1f} (3m/6m/12m); median CPI {B1['cpi_median_12m'].loc[T]:.1f}, trimmed PCE {B1['pce_trim_12m'].loc[T]:.1f}, sticky {B1['cpi_sticky_12m'].loc[T]:.1f}, flexible {B1['cpi_flex_12m'].loc[T]:.1f} (12m).",
   f"Common signal across the {len(MEAS)} 12m measures (median): {common12:.1f}. Above it by more than 0.25: {', '.join(above) or 'none'}; below: {', '.join(below) or 'none'}.",
   f"Disagreement among measures at the {ordinal(pct_rank(D_infl12))} percentile (12m) and {ordinal(pct_rank(D_infl3))} (3m): {'unusually high' if pct_rank(D_infl12) > 80 else 'unusually low' if pct_rank(D_infl12) < 20 else 'not unusual'}."])
qa("2. Accelerating or decelerating", [
   f"{n_dec} of {len(MEAS)} measures have 3m below 12m; core PCE 3m-12m gap {(B1['pce_core_3m'] - B1['pce_core_12m']).loc[T]:+.1f} pp, 6m-12m {(B1['pce_core_6m'] - B1['pce_core_12m']).loc[T]:+.1f}.",
   f"Iterated DFM forecast of the 12-month rate: {fc_str} at {hs_str} months ahead, against {h12['current']:.1f} today: {h12['direction']} ({h12['change']:+.2f} pp at 12m).",
   f"P(12-month rate below today's): {pl_str} at {hs_str} months ahead (unconditional about {PROB.loc['unconditional', '12m']:.0%})."])
qa("3. Breadth", [
   f"Share of categories above 2/3/4/5%: {100*sh(2,3):.0f} / {100*sh(3,3):.0f} / {100*sh(4,3):.0f} / {100*sh(5,3):.0f}% at 3m; {100*sh(2,12):.0f} / {100*sh(3,12):.0f} / {100*sh(4,12):.0f} / {100*sh(5,12):.0f}% at 12m.",
   f"Breadth (above 3%) is {'falling' if b3.iloc[-1] < b3.iloc[-4] else 'rising'} over three months at 3m ({100*(b3.iloc[-1]-b3.iloc[-4]):+.0f} pp) and {'falling' if b12s.iloc[-1] < b12s.iloc[-13] else 'rising'} over a year at 12m ({100*(b12s.iloc[-1]-b12s.iloc[-13]):+.0f} pp).",
   f"Historical position: breadth {ordinal(pct_rank(b3))} percentile (3m), {ordinal(pct_rank(b12s))} (12m); cross-sectional SD {ordinal(pct_rank(B2['xs_sd_3m']))}; upper-tail share {ordinal(pct_rank(B2['upper_tail_share_3m']))}.",
   f"Reading: {'broad-based' if pct_rank(b12s) > 60 else 'concentrated' if pct_rank(b12s) < 40 else 'middling'} at 12m; at 3m the rise is {'concentrated in a few categories' if pct_rank(B2['upper_tail_share_3m']) > 70 else 'not unusually concentrated'}."])
qa("4. Does breadth predict future inflation", [
   f"High-breadth months (top quartile): core PCE averaged {cond.loc['core PCE next 12m', 'high breadth (top quartile)']:.1f}% over the next 12m and stayed above 2.5% in {cond.loc['P(next 12m > 2.5%)', 'high breadth (top quartile)']:.0%} of cases, against {cond.loc['core PCE next 12m', 'low breadth (bottom quartile)']:.1f}% and {cond.loc['P(next 12m > 2.5%)', 'low breadth (bottom quartile)']:.0%} for low breadth. Inflation stayed elevated, but it was already high.",
   f"Given core PCE 12m and 3m, breadth (3m) has HAC t = {rb['t 3m']:+.1f} / {rb['t 6m']:+.1f} / {rb['t 12m']:+.1f} for the 3/6/12m change and relative RMSFE {rb['rel RMSFE 3m']:.2f} / {rb['rel RMSFE 6m']:.2f} / {rb['rel RMSFE 12m']:.2f}: little incremental content. Breadth at 12m: t {rb12['t 12m']:+.1f}, rel RMSFE {rb12['rel RMSFE 12m']:.2f}.",
   f"Against median CPI (rel RMSFE 12m {rmed['rel RMSFE 12m']:.2f}) and trimmed PCE ({rtr['rel RMSFE 12m']:.2f}), breadth is {'more' if rb['rel RMSFE 12m'] < min(rmed['rel RMSFE 12m'], rtr['rel RMSFE 12m']) else 'not more'} useful. Adding the block factors to the global-factor model moves the 12m projection by {BLOCK_GAIN['12m']:+.2f} pp."])
qa("5. Most useful current statistics", [
   f"Best single addition to core PCE 12m by horizon: 3m {best[3]} ({RACE.loc[best[3], 'rel RMSFE 3m']:.2f}); 6m {best[6]} ({RACE.loc[best[6], 'rel RMSFE 6m']:.2f}); 12m {best[12]} ({RACE.loc[best[12], 'rel RMSFE 12m']:.2f}). Gains are small everywhere.",
   f"Forward-looking (beats core PCE 12m alone at two or more horizons): {', '.join(RACE.index[RACE['type'] == 'forward-looking']) or 'none'}. Contemporaneous summaries (|corr| > 0.8, no out-of-sample gain): {', '.join(RACE.index[RACE['type'] == 'contemporaneous']) or 'none'}."])
qa("6. Recent favorable readings: signal or noise", [
   f"Spells with core PCE 3m at least 1 pp below 12m: {len(ev_hist)} since {D.index[0].year}; a genuine turning point (12m rate down at least 0.5 pp a year later) in {ev_hist['turning point'].mean():.0%}, reacceleration within six months in {ev_hist['reaccelerated within 6m'].mean():.0%}.",
   f"Today's gap is {gap.iloc[-1]:+.2f} pp ({'an event' if gap.iloc[-1] < -1 else 'below the event threshold'}). The factor-space analogs saw a median 12m change of {a1.median():+.2f} pp with deceleration in {(a1 < 0).mean():.0%} of cases: {'closer to a sustained disinflation' if a1.median() < -0.3 else 'closer to a soft patch than a sustained disinflation' if a1.median() > -0.1 else 'mixed'}."])
qa("7. Are financial conditions restrictive", [
   f"Financial factor (+ = looser) {z_now['B_fin']:+.2f} z, {ordinal(pctF['B_fin'])} percentile: {'unusually loose' if pctF['B_fin'] > 85 else 'on the loose side of history' if pctF['B_fin'] > 65 else 'unusually tight' if pctF['B_fin'] < 15 else 'on the tight side of history' if pctF['B_fin'] < 35 else 'near its historical middle'}.",
   f"{loose_share:.0%} of {len(fin_vars)} indicators sit on the loose side of their median: loose = {', '.join(fin_now.index[fin_now['side'] == 'loose'])}; tight = {', '.join(fin_now.index[fin_now['side'] == 'tight'])}.",
   f"Financial conditions reach inflation only through the factor VAR; the block factors together move the 12m projection by {BLOCK_GAIN['12m']:+.2f} pp relative to the global-only model."])
qa("8. Is demand pressure still inflationary", [
   f"Demand factor {z_now['B_dem']:+.2f} z ({ordinal(pctF['B_dem'])} percentile); G2 {z_now['G2']:+.2f}. the block factors together move the 12m projection by {BLOCK_GAIN['12m']:+.2f} pp relative to the global-only model.",
   f"Drivers today (loading x z): {', '.join(f'{vname(k)} {v:+.2f}' for k, v in drivers['dem'].items())}. Unemployment {dem_now.loc['unrate', 'latest']:.1f} ({ordinal(dem_now.loc['unrate', 'percentile'])} pct), V/U {dem_now.loc['vu_ratio', 'latest']:.2f}, wages {dem_now.loc['ahe_12m', 'latest']:.1f}%, real PCE 6m {dem_now.loc['real_pce_6m', 'latest']:.1f}%."])
qa("9. Are expectations a problem", [
   f"Levels: Michigan 1y {exp_now.loc['mich_1y', 'latest']:.1f} ({ordinal(exp_now.loc['mich_1y', 'percentile'])} pct), SPF 4q {exp_now.loc['spf_cpi_4q', 'latest']:.1f} ({ordinal(exp_now.loc['spf_cpi_4q', 'percentile'])}), 5y breakeven {exp_now.loc['bei_5y', 'latest']:.2f} ({ordinal(exp_now.loc['bei_5y', 'percentile'])}), 5y5y {exp_now.loc['bei_5y5y', 'latest']:.2f} ({ordinal(exp_now.loc['bei_5y5y', 'percentile'])}), SPF 10y {exp_now.loc['spf_cpi_10y', 'latest']:.1f}.",
   f"Disagreement: SPF cross-sectional SD {exp_now.loc['spf_cpi_4q_sd', 'latest']:.2f} ({ordinal(exp_now.loc['spf_cpi_4q_sd', 'percentile'])} pct); households minus professionals {exp_now.loc['mich_less_spf', 'latest']:+.1f} pp ({ordinal(exp_now.loc['mich_less_spf', 'percentile'])}).",
   f"Predictive content: SPF dispersion as a single addition to core PCE 12m, rel RMSFE {RACE.loc['SPF dispersion', 'rel RMSFE 12m']:.2f} (t {RACE.loc['SPF dispersion', 't 12m']:+.1f}); Michigan 1y {RACE.loc['Michigan 1y', 'rel RMSFE 12m']:.2f} (t {RACE.loc['Michigan 1y', 't 12m']:+.1f}). "
   f"The block is the {'most' if RESID.iloc[-1].idxmax() == 'B_exp' else 'not the most'} inflationary residual in the disagreement decomposition ({RESID.iloc[-1]['B_exp']:+.2f})."])
qa("10. What drives the current forecast", [
   f"12m projection {FC.loc['forecast', '12m']:.1f} against a current 12m rate of {D.loc[T, 'pi12']:.1f}; the block factors account for {BLOCK_GAIN['12m']:+.2f} pp of it relative to the global-only model.",
   f"Over the last {len(NEWS)} months, news revised this projection by {NEWS.sum().sum():+.2f} pp. Pushing up: {pos_part}; pushing down: {neg_part}."])
qa("11. Agreement or disagreement", [
   f"Cross-block disagreement {D_res.iloc[-1]:.2f}, {ordinal(pct_rank(D_res))} percentile (SD across factors {ordinal(pct_rank(D_sd))}). Outliers: {', '.join(f'{k} {v:+.2f}' for k, v in RESID.iloc[-1].sort_values(key=abs, ascending=False).head(3).items())}.",
   f"Within inflation measures {ordinal(pct_rank(D_infl12))} percentile; between price and non-price blocks {ordinal(pct_rank(D_res))}: {'mainly between price and non-price signals' if pct_rank(D_res) > pct_rank(D_infl12) + 15 else 'mainly within the inflation measures' if pct_rank(D_infl12) > pct_rank(D_res) + 15 else 'similar within and between'}; overall {'historically unusual' if pct_rank(D_res) > 85 else 'not historically unusual'}."])
qa("12. Historical analogs", [
   f"Closest configurations: {', '.join(A1.index[:6])}.",
   f"Subsequent 3/6/12m core PCE (median) {A1['next 3m'].median():.1f} / {A1['next 6m'].median():.1f} / {A1['next 12m'].median():.1f}; 12m change median {a1.median():+.2f}. Outcomes: sustained disinflation {np.mean(outc == 'sustained disinflation'):.0%}, reacceleration {np.mean(outc == 'reacceleration'):.0%}, mixed {np.mean(outc == 'mixed/flat'):.0%}."])
qa("13. Disagreement and supply-versus-demand", [
   f"Mean disagreement by regime: adverse-supply-like {rt.get('adverse-supply-like (infl high, demand weak)', np.nan):.2f}, demand-like {rt.get('demand-like (infl high, demand high)', np.nan):.2f}, favorable-supply-like {rt.get('favorable-supply-like (infl low, demand strong)', np.nan):.2f}, weak-demand {rt.get('weak-demand (infl low, demand weak)', np.nan):.2f}: "
   f"{'higher when inflation is strong but demand weak than in demand-led episodes' if rt.get('adverse-supply-like (infl high, demand weak)', 0) > rt.get('demand-like (infl high, demand high)', 0) else 'not higher in supply-like than in demand-led episodes'}.",
   f"Correlates: cross-sectional dispersion {corr_rows['xs_sd_3m']['corr']:+.2f} (t {corr_rows['xs_sd_3m']['t (HAC)']:+.1f}), |oil shock| {corr_rows['abs_oil_12m']['corr']:+.2f}, flexible minus sticky {corr_rows['flex_less_sticky']['corr']:+.2f}, headline-core gap {corr_rows['headline_core_gap']['corr']:+.2f}.",
   f"Given current inflation and demand, a 1-sd rise in disagreement changes the subsequent 12m inflation change by {PRED.loc['beta D_res (pp per sd)', '12m']:+.2f} pp (t {PRED.loc['t', '12m']:+.1f}): {'faster mean reversion' if PRED.loc['beta D_res (pp per sd)', '12m'] < 0 else 'no faster mean reversion'}. Descriptive, not structural."])
qa("14. Implications for the Fed debate", [
   f"Projected core PCE stays {'above' if h12['forecast'] > 2 else 'at or below'} 2% at all horizons ({fc_str}); projected change {h12['change']:+.2f} pp over 12m (time-series benchmark {NOW.loc['M1 time series', '12m'] - h12['current']:+.2f}).",
   f"Evidence for deceleration: {n_dec}/{len(MEAS)} measures decelerating, P(lower in 12m) {p12:.0%}, analogs decelerating {(a1 < 0).mean():.0%}: {'strong' if (p12 > 0.65 and n_dec >= 0.7*len(MEAS)) else 'moderate' if p12 > 0.5 else 'weak'}.",
   f"Uncertainty: 12m pseudo-out-of-sample RMSE {OOS.loc['M3 global + block', '12m']:.2f} pp; block disagreement at the {ordinal(pct_rank(D_res))} percentile.",
   f"Risks implied by the outputs: persistence {'high' if h12['forecast'] > 2.75 else 'moderate' if h12['forecast'] > 2.25 else 'low'} (forecast level); reacceleration {'elevated' if (ev_hist['reaccelerated within 6m'].mean() > 0.5 or z_now['B_exp'] > 1) else 'moderate'} (expectations residual {RESID.iloc[-1]['B_exp']:+.2f}, historical reacceleration frequency {ev_hist['reaccelerated within 6m'].mean():.0%}); "
   f"premature tightening {'notable' if pctF['B_dem'] < 30 else 'limited'} (demand factor at the {ordinal(pctF['B_dem'])} percentile)."])
qa("15. Warsh, Waller, Kashkari", [
   f"Warsh (inflation broad, policy not restrictive): breadth at 12m at the {ordinal(pct_rank(b12s))} percentile ({100*b12s.iloc[-1]:.0f}% above 3%) and financial conditions at the {ordinal(pctF['B_fin'])} percentile on the loose side, so {'both legs' if pct_rank(b12s) > 60 and pctF['B_fin'] > 60 else 'the financial leg' if pctF['B_fin'] > 60 else 'the breadth leg' if pct_rank(b12s) > 60 else 'neither leg'} of the argument find support; demand at the {ordinal(pctF['B_dem'])} percentile does not.",
   f"Waller (underlying inflation declining): {n_dec}/{len(MEAS)} measures show 3m below 12m; the model projects {h12['change']:+.2f} pp over 12m with P(lower) {p12:.0%}, so the momentum is {'confirmed' if p12 > 0.6 else 'only partly confirmed'}; comparable gaps were turning points {ev_hist['turning point'].mean():.0%} of the time.",
   f"Kashkari (entrenchment from waiting): the 12m forecast stays at {h12['forecast']:.1f}%, the expectations block is the most inflationary residual ({RESID.iloc[-1]['B_exp']:+.2f}) with households {exp_now.loc['mich_less_spf', 'latest']:+.1f} pp above professionals, and analogs reaccelerated in {np.mean(outc == 'reacceleration'):.0%} of cases: "
   f"{'supports' if (h12['forecast'] > 2.75 and RESID.iloc[-1]['B_exp'] > 0.5) else 'partly supports'} the concern on level and expectations, {'less so' if np.mean(outc == 'reacceleration') < 0.3 else 'and'} on historical reacceleration."])
R.p(TEXT["p06_caveat_latest_vintage_data_an"])
R.summary([
    f"Core PCE runs at {B1['pce_core_12m'].loc[T]:.1f} percent over 12 months and {B1['pce_core_3m'].loc[T]:.1f} percent annualized over 3 months.",
    TEXT["s02_we_collect_data_across_five_bl"],
    f"The dynamic factor model that leverages data across all five blocks projects 12-month core PCE inflation of {fc_str} percent at {hs_str} months ahead, "
    f"that is, a {'deceleration' if h12['change'] < 0 else 'acceleration'} of {abs(h12['change']):.1f} pp over the 12 months, and inflation is not expected to return to target over the near term.",
    TEXT["s04_the_first_common_factor_in_eac"],
    TEXT["s06_across_the_second_principal_co"]])
R.write("report"); print(f"report.md / report.html written in {time.time()-t0:.0f}s; {len(list(FIG.glob('*.png')))} figures")
