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
import io, sys, time, warnings, html
from pathlib import Path
import numpy as np, pandas as pd, requests
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from scipy import stats
warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.3, "font.size": 9})

HERE = Path(__file__).resolve().parent; CACHE = HERE / "cache"; FIG = HERE / "figures"
for d in (CACHE, FIG): d.mkdir(exist_ok=True)
REFRESH = "--refresh" in sys.argv
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
        for c in df.columns:
            if pd.api.types.is_float_dtype(df[c]): df[c] = df[c].map(lambda v: "" if pd.isna(v) else fmt.format(v))
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
R.p(f"Report generated {pd.Timestamp.today():%B %d, %Y}; data through {max(v.index[-1] for v in RAW.values()):%B %Y}.")
R.summary_slot()
R.h(2, "Introduction")
R.p("The question is what the current configuration of inflation-related indicators implies for future US inflation, how much the indicators agree or disagree with one another, and whether today's configuration resembles past episodes. "
    "The motivation is the current Fed debate, in which policymakers emphasize different statistics: recent inflation momentum, median and trimmed measures, the breadth of price increases, expectations, labor-market conditions, demand, and financial conditions.")
R.p("All of these are treated as potentially useful signals for future inflation rather than sorted into 'measures of underlying inflation' and 'predictors'. A measure of underlying inflation is useful partly because it extracts the persistent, forecast-relevant component of current inflation, so the two roles are not distinct.")
R.p("The approach has five steps. Predictors are organized into five blocks and each block is examined on its own. Two global factors are extracted from the full panel and one factor from each block's residual. Core PCE inflation is forecast at 3, 6, and 12 months with nested direct regressions. "
    "The current forecast is decomposed into contributions from inflation history and each factor, and forecast revisions are decomposed into news. Finally, disagreement across signals is measured, historical analogs are found, and disagreement is related to supply-like and demand-like episodes.")
R.note("Data are latest-vintage FRED series (CSV endpoint, no key). Two inputs are not on FRED and are flagged where used: the Survey of Professional Forecasters individual CPI forecasts (Philadelphia Fed) and the excess bond premium (Federal Reserve). "
       "Pseudo-out-of-sample results computed on revised data are not real-time results; the data loader is isolated so that ALFRED vintages can be substituted later.")
R.h(2, "1. The five blocks")
R.p(f"{(VER['status'] == 'ok').sum()} of {len(VER)} FRED series were downloaded and verified (first and last observations are in cache/series_verification.csv). "
    f"Series starting after 1995 and therefore imputed in the early sample: {', '.join(VER.index[VER['flag'] == 'short history'])}. The panel runs from {START[:4]}, when the breadth block first has at least 20 categories.")
R.p("For each block the same diagnostic is shown: the variables are standardized, a principal-components decomposition is computed, and four panels report the scree (evidence of one versus several dimensions), the correlation of each variable with the first component (closer to one means more aligned with the block's common factor), "
    "the first component over time as a one-line summary of the block, and the residuals from the one-factor fit as a heatmap (whether recent months look different from history).")
# ------------------------------------------------------------------ block EDA
import re
GROUPS = {"infl": [("momentum", r"less|_d\d+_|accel"), ("persistent-measure level", r"sticky|median|trim"), ("flexible-price level", r"flex"), ("headline/core level", r".")],
          "dist": [("breadth", r"share_gt"), ("breadth momentum", r"share_(accel|decel)"), ("dispersion", r"xs_(sd|iqr|p90|skew)|upper_tail"), ("central tendency", r"xs_median")],
          "exp": [("dispersion", r"_sd|_iqr"), ("household-professional/market gaps", r"mich_less|spf_less"), ("term structure", r"less"), ("households", r"mich"), ("professionals", r"spf"), ("model-based", r"clev"), ("markets", r"bei")],
          "dem": [("wages", r"ahe|eci|comp"), ("labor market", r"unrate|claims|payroll|vu_|quits"), ("activity", r"real_|ip_|capu|gdp"), ("sentiment", r"sentiment")],
          "fin": [("risk pricing", r"vix|baa|gz|ebp|term_premium|mortgage"), ("conditions indexes", r"nfci"), ("rates", r"fedfunds|dgs|term_2s10s|real_10y"), ("asset prices", r"equity|usd|oil|ppi"), ("credit supply", r"sloos")]}
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
READING = {   # one-line interpretations, written against the estimated loadings; the data-driven description printed alongside is the check
 ("infl", 1): "Reading: the common level of inflation across headline, core, trimmed and median measures at every horizon, a level factor.",
 ("infl", 2): "Reading: recent momentum in sticky and median prices against their 12-month level, a turning-point factor: high when persistent inflation is low but re-accelerating, low when it is high but slowing (2022-23).",
 ("dist", 1): "Reading: breadth and central tendency of the price-change distribution, how many categories are rising fast; a broad-inflation factor.",
 ("dist", 2): "Reading: two-sided dispersion (IQR, share decelerating) against upper-tail concentration and skewness; separates wide relative-price dispersion from a few categories spiking.",
 ("exp", 1): "Reading: the level of near-term expected inflation across professionals, the Cleveland model, markets and households, plus the slope of the expectations term structure; a near-term expectations factor.",
 ("exp", 2): "Reading: households versus professionals, the model and markets, together with forecaster dispersion; an excess-household-expectations and disagreement factor, high when households expect more than everyone else.",
 ("dem", 1): "Reading: output and employment growth, the business-cycle factor.",
 ("dem", 2): "Reading: wage growth and labor-market tightness (V/U, quits) against the unemployment rate and retail momentum; a labor-tightness and wage-pressure factor distinct from output growth.",
 ("fin", 1): "Reading: credit spreads, the excess bond premium, the NFCI and lending standards (inverted) with equity returns positive; a risk-appetite versus financial-stress factor, oriented so that higher = looser.",
 ("fin", 2): "Reading: the level of nominal and real interest rates, a rates-level factor independent of risk pricing.",
 "G1": "Reading: the common inflation level, essentially the inflation block's level factor plus breadth; the state the median and trimmed measures try to track.",
 "G2": "Reading: inflation momentum against persistence (sticky and median momentum positive, their levels inverted), oriented with demand: a re-acceleration versus disinflation state."}
