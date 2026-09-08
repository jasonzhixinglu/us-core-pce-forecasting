"""Editable prose for the US inflation signals report.

TEXT holds the fixed paragraphs, keyed as used in run.py (the key hints at the paragraph's opening words). READING holds the one-line factor
interpretations. Sentences that embed computed numbers stay in run.py as f-strings.
"""

TEXT = {
 'p01_all_of_these_are_treated_as_po':
  "All of these are treated as potentially useful signals for future inflation rather than sorted into 'measures of underlying inflation' and 'predictors'. A measure of underlying inflation is useful partly because it extracts the persistent, forecast-relevant component of current inflation, so the two roles are not distinct.",

 'p02_for_the_linear_m3_equation_eac':
  "For the linear M3 equation each contribution is the coefficient times the current value's deviation from its sample mean, so contributions sum to the forecast's deviation from the target's mean. This says which signals, at their current values, push the forecast away from its mean; it is not a news decomposition.",

 'p03_do_today_s_indicators_agree_ab':
  "Do today's indicators agree about inflation more or less than they usually do? Four complementary measures are used.",

 'p04_when_in_the_past_did_the_confi':
  'When in the past did the configuration of inflation signals look most like today?',

 'p05_four_further_pieces_of_evidenc':
  'Four further pieces of evidence feed the answers in the next section: the probability that inflation will be lower over each horizon, a horse race of individual statistics as additions to core PCE 12m, the history of inflation conditional on breadth, and an event study of episodes in which the 3-month rate fell well below the 12-month rate.',

 'p06_caveat_latest_vintage_data_an':
  'Caveat: latest-vintage data and full-sample factor loadings; the news decomposition is pseudo-real-time (no data revisions; publication lags only at the ragged edge). Rule-based wording thresholds are in the answers section of run.py.',

}

READING = {   # one-line interpretations of the estimated factors; the data-driven description printed beside each is the check
 ("infl", 1): "Reading: the common level of inflation across headline, core, trimmed and median measures at every horizon; a level factor.",
 ("infl", 2): "Reading: short-horizon flexible-price inflation (1m to 6m), the volatile food, energy and goods component that moves independently of the common level; the PCA forms the momentum contrast itself.",
 ("dist", 1): "Reading: breadth and central tendency of the price-change distribution, how many categories are rising fast; a broad-inflation factor.",
 ("dist", 2): "Reading: two-sided dispersion (IQR, share decelerating) against upper-tail concentration and skewness; separates wide relative-price dispersion from a few categories spiking.",
 ("exp", 1): "Reading: the level of expected inflation across markets, the Cleveland model, professionals and households; an expectations-level factor.",
 ("exp", 2): "Reading: forecaster dispersion and household expectations against the long-run anchors (SPF 10-year, Cleveland 10-year); a near-term uncertainty versus anchoring factor.",
 ("dem", 1): "Reading: output and employment growth; the business-cycle factor.",
 ("dem", 2): "Reading: wage growth and labor-market tightness (V/U, quits) against unemployment and activity momentum; a wage-pressure factor distinct from output growth.",
 ("fin", 1): "Reading: the level of nominal, real and mortgage rates, inverted, so that higher = lower rates = looser; the rates dimension of financial conditions.",
 ("fin", 2): "Reading: credit spreads, the excess bond premium, the NFCI and lending standards against equity returns; the risk-pricing or stress dimension (higher = more stress).",
 "G1": "Reading: the common inflation level, dominated by trimmed, core and headline rates at 3 to 12 months; the state the underlying-inflation measures try to track.",
 "G2": "Reading: activity and investment growth with short-horizon inflation, against tight lending standards and wide spreads; a demand-pressure state.",
}
