"""Editable prose for the US inflation signals report.

TEXT holds the fixed paragraphs, keyed as used in run.py (the key hints at the paragraph's opening words). READING holds the one-line factor
interpretations. Sentences that embed computed numbers stay in run.py as f-strings.
"""

TEXT = {
 'p01_all_of_these_are_treated_as_po':
  "All of these are potentially useful signals for future inflation. Our analysis takes the following steps. Indicators are organized into five blocks and each block is first examined on its own. Then we combine information across all five blocks to forecast core PCE inflation 3, 6, 12, and 24 months ahead, and this current forecast is decomposed into contributions from different sources of news. Finally, we investigate the degree of disagreement across signals, and look toward what this implies for today's configuration of shocks.",

 'p02_for_the_linear_m3_equation_eac':
  "For the linear M3 equation each contribution is the coefficient times the current value's deviation from its sample mean, so contributions sum to the forecast's deviation from the target's mean. This says which signals, at their current values, push the forecast away from its mean; it is not a news decomposition.",

 'p03_do_today_s_indicators_agree_ab':
  "Do today's indicators agree about inflation more or less than they usually do? Four complementary measures are used.",

 'p04_when_in_the_past_did_the_confi':
  'We next ask when in the past the configuration of inflation signals looked most like today.',

 'p05_four_further_pieces_of_evidenc':
  'Four further pieces of evidence feed the answers in the next section: the probability that inflation will be lower over each horizon, a horse race of individual statistics as additions to core PCE 12m, the history of inflation conditional on breadth, and an event study of episodes in which the 3-month rate fell well below the 12-month rate.',

 'p06_caveat_latest_vintage_data_an':
  'Caveat: latest-vintage data and full-sample factor loadings; the news decomposition is pseudo-real-time (no data revisions; publication lags only at the ragged edge). Rule-based wording thresholds are in the answers section of run.py.',

 'p07_we_ask_what_the_current_config':
  "We ask what current indicators imply for future US inflation, how much the indicators agree or disagree with one another, and what they say about the distribution of today's shocks relative to historical episodes.",

 'p07b_the_motivation_is_the_current':
  "This is motivated by the current debate around the Fed's September meeting, in which policymakers emphasize different statistics: recent inflation momentum, median and trimmed measures, the breadth of price increases, expectations, labor-market conditions, demand, and financial conditions.",

 'p08_the_approach_has_five_steps_p':
  "The approach has five steps. Predictors are organized into five blocks and each block is examined on its own. Two global factors are extracted from the full panel and one factor from each block's residual. Core PCE inflation is forecast at 3, 6, and 12 months with nested direct regressions. The current forecast is decomposed into contributions from inflation history and each factor, and forecast revisions are decomposed into news. Finally, disagreement across signals is measured, historical analogs are found, and disagreement is related to supply-like and demand-like episodes.",

 'p09_data_are_latest_vintage_fred_s':
  'Data are latest-vintage FRED series (CSV endpoint, no key). Two inputs are not on FRED and are flagged where used: the Survey of Professional Forecasters individual CPI forecasts (Philadelphia Fed) and the excess bond premium (Federal Reserve). Pseudo-out-of-sample results computed on revised data are not real-time results; the data loader is isolated so that ALFRED vintages can be substituted later.',

 'p10_for_each_block_the_same_diagno':
  "For each block the same diagnostic is shown: the variables are standardized, a principal-components decomposition is computed, and four panels report the scree (evidence of one versus several dimensions), the correlation of each variable with the first component (closer to one means more aligned with the block's common factor), the first component over time as a one-line summary of the block, and the residuals from the one-factor fit as a heatmap (whether recent months look different from history).",

 'p11_only_levels_at_several_horizon':
  'Only levels at several horizons enter the block. Momentum and acceleration (3m minus 12m, changes in the 12m rate) are deliberately not included as separate indicators: they are linear combinations of what is already in the panel, and the PCA recovers them itself as contrasts, with opposite loadings on short- and long-horizon rates. The forecasting regressions in section 3 use momentum terms computed directly from core PCE.',

 'p12_levels_of_expected_inflation_f':
  'Levels of expected inflation from households, professionals, a model and markets at short and long horizons, plus forecaster dispersion. Spreads between sources and horizons are not included as separate indicators; the PCA forms them as contrasts. Michigan 5-10 year expectations and Michigan respondent dispersion are not on FRED and are omitted rather than proxied.',

 'p13_rates_in_levels_quantities_as':
  'Rates in levels, quantities as annualized 3/6-month or 12-month log growth, quarterly series spread over their quarter. Real business fixed and residential investment on FRED start in 2007, so total real private investment stands in.',

 'p14_monthly_averages_of_daily_data':
  'Monthly averages of daily data. Policy and Treasury rates, real rates (TIPS and the 10-year yield minus Cleveland Fed expectations), the NFCI and adjusted NFCI, VIX, the Baa spread, the GZ spread and excess bond premium, the term premium, equity returns, a spliced broad dollar, oil and commodity prices, lending standards and the mortgage rate. Spreads between panel members (term spread, mortgage spread) are left for the PCA to form. The factor is oriented so that positive = looser.',

 'p15_the_factor_model_is_x_lambda':
  "We next combine the five blocks in a dynamic factor model, X = Lambda_G G + lambda_B B + e, allowing two global factors common to the whole panel and one factor specific to each block, with the seven evolving as a joint VAR(1) and each series carrying an AR(1) idiosyncratic component. We estimate it by expectation-maximization, and it is operationalized as a Kalman filter. Signs are normalized so that every factor is positively related to inflation.",

 'p16_core_pce_is_the_target_the_de':
  "Core PCE is the target. The dependent variables are future annualized core PCE inflation over 3, 6, 12 and 24 months, its change relative to today's 12-month rate, and an indicator for deceleration. Three nested direct regressions are compared: M1 uses inflation history and momentum only (12m rate, its 12-month lag, 3m and 6m rates, the 3-month change in the 12m rate, acceleration); M2 adds the two global factors; M3 adds the five block factors.",

 'p17_hypothesis_disagreement_betwe':
  'Hypothesis: disagreement between inflation indicators and demand or financial indicators may be especially common when inflation is driven by supply or relative-price shocks rather than aggregate demand. This section is descriptive: episodes are classified by inflation and demand, disagreement is compared across them, and its correlates and predictive content are tested.',

 's02_we_collect_data_across_five_bl':
  "To project its future trajectory, we collect data across five blocks: inflation measures, inflation distribution measures, inflation expectations measures, demand-side measures, and financial-side measures.",

 's04_the_first_common_factor_in_eac':
  "The first common factor in each of the five blocks is near its historical average: we don't see evidence of overheating, but neither do we see evidence of current conditions being significantly restrictive. The residuals point to inflation expectations running hotter than expected while demand is somewhat weaker than expected, consistent with recent supply-side shocks from energy and tariffs.",

 's05_while_we_dont_see_evidence_of':
  "While we don't see evidence of overheating, we also don't see evidence of current conditions being significantly restrictive.",

 's06_across_the_second_principal_co':
  "Across the second principal components, we see secondary evidence of a higher-than-average wedge between household and professional inflation expectations, a tighter-than-average labor market, and signs of lower-than-usual financial stress.",

 'p18_analogs_the_three_closest_prof':
  "Economic conditions were only partly similar. July 2006 is the closest match: the end of an energy shock, with headline running a point above core, household expectations above professional forecasts, and the Fed at the end of a tightening cycle; the shock did not pass into core, which was 2.0 a year later. May 1993 shares the residual pattern but not the economics: oil was flat, headline sat below core, and the economy was in a post-recession disinflation. December 2015 is the mirror in every block, the reverse relative-price shock after the oil collapse, after which core drifted up from 1.2 to 1.8 as the shock faded. Today differs from all three in level: core is 3.3, a full point above trimmed PCE, with the widest gap between household and professional expectations of the four and the weakest payroll growth.",

 's07_the_five_blocks_of_indicators_a':
  "The five blocks of indicators all reflect a general inflation common factor, which is currently about neutral, but the residuals show that inflation expectations run hotter than expected while demand is somewhat weaker than expected, perhaps reflecting recent supply-side shocks from energy and tariffs.",

 'p19_news_the_dfm_forecast_is_primar':
  "The DFM forecast revisions are driven primarily by news in the basic inflation indicators and in the indicators of inflation dispersion across categories. Contributions were positive in every month from January to May 2026; June saw a large reversal on lower inflation prints, and the news from July has so far been broadly neutral.",

 'p20_info_while_all_models_project':
  "While all three models project inflation to decelerate, the large-scale DFM (M3) projects the fastest convergence, and the smaller information sets in M1 and M2 project a slower pace. In particular, M1 and M2 do not project inflation to return to within 50 basis points of the 2 percent target within 24 months. It is worth noting that the stronger persistence of the time-series forecast may reflect the longer lag structure selected by AIC, whereas the DFM uses a VAR(1) specification that mechanically favors faster mean reversion.",

 'p21_info_notably_the_pseudo_out_of':
  "Notably, the smaller models outperform the larger ones pseudo-out-of-sample. This may reflect overfitting, and the differences are unlikely to be significant under a formal equal-predictive-ability test, but it highlights that the projection of quickly decelerating inflation over the next 12 months may not be robust.",

 'p22_sec3_we_focus_on_the_first_prin':
  "Do today's indicators agree about inflation more or less than they usually do? We focus on the first principal component from each block in section 1 and fit a one-factor PCA model to these five block-level common factors.",

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

BLOCK_PROSE = {   # two paragraphs per block, read off the block figure: what PC1 and PC2 are, and where each stands now
 "infl": [
  "PC1 is the general inflation factor, comoving positively with all inflation measures and correlating most strongly with recent core and trimmed-mean measures. It currently sits close to its historical average.",
  "PC2 captures momentum, loading positively on 3m measures and negatively on 12m measures, so it turns negative when inflation is decelerating. It rose with the Iran war and has since returned to average, without yet turning negative.",
 ],
 "dist": [
  "PC1 is the breadth factor, comoving positively with the share of categories rising quickly and with median category inflation, and correlating most strongly with the 6-month breadth measures. Breadth spiked to +1.5 standard deviations three months ago and has since returned to average.",
  "PC2 separates wide two-sided dispersion from right-tailed concentration, loading positively on the interquartile range and negatively on skewness and the upper-tail share, so it turns negative when a few categories are accelerating rather than the whole distribution shifting. It ran close to -1.5 through the middle of the year, reflecting energy- and tariff-related inflation passthrough, but has since returned to average.",
 ],
 "exp": [
  "PC1 is the overall level of expected inflation, comoving positively with every source and correlating most strongly with the Cleveland Fed measures and the SPF one-year forecast. It currently sits close to its historical average.",
  "PC2 is the wedge between near-term disagreement and long-run expectations, loading positively on forecaster dispersion and household expectations and negatively on the 10-year measures, so it turns positive when households and near-term forecasters run ahead of the long-run view. It sits modestly above average, having partially unwound its spike earlier in the year.",
 ],
 "dem": [
  "PC1 is the standard business-cycle factor, comoving positively with output, employment and real spending growth, and correlating most strongly with year-on-year GDP and compensation growth. It currently sits a little below its historical average.",
  "PC2 is the wage-pressure factor, loading positively on wage growth, the vacancy-unemployment ratio and quits and negatively on unemployment, so it turns positive when the labor market is tight relative to activity. It remains above average, though it has drifted down steadily over the year.",
 ],
 "fin": [
  "PC1 is the common factor of interest rates, inverted so that positive implies looser financial conditions, and correlating most strongly with the mortgage rate, the 10-year real rate and the 10-year Treasury yield. Rates sit at about their historical average.",
  "PC2 is the risk-pricing dimension, loading positively on credit spreads, the excess bond premium, the VIX and the NFCI, so it turns positive when financial stress is elevated. It sits well below average: the pricing of risk is unusually cheap.",
 ],
}

SECTION2 = {   # factor interpretations, written against the estimated loadings (run.py prints them to the console)
 'factors':
  "G1 is the common inflation level factor: it loads most heavily on the SPF one-year forecast and on trimmed-mean CPI and PCE at 3 and 6 months, and accounts for roughly three quarters of the variance of the average inflation series. "
  "G2 is a relative-price factor: it loads on flexible-price CPI, the upper-tail share of the category distribution and commodity PPI, so it rises when a narrow set of volatile prices moves rather than the whole distribution.",

 'blocks':
  "The block factors explain what remains in each block once the global factors are accounted for:",
}

BLOCK_FACTOR = {   # one line per block factor
 "infl": "B_infl: lifts the share of inflation-block variance explained from 74 to 77 percent, so it adds little the global states do not already carry.",
 "dist": "B_dist: captures dispersion across categories, loading on the cross-sectional standard deviation and the 90-10 spread.",
 "exp": "B_exp: captures near-term disagreement against long-run anchoring, positive on SPF dispersion and negative on the Cleveland and SPF 10-year expectations.",
 "dem": "B_dem: captures the activity business cycle, loading on year-on-year GDP, real consumption and industrial production, but not so much on labor-market tightness.",
 "fin": "B_fin: captures the level of interest rates, inverted, loading on the 10-year real rate, the 10-year yield and the term premium.",
}