def block_eda(name, df, ref, flip=False, title=""):
    """Standardize over the panel window, PCA; figure: scree and PC1/PC2 paths; correlations with PC1 and one-factor residuals; correlations with PC2 and two-factor residuals."""
    Zb = zscore(df[df.index >= START].dropna(how="all")); Zb = Zb.loc[:, Zb.notna().mean() > 0.5]
    sc, ld, ex, Zf = pca(Zb, min(8, Zb.shape[1]))
    sgn = np.sign(np.corrcoef(sc["PC1"], Zb[ref].fillna(0))[0, 1]) * (-1 if flip else 1)
    f1 = sgn * sc["PC1"]; BPC[name] = f1; f1z = (f1 - f1.mean()) / f1.std(); l1 = Zf.corrwith(f1z)
    f2z = (sc["PC2"] - sc["PC2"].mean()) / sc["PC2"].std(); l2 = Zf.corrwith(f2z); s2 = np.sign(l2.loc[l2.abs().idxmax()]); f2z, l2 = s2 * f2z, s2 * l2   # PC2 sign: largest |correlation| positive
    res1 = (Zf - np.outer(f1z, l1)).where(Zb.notna()); res2 = (res1 - np.outer(f2z, l2)).where(Zb.notna())
    fig, ax = plt.subplots(3, 2, figsize=(15, 11.5), gridspec_kw={"width_ratios": [1, 1.7]})
    ax[0, 0].bar(range(1, len(ex) + 1), 100 * ex, color="#1e293b"); ax[0, 0].set_title(f"Scree, % of variance (PC1 {100*ex[0]:.0f}%, PC2 {100*ex[1]:.0f}%)"); ax[0, 0].set_xticks(range(1, len(ex) + 1))
    ax[0, 1].plot(f1z.index, f1z, color="k", lw=1.3, label="PC1"); ax[0, 1].plot(f2z.index, f2z, color="k", lw=1, ls="--", label="PC2"); ax[0, 1].axhline(0, color="grey", lw=.6)
    ax[0, 1].set_title(f"Factors, standardized (PC1: + = inflationary; latest {f1z.iloc[-1]:+.1f}, {ordinal(pct_rank(f1))} percentile)"); ax[0, 1].legend(frameon=False)
    def corr_panel(a, l, lab):
        k = min(20, len(l)); show = l.reindex(l.abs().sort_values().index[-k:])
        a.barh(range(k), show.abs().values, color=np.where(show.values > 0, "#1e293b", "#7c9cc6")); a.set_yticks(range(k)); a.set_yticklabels([f"{vname(c)}{' (inv)' if v < 0 else ''}" for c, v in show.items()], fontsize=7)
        a.set_xlim(0, 1); a.set_title(f"|corr| with {lab}, top {k} of {len(l)} (inv = sign inverted)", fontsize=8.5)
    def heat(a, res, l, lab):
        order = l.abs().sort_values(ascending=False).index          # largest |correlation| at the top, matching the bar chart
        im = a.imshow(res[order].T.values, aspect="auto", cmap="RdBu_r", vmin=-3, vmax=3, extent=[mdates.date2num(res.index[0]), mdates.date2num(res.index[-1]), len(order), 0]); a.xaxis_date(); a.grid(False)
        last = res[order].iloc[-3:].mean()                       # label every variable when readable, otherwise only those with a large end-of-sample residual
        lab_rows = list(range(len(order))) if len(order) <= 45 else [i for i, c in enumerate(order) if abs(last[c]) > 1.0]
        a.yaxis.tick_right(); a.set_yticks([i + 0.5 for i in lab_rows]); a.set_yticklabels([f"{vname(order[i])} ({last[order[i]]:+.1f})" for i in lab_rows], fontsize=5.5 if len(lab_rows) > 25 else 7); a.tick_params(axis="y", length=0)
        a.set_title(f"Residuals, {lab} fit (rows by |loading|; red = above the factor fit; label = last-3-month mean, sd)", fontsize=8.5)
        fig.colorbar(im, ax=a, orientation="horizontal", shrink=.35, pad=.12, aspect=40)
    corr_panel(ax[1, 0], l1, "PC1"); heat(ax[1, 1], res1, l1, "one-factor"); corr_panel(ax[2, 0], l2, "PC2"); heat(ax[2, 1], res2, l2, "two-factor")
    plt.tight_layout(); R.fig(fig, f"block_{name}", title)
    DESC[(name, 1)] = describe_factor(name, l1); DESC[(name, 2)] = describe_factor(name, l2)
    R.p(f"PC1 is {DESC[(name, 1)]}. {READING.get((name, 1), '')}")
    R.p(f"PC2 is {DESC[(name, 2)]}. {READING.get((name, 2), '')}")
    top_res = res1.iloc[-1].dropna(); top_res = top_res.reindex(top_res.abs().sort_values().index[-3:][::-1]); res = res1
    dim = "one dominant dimension" if ex[0] > 2 * ex[1] else "at least two dimensions of comparable size"
    R.p(f"{Zb.shape[1]} variables from {Zb.index[0]:%Y-%m}. The first three components explain {100*ex[0]:.0f}, {100*ex[1]:.0f}, and {100*ex[2]:.0f} percent of the variance, which points to {dim}. "
        f"The first component stands at {f1z.iloc[-1]:+.1f} standard deviations today, the {ordinal(pct_rank(f1))} percentile of its history. The largest deviations from what the common factor implies are "
        + ", ".join(f"{vname(c)} ({v:+.1f} sd)" for c, v in top_res.items()) + ".")

# ------------------------------------------------------------------ block 1: inflation measures
def inflation_set(px, tag, kind="index"):
    if kind == "index": p = {h: ann(px, h) for h in (1, 3, 6, 12)}
    else: m1, m12 = px; p = {1: m1, 3: m1.rolling(3).mean(), 6: m1.rolling(6).mean(), 12: m12}
    out = {f"{tag}_{h}m": p[h] for h in (1, 3, 6, 12)}
    out[f"{tag}_3m_less_12m"] = p[3] - p[12]; out[f"{tag}_6m_less_12m"] = p[6] - p[12]
    for k in (3, 6, 12): out[f"{tag}_d{k}_12m"] = p[12] - p[12].shift(k)
    out[f"{tag}_accel"] = p[3] - p[3].shift(3); return out
B1 = {}
for sid, tag in [("CPIAUCSL", "cpi"), ("CPILFESL", "cpi_core"), ("PCEPI", "pce"), ("PCEPILFE", "pce_core"), ("CUSR0000SASLE", "cpi_svc_xe"), ("DSERRG3M086SBEA", "pce_svc")]:
    B1.update(inflation_set(m(sid), tag))
for m1, m12, tag in [("MEDCPIM158SFRBCLE", "MEDCPIM159SFRBCLE", "cpi_median"), ("TRMMEANCPIM158SFRBCLE", "TRMMEANCPIM159SFRBCLE", "cpi_trim"), ("PCETRIM1M158SFRBDAL", "PCETRIM12M159SFRBDAL", "pce_trim"),
                     ("STICKCPIM157SFRBATL", "STICKCPIM159SFRBATL", "cpi_sticky"), ("CORESTICKM157SFRBATL", "CORESTICKM159SFRBATL", "cpi_core_sticky"), ("FLEXCPIM157SFRBATL", "FLEXCPIM159SFRBATL", "cpi_flex"),
                     ("COREFLEXCPIM157SFRBATL", "COREFLEXCPIM159SFRBATL", "cpi_core_flex")]:
    B1.update(inflation_set((m(m1), m(m12)), tag, kind="rates"))
B1 = pd.DataFrame(B1); B1 = B1[[c for c in B1 if not (c.startswith(("cpi_svc_xe", "pce_svc", "cpi_core_sticky", "cpi_core_flex")) and not c.endswith(("_3m", "_12m")))]]
R.h(3, "Block 1: inflation measures")
R.table(pd.DataFrame([["CPI, core CPI, PCE, core PCE, CPI services ex energy, PCE services", "BLS, BEA (index levels)", "annualized 1/3/6/12-month log changes"],
                      ["Median CPI, 16% trimmed-mean CPI", "Cleveland Fed (1-month annualized and 12-month rates)", "3m and 6m as rolling means of the 1-month rate"],
                      ["Trimmed-mean PCE", "Dallas Fed", "as above"], ["Sticky, core sticky, flexible, core flexible CPI", "Atlanta Fed", "as above"],
                      ["Momentum for every measure", "derived", "3m minus 12m, 6m minus 12m, change in the 12m rate over 3/6/12 months, acceleration (3m rate minus its value three months earlier)"]],
                     columns=["Indicators", "Source", "Transformation"]).set_index("Indicators"), "Block 1 contents", small=True)
R.p("For the principal indexes the multi-horizon rates capture the level of inflation and the momentum terms whether it is accelerating or decelerating; the median, trimmed, sticky and flexible measures add alternative filters of the same aggregate.")
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
R.h(3, "Block 2: price-change distribution")
R.table(pd.DataFrame([["Food (7)", "cereals; meats, poultry, fish, eggs; dairy; fruits and vegetables; other food at home; food away from home; alcohol"],
                      ["Energy (4)", "gasoline; fuel oil; electricity; utility gas"],
                      ["Core goods (12)", "men's, women's and infants' apparel; footwear; new and used vehicles; vehicle parts; medical commodities; household furnishings; tobacco; recreation commodities; educational books"],
                      ["Services (11)", "rent; owners' equivalent rent; lodging away from home; water and sewer; professional medical and hospital services; vehicle maintenance; public transportation; tuition and childcare; personal care; other services"],
                      ["Statistics", "shares above 0/2/3/4/5 percent, shares accelerating and decelerating, SD, IQR, 90-10 spread, skewness, median, upper-tail share; each at 3, 6 and 12 months"]],
                     columns=["Group", "Categories"]).set_index("Group"), "Block 2 contents: 34 CPI expenditure categories (FRED, seasonally adjusted)", small=True)
R.p(f"Cross-sectional statistics of annualized 3/6/12-month inflation across {P.shape[1]} CPI expenditure categories from FRED (SA), selected so that no category nests another; "
    "unbalanced panel (22 categories in the late 1980s, 34 from 1998; minimum 20). Shares above 0/2/3/4/5%, shares accelerating and decelerating, SD, IQR, 90-10 spread, skewness, median, upper-tail share. "
    "Unweighted only (BLS relative importances are not on FRED; WEIGHTS is the hook). A BEA detailed-PCE panel would be the upgrade.")
block_eda("dist", B2.drop(columns="n_cats"), "share_gt3_12m", title="Block 2, price-change distribution")

# ------------------------------------------------------------------ block 3: expectations
E = pd.DataFrame({"mich_1y": m("MICH"), "clev_1y": m("EXPINF1YR"), "clev_10y": m("EXPINF10YR"), "bei_5y": m("T5YIE"), "bei_10y": m("T10YIE"), "bei_5y5y": m("T5YIFR")}).join(SPF_Q.drop(columns="spf_n").pipe(q_to_m), how="outer")
E["mich_less_spf"] = E["mich_1y"] - E["spf_cpi_4q"]; E["mich_less_bei5"] = E["mich_1y"] - E["bei_5y"]; E["spf_less_clev1"] = E["spf_cpi_4q"] - E["clev_1y"]
E["mich_1y_less_clev10"] = E["mich_1y"] - E["clev_10y"]; E["spf_4q_less_10y"] = E["spf_cpi_4q"] - E["spf_cpi_10y"]; E["bei_5y_less_5y5y"] = E["bei_5y"] - E["bei_5y5y"]; E["clev_1y_less_10y"] = E["clev_1y"] - E["clev_10y"]
B3 = E
R.h(3, "Block 3: inflation expectations")
R.table(pd.DataFrame([["Households", "Michigan 1-year median expectation"], ["Professionals", "SPF median 4-quarter-ahead CPI; SPF 10-year CPI (Philadelphia Fed)"], ["Model-based", "Cleveland Fed 1-year and 10-year expected inflation"],
                      ["Markets", "5-year, 10-year and 5y5y forward breakevens"], ["Disagreement", "SPF cross-sectional IQR and SD of the 4-quarter forecast; households minus professionals; households minus markets; professionals minus the Cleveland model"],
                      ["Term structure", "1-year minus 10-year for Michigan/Cleveland, SPF 4q minus 10y, 5y minus 5y5y breakevens"]],
                     columns=["Group", "Indicators"]).set_index("Group"), "Block 3 contents", small=True)
R.p("Levels of expected inflation, Cleveland Fed 1y/10y, SPF 4-quarter-ahead CPI median and SPF 10y, 5y/10y/5y5y breakevens; disagreement as the SPF cross-sectional IQR and SD and as spreads between households, professionals, the Cleveland model and markets; near minus long horizons. "
    "Michigan 5-10y expectations and Michigan respondent dispersion are not on FRED and are omitted rather than proxied.")
block_eda("exp", B3, "mich_1y", title="Block 3, expectations")

# ------------------------------------------------------------------ block 4: demand and labor
B4 = pd.DataFrame({"unrate": m("UNRATE"), "unrate_d12": m("UNRATE") - m("UNRATE").shift(12), "payrolls_3m": ann(m("PAYEMS"), 3), "payrolls_12m": ann(m("PAYEMS"), 12), "claims_log": np.log(m("ICSA")),
                   "claims_d3_log": dlog(m("ICSA"), 3), "vu_ratio": m("JTSJOL") / m("UNEMPLOY"), "quits": m("JTSQUR"), "ahe_12m": ann(m("AHETPI"), 12), "ahe_3m": ann(m("AHETPI"), 3),
                   "eci_wages_yoy": q_to_m(RAW["ECIWAG"].pct_change(4) * 100), "comp_12m": ann(m("W209RC1"), 12), "real_pce_6m": ann(m("DPCERA3M086SBEA"), 6), "real_pce_12m": ann(m("DPCERA3M086SBEA"), 12),
                   "real_retail_6m": ann(m("RRSFS"), 6), "ip_6m": ann(m("INDPRO"), 6), "ip_12m": ann(m("INDPRO"), 12), "capu": m("TCU"), "real_inv_yoy": q_to_m(RAW["GPDIC1"].pct_change(4) * 100),
                   "gdp_yoy": q_to_m(RAW["GDPC1"].pct_change(4) * 100), "sentiment": m("UMCSENT")})
R.h(3, "Block 4: demand and labor")
R.table(pd.DataFrame([["Labor market", "unemployment rate and its 12-month change; payroll growth (3m, 12m); initial claims (log level, 3-month change); job openings to unemployed; quits rate"],
                      ["Wages", "average hourly earnings (3m, 12m); ECI wages and salaries (yoy, quarterly); compensation of employees (12m)"],
                      ["Activity and demand", "real PCE (6m, 12m); real retail sales (6m); industrial production (6m, 12m); capacity utilization; real private investment (yoy, quarterly); real GDP (yoy, quarterly); Michigan sentiment"]],
                     columns=["Group", "Indicators"]).set_index("Group"), "Block 4 contents", small=True)
R.p("Rates in levels (and 12-month changes for unemployment), quantities as annualized 3/6-month or 12-month log growth, quarterly series spread over their quarter. "
    "Real business fixed and residential investment on FRED start in 2007, so total real private investment stands in.")
block_eda("dem", B4, "payrolls_12m", title="Block 4, demand and labor")

# ------------------------------------------------------------------ block 5: financial
usd_old, usd_new = m("TWEXBMTH"), m("DTWEXBGS"); ov = usd_old.index.intersection(usd_new.index); usd = pd.concat([usd_old[usd_old.index < ov[0]] * (usd_new[ov] / usd_old[ov]).mean(), usd_new])
B5 = pd.DataFrame({"fedfunds": m("FEDFUNDS"), "dgs2": m("DGS2"), "dgs10": m("DGS10"), "term_2s10s": m("DGS10") - m("DGS2"), "fedfunds_d12": m("FEDFUNDS") - m("FEDFUNDS").shift(12), "real_10y_tips": m("DFII10"),
                   "real_10y_clev": m("DGS10") - m("EXPINF10YR"), "nfci": m("NFCI"), "anfci": m("ANFCI"), "vix": m("VIXCLS"), "baa_spread": m("BAA10Y"), "gz_spread": EBP["gz_spread"], "ebp": EBP["ebp"],
                   "term_premium_10y": m("THREEFYTP10"), "equity_12m_ret": dlog(m("NASDAQCOM"), 12), "equity_3m_ret": dlog(m("NASDAQCOM"), 3), "usd_12m": dlog(usd, 12), "oil_12m": dlog(m("WTISPLC"), 12),
                   "oil_3m": dlog(m("WTISPLC"), 3), "ppi_comm_12m": dlog(m("PPIACO"), 12), "sloos_ci": q_to_m(RAW["DRTSCILM"]), "mortgage_spread": m("MORTGAGE30US") - m("DGS10")})
R.h(3, "Block 5: financial conditions and risk pricing")
R.table(pd.DataFrame([["Rates", "fed funds and its 12-month change; 2- and 10-year Treasury yields; 2s10s slope; 10-year TIPS yield; 10-year minus Cleveland 10-year expectations"],
                      ["Conditions indexes", "Chicago Fed NFCI and adjusted NFCI"], ["Risk pricing", "VIX; Baa minus 10-year; GZ spread and excess bond premium; Kim-Wright 10-year term premium; mortgage spread"],
                      ["Asset prices", "Nasdaq 3- and 12-month returns; broad dollar 12-month change (spliced index); WTI oil 3- and 12-month changes; PPI all commodities 12-month change"], ["Credit supply", "SLOOS net tightening of C&I standards (quarterly)"]],
                     columns=["Group", "Indicators"]).set_index("Group"), "Block 5 contents", small=True)
R.p("Monthly averages of daily data; policy and Treasury rates, term spread, real rates (TIPS and 10y minus Cleveland expectations), NFCI and adjusted NFCI, VIX, Baa spread, "
    "GZ spread and excess bond premium, term premium, equity returns (Nasdaq; the S&P 500 on FRED is limited to ten years), a spliced broad dollar, oil and commodity prices, SLOOS standards, mortgage spread. "
    "The factor is oriented so that positive = looser.")
block_eda("fin", B5, "nfci", flip=True, title="Block 5, financial conditions (+ = looser)")

# =============================================================================== panel and factors
BLOCKS = {"infl": B1, "dist": B2.drop(columns="n_cats"), "exp": B3, "dem": B4, "fin": B5}
X = pd.concat(BLOCKS, axis=1); X = X[X.index >= START]; X = X.loc[:, (X.notna().mean() > 0.5) & (X.std() > 0)]
END = B1["pce_core_12m"].dropna().index[-1]; X = X[X.index <= END]; Z = zscore(X)
DICT = pd.DataFrame({"block": [b for b, _ in X.columns], "first_obs": [X[c].first_valid_index().date() for c in X.columns]}, index=[c for _, c in X.columns]); DICT.to_csv(CACHE / "data_dictionary.csv")

R.h(2, "2. Factor structure")
G, LG, exG, Zfill = pca(Z, 2)
sign = lambda f, ref: f * np.sign(np.corrcoef(f, ref.reindex(f.index).fillna(0))[0, 1])
G["PC1"] = sign(G["PC1"], Z[("infl", "pce_core_12m")]); G["PC2"] = sign(G["PC2"], Z["dem"].mean(axis=1)); G.columns = ["G1", "G2"]; LG.columns = ["G1", "G2"]
LG["G1"] *= np.sign(np.corrcoef(G["G1"], Zfill.values @ LG["G1"].values)[0, 1]); LG["G2"] *= np.sign(np.corrcoef(G["G2"], Zfill.values @ LG["G2"].values)[0, 1])
resid = Zfill - pd.DataFrame(G.values @ np.linalg.lstsq(G.values, Zfill.values, rcond=None)[0], index=Z.index, columns=Z.columns)
REF = {"infl": ("infl", "pce_core_12m"), "dist": ("dist", "share_gt3_12m"), "exp": ("exp", "mich_1y"), "dem": ("dem", "payrolls_12m"), "fin": ("fin", "nfci")}
Bf, exB, LB = {}, {}, {}
for b in BLOCKS:
    sc, ld, ex, _ = pca(resid[b].where(Z[b].notna()), 1); sg = np.sign(np.corrcoef(sc["PC1"], Z[REF[b]].fillna(0))[0, 1]) * (-1 if b == "fin" else 1)
    Bf[f"B_{b}"] = sg * sc["PC1"]; exB[b] = ex[0]; LB[b] = sg * ld["PC1"]
F = pd.concat([G, pd.DataFrame(Bf)], axis=1); Fz = zscore(F)
var = VAR(F.dropna()).fit(1); persist = pd.Series(np.diag(var.coefs[0]), index=F.columns)
top = lambda ld, k=3: ", ".join(f"{vname(c)} ({v:+.2f})" for c, v in ld.reindex(ld.abs().sort_values().index[-k:][::-1]).items())
R.p("The factor model is X = Lambda_G G + lambda_B B + e: two global factors common to the whole panel and one factor specific to each block. The implementation is simple: standardize the panel, extract two principal components, subtract the fitted global component, and take the first principal component of each block's residual. "
    "Signs are normalized so that every factor is oriented as inflationary pressure (the financial factor: looser conditions). A VAR(1) on the seven factors provides the dynamics used in the news decomposition.")
R.p(f"The panel has {X.shape[1]} variables from {X.index[0]:%Y-%m} to {END:%Y-%m}. Two global PCs on the standardized panel explain {100*exG.sum():.0f}% of its variance (G1 {100*exG[0]:.0f}%, G2 {100*exG[1]:.0f}%); "
    f"one PC per block on the residual explains {', '.join(f'{b} {100*v:.0f}%' for b, v in exB.items())} of the block's residual variance. Every factor is oriented so that higher = more inflationary pressure (financial: looser). "
    f"VAR(1) own-persistence: {', '.join(f'{k} {v:.2f}' for k, v in persist.items())}.")
LGc = {g: Zfill.corrwith((G[g] - G[g].mean()) / G[g].std()) for g in ("G1", "G2")}
def describe_global(l, k=10):
    tp = l.reindex(l.abs().sort_values(ascending=False).index[:k]); pos, neg = tp[tp > 0], tp[tp < 0]
    def side(x):
        if x.empty: return "none"
        g = pd.Series([f"{b_} {group_of(b_, c)}" for b_, c in x.index]).value_counts(); return ", ".join(f"{k_} ({int(n)})" for k_, n in g.items()) + "; e.g. " + ", ".join(vname(c) for c in x.index[:3])
    blk = pd.Series([b_ for b_, _ in tp.index]).value_counts(); return f"drawn from {', '.join(f'{k_} ({int(n)})' for k_, n in blk.items())} among its top-{k} correlates; aligned positively with {side(pos)}; inverted: {side(neg)}"
R.p(f"G1 is {describe_global(LGc['G1'])}. {READING.get('G1', '')}")
R.p(f"G2 is {describe_global(LGc['G2'])}. {READING.get('G2', '')}")
R.bullets([f"B_{b} loads on: {top(LB[b])}" for b in BLOCKS])
fig, axes = plt.subplots(1, 2, figsize=(15, 3.6))
Fz[["G1", "G2"]].plot(ax=axes[0], lw=1.2, color=["k", "tab:red"]); axes[0].set_title("Global factors (standardized)")
Fz[[c for c in Fz if c.startswith("B_")]].plot(ax=axes[1], lw=1); axes[1].set_title("Block-specific factors (standardized)")
for ax in axes: ax.axhline(0, color="grey", lw=.6); ax.legend(ncol=4, fontsize=8, frameon=False)
R.fig(fig, "factors", "Global and block-specific factors.")

# =============================================================================== targets and forecasts
R.h(2, "3. Forecasting core PCE")
pce_core = m("PCEPILFE"); logp = np.log(pce_core)
Y = pd.DataFrame({f"pi_fut_{h}": 1200 / h * (logp.shift(-h) - logp) for h in H}); pi12 = 1200 / 12 * (logp - logp.shift(12))
for h in H: Y[f"dpi_{h}"] = Y[f"pi_fut_{h}"] - pi12; Y[f"decel_{h}"] = (Y[f"dpi_{h}"] < 0).astype(float).where(Y[f"dpi_{h}"].notna())
HIST = pd.DataFrame({"pi12": pi12, "pi12_lag12": pi12.shift(12), "pi3": B1["pce_core_3m"], "pi6": B1["pce_core_6m"], "d3_pi12": B1["pce_core_d3_12m"], "accel": B1["pce_core_accel"]})
SETS = {"M1 history": list(HIST.columns), "M2 +global": list(HIST.columns) + ["G1", "G2"], "M3 +global+block": list(HIST.columns) + list(F.columns)}
D = pd.concat([HIST, F, Y], axis=1).loc[F.index]; T = D.index[-1]
results = []
for h in [3, 6, 12]:
    for name, cols in SETS.items():
        f = oos_forecast(D, f"pi_fut_{h}", cols, h); e = (D[f"pi_fut_{h}"] - f).dropna(); da = (np.sign(f - D["pi12"]) == np.sign(D[f"dpi_{h}"])).loc[e.index].mean()
        results.append(dict(h=h, model=name, RMSFE=np.sqrt((e ** 2).mean()), dir_acc=da))
RES_OOS = pd.DataFrame(results); RES_OOS["rel_RMSFE"] = RES_OOS["RMSFE"] / RES_OOS.groupby("h")["RMSFE"].transform("first"); RM = RES_OOS.set_index(["h", "model"])
R.p("Core PCE is the target. The dependent variables are future annualized core PCE inflation over 3, 6, 12 and 24 months, its change relative to today's 12-month rate, and an indicator for deceleration. "
    "Three nested direct regressions are compared: M1 uses inflation history and momentum only (12m rate, its 12-month lag, 3m and 6m rates, the 3-month change in the 12m rate, acceleration); M2 adds the two global factors; M3 adds the five block factors.")
R.p("Forecasts are evaluated pseudo-out-of-sample with an expanding window, its change relative to today's 12m rate, and the deceleration indicator. Direct regressions with three nested information sets: M1 inflation history and momentum, M2 plus the global factors, M3 plus the block factors. "
    f"Expanding-window pseudo-out-of-sample from {OOS_START[:4]} with full-sample factor loadings (a look-ahead in the factor construction).")
R.table(RES_OOS.pivot(index="model", columns="h", values=["RMSFE", "rel_RMSFE", "dir_acc"]), "Out-of-sample RMSFE, RMSFE relative to M1, and directional accuracy for acceleration/deceleration, by horizon (months)")
rows = {}
for h in [3, 6, 12]:
    r = ols(D[f"pi_fut_{h}"], D[SETS["M3 +global+block"]], hac=h); rows[f"{h}m"] = pd.Series({k: f"{r.params[k]:+.2f} ({r.tvalues[k]:+.1f})" for k in F.columns}); rows[f"{h}m"]["R2 M3 / M1"] = f"{r.rsquared:.2f} / {ols(D[f'pi_fut_{h}'], D[SETS['M1 history']]).rsquared:.2f}"
R.table(pd.DataFrame(rows), "In-sample factor coefficients (HAC t-statistics, lag = horizon) in the M3 regression")

R.h(2, "4. What the model says today")
today = {}
for h in [3, 6, 12]:
    cols = SETS["M3 +global+block"]; r = ols(D[f"pi_fut_{h}"], D[cols]); fc = r.params["const"] + (r.params[cols] * D.loc[T, cols]).sum(); rm = RM.loc[(h, "M3 +global+block"), "RMSFE"]
    r1 = ols(D[f"pi_fut_{h}"], D[SETS["M1 history"]]); f1 = r1.params["const"] + (r1.params[SETS["M1 history"]] * D.loc[T, SETS["M1 history"]]).sum()
    today[f"{h}m"] = {"current 12m core PCE": D.loc[T, "pi12"], "current h-month core PCE": B1[f"pce_core_{h}m"].loc[T], "forecast M3": fc, "forecast M1 history": f1, "forecast change vs 12m": fc - D.loc[T, "pi12"],
                      "direction": "decelerating" if fc < D.loc[T, "pi12"] else "accelerating", "90% band": f"[{fc-1.645*rm:.1f}, {fc+1.645*rm:.1f}]"}
TODAY = pd.DataFrame(today); R.table(TODAY, f"Forecast origin {T:%B %Y}; annualized percent; band from the out-of-sample RMSFE")

# =============================================================================== decompositions
R.h(2, "5. Current-signal and news decompositions")
GROUP = {**{c: "history" for c in HIST.columns}, "G1": "G1", "G2": "G2", "B_infl": "inflation", "B_dist": "distribution", "B_exp": "expectations", "B_dem": "demand", "B_fin": "financial"}
dec = {}
for h in [3, 6, 12]:
    cols = SETS["M3 +global+block"]; r = ols(D[f"pi_fut_{h}"], D[cols]); c = (r.params[cols] * (D.loc[T, cols] - D[cols].mean())).groupby(pd.Series(GROUP)).sum()
    dec[f"{h}m"] = pd.concat([pd.Series({"sample mean of target": D[f"pi_fut_{h}"].mean()}), c, pd.Series({"forecast": D[f"pi_fut_{h}"].mean() + c.sum()})])
dec = pd.DataFrame(dec).loc[["sample mean of target", "history", "G1", "G2", "inflation", "distribution", "expectations", "demand", "financial", "forecast"]]
fig, ax = plt.subplots(figsize=(8, 3.4)); dec.iloc[1:-1].plot.bar(ax=ax, width=.75); ax.axhline(0, color="grey", lw=.6); ax.set_title(f"Contributions to the core PCE forecast, {T:%b %Y} (pp, deviation from sample mean)"); ax.legend(title="horizon", frameon=False); plt.xticks(rotation=0)
R.h(3, "Current-signal decomposition")
R.p("For the linear M3 equation each contribution is the coefficient times the current value's deviation from its sample mean, so contributions sum to the forecast's deviation from the target's mean. This says which signals, at their current values, push the forecast away from its mean; it is not a news decomposition.")
R.fig(fig, "decomposition", "Current-signal decomposition of the core PCE forecast."); R.table(dec, "Contributions (pp)")

# news decomposition
X_full = pd.concat(BLOCKS, axis=1)[X.columns]; X_full = X_full[X_full.index >= START].dropna(how="all"); Z_full = (X_full - X.mean()) / X.std()
Lam = pd.DataFrame(0.0, index=Z.columns, columns=F.columns); Lam[["G1", "G2"]] = LG.values
for b in BLOCKS: Lam.loc[Lam.index.get_level_values(0) == b, f"B_{b}"] = LB[b].values
Rdiag = (Zfill - pd.DataFrame(F.values @ Lam.values.T, index=Z.index, columns=Z.columns)).var().values; A = var.coefs[0]; Q = var.sigma_u.values; nF = F.shape[1]
beta12 = ols(D["pi_fut_12"], D[list(F.columns)]); beta = beta12.params[list(F.columns)].values; alpha = beta12.params["const"]
def kalman_news(Z_full):
    L = Lam.values; T_, N = Z_full.shape; f, Pm = np.zeros(nF), np.eye(nF) * 10.0
    Ff = np.full((T_, nF), np.nan); NEWS = np.full((T_, N), np.nan); CONTR = np.full((T_, N), np.nan); REV = np.full(T_, np.nan)
    for t in range(T_):
        fp, Pp = A @ f, A @ Pm @ A.T + Q; obs = ~np.isnan(Z_full.values[t]); f, Pm = fp, Pp
        if obs.any():
            Lt, z = L[obs], Z_full.values[t, obs]; nu = z - Lt @ fp; S = Lt @ Pp @ Lt.T + np.diag(Rdiag[obs]); K = Pp @ Lt.T @ np.linalg.inv(S)
            f, Pm = fp + K @ nu, Pp - K @ Lt @ Pp; w = beta @ K; NEWS[t, obs] = nu; CONTR[t, obs] = w * nu; REV[t] = (w * nu).sum()
        Ff[t] = f
    idx = Z_full.index; return pd.DataFrame(Ff, idx, F.columns), pd.DataFrame(NEWS, idx, Z_full.columns), pd.DataFrame(CONTR, idx, Z_full.columns), pd.Series(REV, idx)
F_filt, NEWS, CONTR, REV = kalman_news(Z_full); tau = Z_full.index[-1]
grp = pd.Series([b for b, c in Z_full.columns], index=Z_full.columns); by_block = CONTR.T.groupby(grp).sum(min_count=1).T; recent = by_block.loc[by_block.index >= tau - pd.DateOffset(months=12)]
fig, axes = plt.subplots(1, 2, figsize=(15, 3.8), gridspec_kw={"width_ratios": [1.3, 1]}); ax = axes[0]; bp, bn = np.zeros(len(recent)), np.zeros(len(recent)); x = np.arange(len(recent))
for b in BLOCKS:
    v = recent[b].fillna(0).values; pos, neg = np.clip(v, 0, None), np.clip(v, None, 0); ax.bar(x, pos, bottom=bp, label=b); ax.bar(x, neg, bottom=bn, color=ax.patches[-1].get_facecolor()); bp += pos; bn += neg
ax.plot(x, REV.reindex(recent.index).values, "k.", label="total"); ax.axhline(0, color="grey", lw=.6); ax.set_xticks(x); ax.set_xticklabels([d.strftime("%b%y") for d in recent.index], fontsize=8); ax.legend(ncol=6, fontsize=8, frameon=False)
ax.set_title("Monthly revision of the 12m-ahead core PCE forecast attributed to news, by block (pp)")
ax = axes[1]; c_now = CONTR.iloc[-1].dropna(); c_now.index = [f"{b}:{v}" for b, v in c_now.index]; tp = c_now.reindex(c_now.abs().sort_values().index[-10:])
ax.barh(tp.index, tp.values, color=np.where(tp > 0, "tab:red", "tab:blue")); ax.axvline(0, color="grey", lw=.6); ax.set_title(f"Largest news contributions, {tau:%b %Y} (pp)"); ax.tick_params(axis="y", labelsize=8); plt.tight_layout()
R.h(3, "News decomposition")
R.p(f"The factor system in state-space form (loadings from the PCA, VAR(1) dynamics, diagonal idiosyncratic variances), filtered month by month through the ragged edge ({tau:%b %Y}). "
    f"News in each released series is its surprise relative to the previous month's information set; the revision of the factor-only 12m forecast is attributed through the Kalman gain. Latest-vintage values, so data revisions are ignored and publication lags enter only at the ragged edge. "
    f"Filtered factors track the PCA factors (correlations {', '.join(f'{c} {F_filt[c].corr(F[c]):.2f}' for c in F.columns)}). "
    f"{tau:%b %Y} revision {REV.iloc[-1]:+.2f} pp ({', '.join(f'{b} {v:+.2f}' for b, v in by_block.iloc[-1].dropna().items())}); cumulative over 12 months {REV.reindex(recent.index).sum():+.2f} pp; largest monthly revision {REV.reindex(recent.index).abs().idxmax():%b %Y} ({REV.reindex(recent.index).abs().max():.2f}).")
R.fig(fig, "news", "News decomposition of forecast revisions.")

# =============================================================================== disagreement
R.h(2, "6. Agreement and disagreement")
Fz7 = Fz.dropna(); D_sd = Fz7.std(axis=1); C1, lamb, exC, _ = pca(Fz7, 1); RESID = Fz7 - pd.DataFrame(np.outer(C1["PC1"], lamb["PC1"]), index=Fz7.index, columns=Fz7.columns); D_res = np.sqrt((RESID ** 2).mean(axis=1))
MEAS = ["cpi", "cpi_core", "pce", "pce_core", "cpi_median", "cpi_trim", "pce_trim", "cpi_sticky", "cpi_core_sticky", "cpi_flex", "cpi_core_flex"]
meas12 = B1[[f"{t}_12m" for t in MEAS]]; meas3 = B1[[f"{t}_3m" for t in MEAS]]; D_infl12 = meas12.std(axis=1); D_infl3 = meas3.std(axis=1)
DIS = pd.DataFrame({"D_sd (A)": D_sd, "D_res (B)": D_res, "D_infl_12m (C)": D_infl12, "D_infl_3m (C)": D_infl3})
R.p("Do today's indicators agree about inflation more or less than they usually do? Four complementary measures are used.")
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
R.h(2, "7. Historical analogs")
def analogs(V, k=15, exclude_months=24, min_gap=6):
    v0 = V.iloc[-1]; hist = V[V.index <= V.index[-1] - pd.DateOffset(months=exclude_months)].dropna(); dist = np.sqrt(((hist - v0) ** 2).sum(axis=1)).sort_values(); picked = []
    for t in dist.index:
        if all(abs((t - q).days) > min_gap * 30 for q in picked): picked.append(t)
        if len(picked) == k: break
    out = pd.DataFrame({"distance": dist[picked], "core PCE 12m then": pi12.reindex(picked)})
    for h in (3, 6, 12): out[f"next {h}m"] = Y[f"pi_fut_{h}"].reindex(picked)
    out["change 12m ahead"] = out["next 12m"] - out["core PCE 12m then"]; out["D_res then"] = D_res.reindex(picked); out.index = [d.strftime("%Y-%m") for d in out.index]; return out
A1 = analogs(Fz7); A2 = analogs(RESID); a1 = A1["change 12m ahead"]; outc = np.where(a1 < -0.5, "sustained disinflation", np.where(a1 > 0.5, "reacceleration", "mixed/flat"))
R.p("When in the past did the configuration of inflation signals look most like today?")
R.p(f"Nearest neighbors of today's standardized factor vector (Euclidean distance, excluding the last 24 months, at most one match per six-month window). Across the 15 analogs the median subsequent 12m core PCE is {A1['next 12m'].median():.2f} "
    f"(median change {a1.median():+.2f} pp, decelerating in {(a1 < 0).mean():.0%}). Matching on the pattern of disagreement instead gives {', '.join(A2.index[:5])} (median change {A2['change 12m ahead'].median():+.2f}). Not causal.")
R.table(A1, f"Analogs on the factor vector, origin {T:%b %Y}")

# =============================================================================== supply vs demand
R.h(2, "8. Supply-like versus demand-like episodes and disagreement")
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
R.p("Hypothesis: disagreement between inflation indicators and demand or financial indicators may be especially common when inflation is driven by supply or relative-price shocks rather than aggregate demand. "
    "This section is descriptive: episodes are classified by inflation and demand, disagreement is compared across them, and its correlates and predictive content are tested.")
R.p(f"Regimes from core PCE 12m and the demand block's first PC, each above or below its median. Current regime: {regime.iloc[-1]}. Descriptive only; a sign-restricted VAR or external instruments would be the structural extension.")
R.table(reg_tab, "Disagreement by regime"); R.table(pd.DataFrame(corr_rows).T, "Contemporaneous correlates of disagreement (standardized regressors, HAC t)")
R.table(PRED, "Subsequent change in core PCE on disagreement, current inflation, and the demand factor (HAC t)")

# =============================================================================== additional evidence
R.h(2, "9. Additional evidence")
R.p("Four further pieces of evidence feed the answers in the next section: the probability that inflation will be lower over each horizon, a horse race of individual statistics as additions to core PCE 12m, the history of inflation conditional on breadth, and an event study of episodes in which the 3-month rate fell well below the 12-month rate.")
prob = {}
for h in [3, 6, 12]:
    cols = SETS["M3 +global+block"]; rm = RM.loc[(h, "M3 +global+block"), "RMSFE"]; fc = today[f"{h}m"]["forecast M3"]
    lg = sm.Logit(D[f"decel_{h}"], sm.add_constant(D[cols]), missing="drop").fit(disp=0)
    prob[f"{h}m"] = {"P(lower) normal approx.": stats.norm.cdf((D.loc[T, "pi12"] - fc) / rm), "P(lower) logit": float(lg.predict(sm.add_constant(D[cols]).loc[[T]]).iloc[0]), "unconditional": D[f"decel_{h}"].mean()}
PROB = pd.DataFrame(prob); n_dec = int((meas3.loc[T].values < meas12.loc[T].values).sum())
CANDS = {"core PCE 3m": B1["pce_core_3m"], "core PCE 6m": B1["pce_core_6m"], "core PCE 3m-12m": B1["pce_core_3m_less_12m"], "core CPI 12m": B1["cpi_core_12m"], "median CPI 12m": B1["cpi_median_12m"], "median CPI 3m": B1["cpi_median_3m"],
         "trimmed PCE 12m": B1["pce_trim_12m"], "trimmed CPI 12m": B1["cpi_trim_12m"], "sticky CPI 12m": B1["cpi_sticky_12m"], "flexible CPI 12m": B1["cpi_flex_12m"], "breadth >3% (3m)": B2["share_gt3_3m"],
         "breadth >3% (12m)": B2["share_gt3_12m"], "xs dispersion (3m)": B2["xs_sd_3m"], "xs median (3m)": B2["xs_median_3m"], "SPF dispersion": B3["spf_cpi_4q_sd"], "Michigan 1y": B3["mich_1y"]}
DC = pd.concat([D[["pi12", "pi3"] + [f"pi_fut_{h}" for h in H] + [f"dpi_{h}" for h in H]], pd.DataFrame(CANDS)], axis=1).loc[D.index]; race = []
for name in CANDS:
    row = {"measure": name, "corr with core PCE 12m": DC[name].corr(DC["pi12"])}
    for h in [3, 6, 12]:
        base = oos_forecast(DC, f"pi_fut_{h}", ["pi12"], h); alt = oos_forecast(DC, f"pi_fut_{h}", ["pi12", name], h); e0 = (DC[f"pi_fut_{h}"] - base).dropna(); e1 = (DC[f"pi_fut_{h}"] - alt).dropna(); idx = e0.index.intersection(e1.index)
        row[f"rel RMSFE {h}m"] = np.sqrt((e1[idx] ** 2).mean() / (e0[idx] ** 2).mean()); row[f"t {h}m"] = ols(DC[f"dpi_{h}"], DC[["pi12", "pi3", name]], hac=h).tvalues[name]
    race.append(row)
RACE = pd.DataFrame(race).set_index("measure")
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
blk_pred = {f"{h}m": {c: f"{r.params[c]:+.2f} ({r.tvalues[c]:+.1f})" for c in F.columns} for h, r in [(h, ols(D[f"pi_fut_{h}"], D[SETS["M3 +global+block"]], hac=h)) for h in (3, 6, 12)]}
drivers = {b: (LB[b] * Z[b].iloc[-1].fillna(0)).sort_values(key=abs, ascending=False).head(5) for b in BLOCKS}
fin_vars = ["fedfunds", "real_10y_clev", "term_2s10s", "nfci", "vix", "baa_spread", "ebp", "term_premium_10y", "equity_12m_ret", "usd_12m", "mortgage_spread", "sloos_ci"]; tight_if_high = {"fedfunds", "real_10y_clev", "nfci", "vix", "baa_spread", "ebp", "mortgage_spread", "sloos_ci", "usd_12m", "term_premium_10y"}
fin_now = pd.DataFrame({"latest": [B5[c].dropna().iloc[-1] for c in fin_vars], "percentile": [pct_rank(B5[c]) for c in fin_vars]}, index=fin_vars); fin_now["side"] = ["tight" if ((c in tight_if_high) == (p > 50)) else "loose" for c, p in zip(fin_vars, fin_now["percentile"])]
exp_now = pd.DataFrame({"latest": [B3[c].dropna().iloc[-1] for c in ["mich_1y", "spf_cpi_4q", "clev_1y", "bei_5y", "bei_5y5y", "spf_cpi_10y", "spf_cpi_4q_sd", "mich_less_spf"]], "percentile": [pct_rank(B3[c]) for c in ["mich_1y", "spf_cpi_4q", "clev_1y", "bei_5y", "bei_5y5y", "spf_cpi_10y", "spf_cpi_4q_sd", "mich_less_spf"]]},
                       index=["mich_1y", "spf_cpi_4q", "clev_1y", "bei_5y", "bei_5y5y", "spf_cpi_10y", "spf_cpi_4q_sd", "mich_less_spf"])
dem_now = pd.DataFrame({"latest": [B4[c].dropna().iloc[-1] for c in ["unrate", "vu_ratio", "ahe_12m", "real_pce_6m"]], "percentile": [pct_rank(B4[c]) for c in ["unrate", "vu_ratio", "ahe_12m", "real_pce_6m"]]}, index=["unrate", "vu_ratio", "ahe_12m", "real_pce_6m"])
R.table(PROB, "Probability that core PCE inflation is lower over the next h months than the current 12m rate"); R.table(RACE[[f"rel RMSFE {h}m" for h in (3, 6, 12)] + ["corr with core PCE 12m", "type"]], "Horse race: each statistic added to core PCE 12m; relative RMSFE < 1 beats core PCE 12m alone")
R.table(cond, "Conditional history by breadth (share of categories above 3% at 12m)"); R.table(EV, "Spells with core PCE 3m at least 1 pp below 12m")

# =============================================================================== answers
R.h(2, "10. Answers")
z_now = Fz.iloc[-1]; pctF = {c: pct_rank(Fz[c]) for c in F.columns}; h12 = today["12m"]; lat12 = meas12.loc[T]; common12 = float(lat12.median())
above = [vname(c) for c in lat12.index[lat12 > common12 + 0.25]]; below = [vname(c) for c in lat12.index[lat12 < common12 - 0.25]]
sh = lambda k, h: B2[f"share_gt{k}_{h}m"].dropna().iloc[-1]; b3 = B2["share_gt3_3m"].dropna(); b12s = B2["share_gt3_12m"].dropna(); d12 = dec["12m"].iloc[1:-1]
rb, rb12, rmed, rtr = RACE.loc["breadth >3% (3m)"], RACE.loc["breadth >3% (12m)"], RACE.loc["median CPI 12m"], RACE.loc["trimmed PCE 12m"]; best = {h: RACE[f"rel RMSFE {h}m"].idxmin() for h in (3, 6, 12)}
p12 = PROB.loc["P(lower) normal approx.", "12m"]; rt = reg_tab["D_res mean"]; loose_share = (fin_now["side"] == "loose").mean(); pos_part = ", ".join(f"{k} {v:+.2f}" for k, v in d12[d12 > 0.01].items()) or "none"; neg_part = ", ".join(f"{k} {v:+.2f}" for k, v in d12[d12 < -0.01].items()) or "none"
def qa(title, lines): R.h(3, title); R.bullets(lines)
qa("1. Best estimate of underlying inflation today", [
   f"Core PCE {B1['pce_core_3m'].loc[T]:.1f} / {B1['pce_core_6m'].loc[T]:.1f} / {B1['pce_core_12m'].loc[T]:.1f} (3m/6m/12m); median CPI {B1['cpi_median_12m'].loc[T]:.1f}, trimmed PCE {B1['pce_trim_12m'].loc[T]:.1f}, sticky {B1['cpi_sticky_12m'].loc[T]:.1f}, flexible {B1['cpi_flex_12m'].loc[T]:.1f} (12m).",
   f"Common signal across the {len(MEAS)} 12m measures (median): {common12:.1f}. Above it by more than 0.25: {', '.join(above) or 'none'}; below: {', '.join(below) or 'none'}.",
   f"Disagreement among measures at the {ordinal(pct_rank(D_infl12))} percentile (12m) and {ordinal(pct_rank(D_infl3))} (3m): {'unusually high' if pct_rank(D_infl12) > 80 else 'unusually low' if pct_rank(D_infl12) < 20 else 'not unusual'}."])
qa("2. Accelerating or decelerating", [
   f"{n_dec} of {len(MEAS)} measures have 3m below 12m; core PCE 3m-12m gap {B1['pce_core_3m_less_12m'].loc[T]:+.1f} pp, 6m-12m {B1['pce_core_6m_less_12m'].loc[T]:+.1f}.",
   f"Factor model: {today['3m']['forecast M3']:.1f} / {today['6m']['forecast M3']:.1f} / {h12['forecast M3']:.1f} over 3/6/12m against a 12m rate of {h12['current 12m core PCE']:.1f}: {h12['direction']} ({h12['forecast change vs 12m']:+.2f} pp at 12m).",
   f"P(lower over 3/6/12m): normal approximation {PROB.loc['P(lower) normal approx.', '3m']:.0%} / {PROB.loc['P(lower) normal approx.', '6m']:.0%} / {p12:.0%}; logit {PROB.loc['P(lower) logit', '3m']:.0%} / {PROB.loc['P(lower) logit', '6m']:.0%} / {PROB.loc['P(lower) logit', '12m']:.0%} (unconditional about {PROB.loc['unconditional', '12m']:.0%})."])
qa("3. Breadth", [
   f"Share of categories above 2/3/4/5%: {100*sh(2,3):.0f} / {100*sh(3,3):.0f} / {100*sh(4,3):.0f} / {100*sh(5,3):.0f}% at 3m; {100*sh(2,12):.0f} / {100*sh(3,12):.0f} / {100*sh(4,12):.0f} / {100*sh(5,12):.0f}% at 12m.",
   f"Breadth (above 3%) is {'falling' if b3.iloc[-1] < b3.iloc[-4] else 'rising'} over three months at 3m ({100*(b3.iloc[-1]-b3.iloc[-4]):+.0f} pp) and {'falling' if b12s.iloc[-1] < b12s.iloc[-13] else 'rising'} over a year at 12m ({100*(b12s.iloc[-1]-b12s.iloc[-13]):+.0f} pp).",
   f"Historical position: breadth {ordinal(pct_rank(b3))} percentile (3m), {ordinal(pct_rank(b12s))} (12m); cross-sectional SD {ordinal(pct_rank(B2['xs_sd_3m']))}; upper-tail share {ordinal(pct_rank(B2['upper_tail_share_3m']))}.",
   f"Reading: {'broad-based' if pct_rank(b12s) > 60 else 'concentrated' if pct_rank(b12s) < 40 else 'middling'} at 12m; at 3m the rise is {'concentrated in a few categories' if pct_rank(B2['upper_tail_share_3m']) > 70 else 'not unusually concentrated'}."])
qa("4. Does breadth predict future inflation", [
   f"High-breadth months (top quartile): core PCE averaged {cond.loc['core PCE next 12m', 'high breadth (top quartile)']:.1f}% over the next 12m and stayed above 2.5% in {cond.loc['P(next 12m > 2.5%)', 'high breadth (top quartile)']:.0%} of cases, against {cond.loc['core PCE next 12m', 'low breadth (bottom quartile)']:.1f}% and {cond.loc['P(next 12m > 2.5%)', 'low breadth (bottom quartile)']:.0%} for low breadth. Inflation stayed elevated, but it was already high.",
   f"Given core PCE 12m and 3m, breadth (3m) has HAC t = {rb['t 3m']:+.1f} / {rb['t 6m']:+.1f} / {rb['t 12m']:+.1f} for the 3/6/12m change and relative RMSFE {rb['rel RMSFE 3m']:.2f} / {rb['rel RMSFE 6m']:.2f} / {rb['rel RMSFE 12m']:.2f}: little incremental content. Breadth at 12m: t {rb12['t 12m']:+.1f}, rel RMSFE {rb12['rel RMSFE 12m']:.2f}.",
   f"Against median CPI (rel RMSFE 12m {rmed['rel RMSFE 12m']:.2f}) and trimmed PCE ({rtr['rel RMSFE 12m']:.2f}), breadth is {'more' if rb['rel RMSFE 12m'] < min(rmed['rel RMSFE 12m'], rtr['rel RMSFE 12m']) else 'not more'} useful. In the factor regression the distribution block is the one block with a significant coefficient ({blk_pred['12m']['B_dist']} at 12m)."])
qa("5. Most useful current statistics", [
   f"Best single addition to core PCE 12m by horizon: 3m {best[3]} ({RACE.loc[best[3], 'rel RMSFE 3m']:.2f}); 6m {best[6]} ({RACE.loc[best[6], 'rel RMSFE 6m']:.2f}); 12m {best[12]} ({RACE.loc[best[12], 'rel RMSFE 12m']:.2f}). Gains are small everywhere.",
   f"Forward-looking (beats core PCE 12m alone at two or more horizons): {', '.join(RACE.index[RACE['type'] == 'forward-looking']) or 'none'}. Contemporaneous summaries (|corr| > 0.8, no out-of-sample gain): {', '.join(RACE.index[RACE['type'] == 'contemporaneous']) or 'none'}."])
qa("6. Recent favorable readings: signal or noise", [
   f"Spells with core PCE 3m at least 1 pp below 12m: {len(ev_hist)} since {D.index[0].year}; a genuine turning point (12m rate down at least 0.5 pp a year later) in {ev_hist['turning point'].mean():.0%}, reacceleration within six months in {ev_hist['reaccelerated within 6m'].mean():.0%}.",
   f"Today's gap is {gap.iloc[-1]:+.2f} pp ({'an event' if gap.iloc[-1] < -1 else 'below the event threshold'}). The factor-space analogs saw a median 12m change of {a1.median():+.2f} pp with deceleration in {(a1 < 0).mean():.0%} of cases: {'closer to a sustained disinflation' if a1.median() < -0.3 else 'closer to a soft patch than a sustained disinflation' if a1.median() > -0.1 else 'mixed'}."])
qa("7. Are financial conditions restrictive", [
   f"Financial factor (+ = looser) {z_now['B_fin']:+.2f} z, {ordinal(pctF['B_fin'])} percentile: {'unusually loose' if pctF['B_fin'] > 85 else 'on the loose side of history' if pctF['B_fin'] > 65 else 'unusually tight' if pctF['B_fin'] < 15 else 'on the tight side of history' if pctF['B_fin'] < 35 else 'near its historical middle'}.",
   f"{loose_share:.0%} of {len(fin_vars)} indicators sit on the loose side of their median: loose = {', '.join(fin_now.index[fin_now['side'] == 'loose'])}; tight = {', '.join(fin_now.index[fin_now['side'] == 'tight'])}.",
   f"Predictive content given inflation history: {blk_pred['3m']['B_fin']} / {blk_pred['6m']['B_fin']} / {blk_pred['12m']['B_fin']} at 3/6/12m (coefficient, HAC t); contribution to today's 12m forecast {dec.loc['financial', '12m']:+.2f} pp."])
qa("8. Is demand pressure still inflationary", [
   f"Demand factor {z_now['B_dem']:+.2f} z ({ordinal(pctF['B_dem'])} percentile); G2 {z_now['G2']:+.2f}. Predictive content given history: {blk_pred['3m']['B_dem']} / {blk_pred['6m']['B_dem']} / {blk_pred['12m']['B_dem']}; contribution to the 12m forecast {dec.loc['demand', '12m']:+.2f} pp.",
   f"Drivers today (loading x z): {', '.join(f'{vname(k)} {v:+.2f}' for k, v in drivers['dem'].items())}. Unemployment {dem_now.loc['unrate', 'latest']:.1f} ({ordinal(dem_now.loc['unrate', 'percentile'])} pct), V/U {dem_now.loc['vu_ratio', 'latest']:.2f}, wages {dem_now.loc['ahe_12m', 'latest']:.1f}%, real PCE 6m {dem_now.loc['real_pce_6m', 'latest']:.1f}%."])
qa("9. Are expectations a problem", [
   f"Levels: Michigan 1y {exp_now.loc['mich_1y', 'latest']:.1f} ({ordinal(exp_now.loc['mich_1y', 'percentile'])} pct), SPF 4q {exp_now.loc['spf_cpi_4q', 'latest']:.1f} ({ordinal(exp_now.loc['spf_cpi_4q', 'percentile'])}), 5y breakeven {exp_now.loc['bei_5y', 'latest']:.2f} ({ordinal(exp_now.loc['bei_5y', 'percentile'])}), 5y5y {exp_now.loc['bei_5y5y', 'latest']:.2f} ({ordinal(exp_now.loc['bei_5y5y', 'percentile'])}), SPF 10y {exp_now.loc['spf_cpi_10y', 'latest']:.1f}.",
   f"Disagreement: SPF cross-sectional SD {exp_now.loc['spf_cpi_4q_sd', 'latest']:.2f} ({ordinal(exp_now.loc['spf_cpi_4q_sd', 'percentile'])} pct); households minus professionals {exp_now.loc['mich_less_spf', 'latest']:+.1f} pp ({ordinal(exp_now.loc['mich_less_spf', 'percentile'])}).",
   f"Predictive content: expectations block given history {blk_pred['12m']['B_exp']} at 12m; SPF dispersion as a single addition, rel RMSFE {RACE.loc['SPF dispersion', 'rel RMSFE 12m']:.2f} (t {RACE.loc['SPF dispersion', 't 12m']:+.1f}); Michigan 1y {RACE.loc['Michigan 1y', 'rel RMSFE 12m']:.2f} (t {RACE.loc['Michigan 1y', 't 12m']:+.1f}). "
   f"Contribution to the 12m forecast {dec.loc['expectations', '12m']:+.2f} pp; the block is the {'most' if RESID.iloc[-1].idxmax() == 'B_exp' else 'not the most'} inflationary residual in the disagreement decomposition ({RESID.iloc[-1]['B_exp']:+.2f})."])
qa("10. What drives the current forecast", [
   f"12m forecast {dec.loc['forecast', '12m']:.1f}: history {d12['history']:+.2f}, all factors together {d12.drop('history').sum():+.2f} (table in section 5).", f"Pushing up: {pos_part}; pushing down: {neg_part}."])
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
   f"Projected core PCE stays {'above' if h12['forecast M3'] > 2 else 'at or below'} 2% at all horizons ({today['3m']['forecast M3']:.1f} / {today['6m']['forecast M3']:.1f} / {h12['forecast M3']:.1f}); projected change {h12['forecast change vs 12m']:+.2f} pp over 12m (history-only model {h12['forecast M1 history'] - h12['current 12m core PCE']:+.2f}).",
   f"Evidence for deceleration: {n_dec}/{len(MEAS)} measures decelerating, P(lower in 12m) {p12:.0%}, analogs decelerating {(a1 < 0).mean():.0%}: {'strong' if (p12 > 0.65 and n_dec >= 0.7*len(MEAS)) else 'moderate' if p12 > 0.5 else 'weak'}.",
   f"Uncertainty: 90% band {h12['90% band']}; block disagreement at the {ordinal(pct_rank(D_res))} percentile.",
   f"Risks implied by the outputs: persistence {'high' if h12['forecast M3'] > 2.75 else 'moderate' if h12['forecast M3'] > 2.25 else 'low'} (forecast level); reacceleration {'elevated' if (ev_hist['reaccelerated within 6m'].mean() > 0.5 or z_now['B_exp'] > 1) else 'moderate'} (expectations residual {RESID.iloc[-1]['B_exp']:+.2f}, historical reacceleration frequency {ev_hist['reaccelerated within 6m'].mean():.0%}); "
   f"premature tightening {'notable' if pctF['B_dem'] < 30 else 'limited'} (demand factor at the {ordinal(pctF['B_dem'])} percentile)."])
qa("15. Warsh, Waller, Kashkari", [
   f"Warsh (inflation broad, policy not restrictive): breadth at 12m at the {ordinal(pct_rank(b12s))} percentile ({100*b12s.iloc[-1]:.0f}% above 3%) and financial conditions at the {ordinal(pctF['B_fin'])} percentile on the loose side, so {'both legs' if pct_rank(b12s) > 60 and pctF['B_fin'] > 60 else 'the financial leg' if pctF['B_fin'] > 60 else 'the breadth leg' if pct_rank(b12s) > 60 else 'neither leg'} of the argument find support; demand at the {ordinal(pctF['B_dem'])} percentile does not.",
   f"Waller (underlying inflation declining): {n_dec}/{len(MEAS)} measures show 3m below 12m; the model projects {h12['forecast change vs 12m']:+.2f} pp over 12m with P(lower) {p12:.0%}, so the momentum is {'confirmed' if p12 > 0.6 else 'only partly confirmed'}; comparable gaps were turning points {ev_hist['turning point'].mean():.0%} of the time.",
   f"Kashkari (entrenchment from waiting): the 12m forecast stays at {h12['forecast M3']:.1f}%, the expectations block is the most inflationary residual ({RESID.iloc[-1]['B_exp']:+.2f}) with households {exp_now.loc['mich_less_spf', 'latest']:+.1f} pp above professionals, and analogs reaccelerated in {np.mean(outc == 'reacceleration'):.0%} of cases: "
   f"{'supports' if (h12['forecast M3'] > 2.75 and RESID.iloc[-1]['B_exp'] > 0.5) else 'partly supports'} the concern on level and expectations, {'less so' if np.mean(outc == 'reacceleration') < 0.3 else 'and'} on historical reacceleration."])
R.p("Caveat: latest-vintage data and full-sample factor loadings; the news decomposition is pseudo-real-time (no data revisions; publication lags only at the ragged edge). Rule-based wording thresholds are in the answers section of run.py.")
R.summary([
    f"Core PCE runs at {B1['pce_core_12m'].loc[T]:.1f} percent over 12 months and {B1['pce_core_3m'].loc[T]:.1f} over 3 months; the median across eleven measures is {common12:.1f}, and {n_dec} of {len(MEAS)} measures show 3m below 12m.",
    f"The factor model projects {today['3m']['forecast M3']:.1f} / {today['6m']['forecast M3']:.1f} / {h12['forecast M3']:.1f} percent over 3/6/12 months, a change of {h12['forecast change vs 12m']:+.2f} pp at 12 months; the probability of lower inflation over 12 months is {p12:.0%} (normal approximation) to {PROB.loc['P(lower) logit', '12m']:.0%} (logit).",
    f"Out of sample the factors do not beat inflation history (relative RMSFE {RM.loc[(12, 'M3 +global+block'), 'rel_RMSFE']:.2f} at 12 months); the distribution block is the only factor with a significant coefficient.",
    f"Breadth: {100*b12s.iloc[-1]:.0f} percent of categories above 3 percent at 12 months ({ordinal(pct_rank(b12s))} percentile), {100*b3.iloc[-1]:.0f} percent at 3 months ({ordinal(pct_rank(b3))}).",
    f"Financial conditions sit at the {ordinal(pctF['B_fin'])} percentile on the loose side; demand at the {ordinal(pctF['B_dem'])}; expectations are the outlier, with households {exp_now.loc['mich_less_spf', 'latest']:+.1f} pp above professionals and SPF dispersion at the {ordinal(exp_now.loc['spf_cpi_4q_sd', 'percentile'])} percentile.",
    f"Cross-block disagreement is at the {ordinal(pct_rank(D_res))} percentile; the closest analogs are {', '.join(A1.index[:4])}, after which core PCE changed by {a1.median():+.2f} pp (median) over 12 months.",
    f"Current regime: {regime.iloc[-1]}."])
R.write("report"); print(f"report.md / report.html written in {time.time()-t0:.0f}s; {len(list(FIG.glob('*.png')))} figures")
