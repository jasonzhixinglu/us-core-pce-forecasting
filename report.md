
# US inflation signals: agreement, disagreement, and forecasting

**Summary**

- Core PCE runs at 3.3 percent over 12 months and 3.0 percent annualized over 3 months.
- We collect data across five blocks: inflation measures, inflation distribution measures, inflation expectations measures, demand-side measures, and financial-side measures.
- The dynamic factor model that leverages data across all five blocks projects core PCE inflation of 3.2 / 3.2 / 3.1 percent annualized over the next 3/6/12 months, that is, a deceleration of 0.2 pp over the 12 months, and inflation is not expected to return to target over the near term.
- The first common factor in each of the five blocks is near its historical average, although we see some notable divergence in the second factors.
- While we don't see evidence of overheating, we also don't see evidence of current conditions being significantly restrictive.
- Across the second principal components, we see secondary evidence of a higher-than-average wedge between household and professional inflation expectations, a tighter-than-average labor market, and signs of lower-than-usual financial stress.


## Introduction

We ask what the current configuration of inflation-related indicators implies for future US inflation, how much the indicators agree or disagree with one another, and what they say about the distribution of today's shocks relative to historical episodes.

The motivation is the current Fed debate, in which policymakers emphasize different statistics: recent inflation momentum, median and trimmed measures, the breadth of price increases, expectations, labor-market conditions, demand, and financial conditions.

All of these are treated as potentially useful signals for future inflation. Our analysis takes the following steps. Predictors are organized into five blocks and each block is first examined on its own. Then we combine information across all five blocks to forecast core PCE inflation 3, 6, and 12 months ahead, and this current forecast is decomposed into contributions from different sources of news. Finally, we investigate the degree of disagreement across signals, and look toward what this implies for today's configuration of shocks.


## 1. The five blocks


### Block 1: inflation measures

*Block 1 indicators*

| shorthand | indicator | source | transformation |
|---|---|---|---|
| cpi_{1,3,6,12}m | CPI, all items | BLS via FRED | annualized 1/3/6/12-month log change of the index |
| cpi_core_{1,3,6,12}m | CPI ex food and energy | BLS via FRED | annualized 1/3/6/12-month log change of the index |
| pce_{1,3,6,12}m | PCE price index | BEA via FRED | annualized 1/3/6/12-month log change of the index |
| pce_core_{1,3,6,12}m | PCE ex food and energy | BEA via FRED | annualized 1/3/6/12-month log change of the index |
| cpi_svc_xe_{1,3,6,12}m | CPI services ex energy services | BLS via FRED | annualized 1/3/6/12-month log change of the index |
| pce_svc_{1,3,6,12}m | PCE services price index | BEA via FRED | annualized 1/3/6/12-month log change of the index |
| cpi_median_{1,3,6,12}m | Median CPI | Cleveland Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |
| cpi_trim_{1,3,6,12}m | 16% trimmed-mean CPI | Cleveland Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |
| pce_trim_{1,3,6,12}m | Trimmed-mean PCE | Dallas Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |
| cpi_sticky_{1,3,6,12}m | Sticky-price CPI | Atlanta Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |
| cpi_core_sticky_{1,3,6,12}m | Core sticky-price CPI | Atlanta Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |
| cpi_flex_{1,3,6,12}m | Flexible-price CPI | Atlanta Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |
| cpi_core_flex_{1,3,6,12}m | Core flexible-price CPI | Atlanta Fed via FRED | published 1-month annualized and 12-month rates; 3m and 6m as rolling means of the 1-month rate |

![Block 1, inflation measures](figures/block_infl.png)
*Block 1, inflation measures*

PC1 is the general inflation factor, and comoves positively with all inflation measures, and correlation is highest with recent core and trimmed mean inflation measures. This measure is overall about neutral.

PC2 is capturing momentum, loading positively on 3m inflation measures and negatively on 12m inflation measures, so PC2 is negative when inflation is decelerating. Inflation was recently accelerating since the Iran war, but has now come back down to about neutral.


### Block 2: price-change distribution

*Block 2 universe: 34 CPI expenditure categories (FRED, seasonally adjusted)*

| Group | Categories |
|---|---|
| Food (7) | cereals; meats, poultry, fish, eggs; dairy; fruits and vegetables; other food at home; food away from home; alcohol |
| Energy (4) | gasoline; fuel oil; electricity; utility gas |
| Core goods (12) | men's, women's and infants' apparel; footwear; new and used vehicles; vehicle parts; medical commodities; household furnishings; tobacco; recreation commodities; educational books |
| Services (11) | rent; owners' equivalent rent; lodging away from home; water and sewer; professional medical and hospital services; vehicle maintenance; public transportation; tuition and childcare; personal care; other services |

*Block 2 indicators*

| shorthand | indicator | source | transformation |
|---|---|---|---|
| share_gt{0,2,3,4,5}_{3,6,12}m | share of categories with inflation above 0/2/3/4/5 percent | 34 CPI categories, BLS via FRED | count divided by categories available; computed on annualized 3/6/12-month category inflation |
| share_accel_{3,6,12}m | share of categories accelerating | 34 CPI categories, BLS via FRED | h-month rate above the 12-month rate (at h = 12: above the 12-month rate a year earlier); computed on annualized 3/6/12-month category inflation |
| share_decel_{3,6,12}m | share of categories decelerating | 34 CPI categories, BLS via FRED | as above, below; computed on annualized 3/6/12-month category inflation |
| xs_sd_{3,6,12}m | cross-sectional standard deviation | 34 CPI categories, BLS via FRED | across categories; computed on annualized 3/6/12-month category inflation |
| xs_iqr_{3,6,12}m | interquartile range | 34 CPI categories, BLS via FRED | 75th minus 25th percentile across categories; computed on annualized 3/6/12-month category inflation |
| xs_p90_p10_{3,6,12}m | 90-10 spread | 34 CPI categories, BLS via FRED | 90th minus 10th percentile; computed on annualized 3/6/12-month category inflation |
| xs_skew_{3,6,12}m | cross-sectional skewness | 34 CPI categories, BLS via FRED | computed on annualized 3/6/12-month category inflation |
| xs_median_{3,6,12}m | median category inflation | 34 CPI categories, BLS via FRED | computed on annualized 3/6/12-month category inflation |
| upper_tail_share_{3,6,12}m | upper-tail share | 34 CPI categories, BLS via FRED | share of the sum of absolute category inflation coming from the top decile; computed on annualized 3/6/12-month category inflation |

![Block 2, price-change distribution](figures/block_dist.png)
*Block 2, price-change distribution*

PC1 is the breadth factor, and comoves positively with the share of categories rising quickly and with median category inflation, and correlation is highest with the 6-month measures. Breadth spiked to +1.5 standard deviations three months ago but has since come back to about neutral.

PC2 separates wide two-sided dispersion from upper-tail concentration, loading positively on the interquartile range and negatively on skewness and the upper-tail share, so PC2 is negative when a few categories are doing the work rather than the whole distribution shifting. PC2 ran close to -1.5 through the middle of the year, and has since returned to about neutral.


### Block 3: inflation expectations

*Block 3 indicators*

| shorthand | indicator | source | transformation |
|---|---|---|---|
| mich_1y | Michigan 1-year expected inflation, median | Michigan survey via FRED | level, percent |
| clev_1y | Cleveland Fed 1-year expected inflation | Cleveland Fed via FRED | level |
| clev_10y | Cleveland Fed 10-year expected inflation | Cleveland Fed via FRED | level |
| bei_5y | 5-year breakeven inflation | Treasury via FRED | monthly mean of daily |
| bei_10y | 10-year breakeven | Treasury via FRED | monthly mean |
| bei_5y5y | 5y5y forward breakeven | Treasury via FRED | monthly mean |
| spf_cpi_4q | SPF median CPI forecast, next four quarters | Philadelphia Fed SPF (not on FRED) | mean of the individual CPI2-CPI5 forecasts, median across forecasters; quarterly spread to months |
| spf_cpi_4q_iqr | SPF cross-sectional IQR of the 4-quarter forecast | Philadelphia Fed SPF | 75th minus 25th percentile across forecasters |
| spf_cpi_4q_sd | SPF cross-sectional SD of the 4-quarter forecast | Philadelphia Fed SPF | across forecasters |
| spf_cpi_10y | SPF median 10-year CPI forecast | Philadelphia Fed SPF | quarterly spread to months |

![Block 3, expectations](figures/block_exp.png)
*Block 3, expectations*

PC1 is the level of expected inflation, and comoves positively with every source, and correlation is highest with the Cleveland model and the SPF one-year forecast. The level is about neutral.

PC2 is the wedge between near-term uncertainty and long-run anchoring, loading positively on forecaster dispersion and household expectations and negatively on the 10-year anchors, so PC2 is positive when households and near-term forecasters run ahead of the anchors. It sits modestly above average, having spiked earlier in the year.


### Block 4: demand and labor

*Block 4 indicators*

| shorthand | indicator | source | transformation |
|---|---|---|---|
| unrate | Unemployment rate | BLS via FRED | level, percent |
| payrolls_3m / payrolls_12m | Nonfarm payrolls | BLS via FRED | annualized 3- and 12-month log growth |
| claims_log | Initial claims | DOL via FRED | log of the monthly mean of weekly claims |
| vu_ratio | Job openings to unemployed | BLS JOLTS via FRED | ratio |
| quits | Quits rate | BLS JOLTS via FRED | level, percent |
| ahe_3m / ahe_12m | Average hourly earnings, production workers | BLS via FRED | annualized 3- and 12-month log growth |
| eci_wages_yoy | ECI wages and salaries | BLS via FRED | year-on-year percent, quarterly spread to months |
| comp_12m | Compensation of employees | BEA via FRED | 12-month log growth |
| real_pce_6m / real_pce_12m | Real PCE | BEA via FRED | annualized 6- and 12-month log growth |
| real_retail_6m | Real retail sales | Census via FRED | annualized 6-month log growth |
| ip_6m / ip_12m | Industrial production | Fed via FRED | annualized 6- and 12-month log growth |
| capu | Capacity utilization | Fed via FRED | level, percent |
| real_inv_yoy | Real gross private domestic investment | BEA via FRED | year-on-year, quarterly spread to months |
| gdp_yoy | Real GDP | BEA via FRED | year-on-year, quarterly spread to months |
| sentiment | Michigan consumer sentiment | Michigan via FRED | level |

![Block 4, demand and labor](figures/block_dem.png)
*Block 4, demand and labor*

PC1 is the business-cycle factor, and comoves positively with output, employment and real spending growth, and correlation is highest with year-on-year GDP and compensation. Activity sits a little below its historical average.

PC2 is the wage-pressure factor, loading positively on wage growth, the vacancy-unemployment ratio and quits and negatively on unemployment, so PC2 is positive when the labor market is tight relative to activity. It remains above average, though it has drifted down steadily over the past year.


### Block 5: financial conditions and risk pricing

*Block 5 indicators*

| shorthand | indicator | source | transformation |
|---|---|---|---|
| fedfunds | Effective federal funds rate | Fed via FRED | monthly mean, percent |
| dgs2 / dgs10 | 2- and 10-year Treasury yields | Treasury via FRED | monthly mean of daily |
| real_10y_tips | 10-year TIPS yield | Treasury via FRED | monthly mean |
| real_10y_clev | 10-year real rate | derived | 10-year yield minus Cleveland Fed 10-year expected inflation (the expectation is in block 3, so this is not a within-block difference) |
| nfci / anfci | Chicago Fed NFCI and adjusted NFCI | Chicago Fed via FRED | monthly mean; positive = tighter |
| vix | VIX | Cboe via FRED | monthly mean |
| baa_spread | Moody's Baa yield minus 10-year Treasury | FRED (published spread) | monthly mean |
| gz_spread / ebp | Gilchrist-Zakrajsek spread and excess bond premium | Federal Reserve (not on FRED) | level |
| term_premium_10y | Kim-Wright 10-year term premium | Fed via FRED | monthly mean |
| equity_3m_ret / equity_12m_ret | Nasdaq composite | FRED | 3- and 12-month log return (the S&P 500 on FRED covers ten years only) |
| usd_12m | Broad dollar index | Fed via FRED | 12-month log change; 1973-2019 and 2006- indexes spliced at the overlap |
| oil_3m / oil_12m | WTI crude oil | FRED | 3- and 12-month log change |
| ppi_comm_12m | PPI all commodities | BLS via FRED | 12-month log change |
| sloos_ci | SLOOS net share tightening C&I standards | Fed via FRED | quarterly spread to months |
| mortgage30 | 30-year mortgage rate | Freddie Mac via FRED | monthly mean |

![Block 5, financial conditions (+ = looser)](figures/block_fin.png)
*Block 5, financial conditions (+ = looser)*

PC1 is the rates dimension of financial conditions, inverted so that positive means looser, and correlation is highest with the mortgage rate, the 10-year real rate and the 10-year Treasury yield. Rates sit at about their historical average, so this dimension is neither restrictive nor accommodative.

PC2 is the risk-pricing dimension, loading positively on credit spreads, the excess bond premium, the VIX and the NFCI, so PC2 is positive when financial stress is elevated. It sits well below average, so risk pricing is unusually benign rather than stressed.


## 2. Factor structure

The factor model is X = Lambda_G G + lambda_B B + e: two global factors common to the whole panel and one factor specific to each block. The implementation is simple: standardize the panel, extract two principal components, subtract the fitted global component, and take the first principal component of each block's residual. Signs are normalized so that every factor is oriented as inflationary pressure (the financial factor: looser conditions). A VAR(1) on the seven factors provides the dynamics used in the news decomposition.

The panel has 140 variables from 1985-01 to 2026-07. Two global PCs on the standardized panel explain 52% of its variance (G1 39%, G2 13%); one PC per block on the residual explains infl 20%, dist 28%, exp 50%, dem 31%, fin 34% of the block's residual variance. Every factor is oriented so that higher = more inflationary pressure (financial: looser). VAR(1) own-persistence: G1 0.97, G2 0.93, B_infl 0.85, B_dist 0.84, B_exp 0.86, B_dem 0.82, B_fin 0.96.

G1 is drawn from infl (10) among its top-10 correlates; aligned positively with infl 6m rate (4), infl 12m rate (4), infl short-horizon rate (1m/3m) (2); e.g. cpi_trim_6m, pce_trim_6m, cpi_trim_3m; inverted: none. Reading: the common inflation level, dominated by trimmed, core and headline rates at 3 to 12 months; the state the underlying-inflation measures try to track.

G2 is drawn from dem (5), fin (3), infl (2) among its top-10 correlates; aligned positively with dem activity (5), infl short-horizon rate (1m/3m) (1), infl 6m rate (1), fin asset prices (1); e.g. ip_12m, ip_6m, real_inv_yoy; inverted: fin credit supply (1), fin risk pricing (1); e.g. sloos_ci, ebp. Reading: activity and investment growth with short-horizon inflation, against tight lending standards and wide spreads; a demand-pressure state.

- B_infl loads on: cpi_core_flex_6m (-0.29), cpi_core_flex_3m (-0.28), cpi_core_flex_12m (-0.26)
- B_dist loads on: xs_sd_12m (+0.29), xs_sd_6m (+0.27), xs_sd_3m (+0.25)
- B_exp loads on: spf_cpi_10y (-0.45), spf_cpi_4q_sd (+0.44), clev_10y (-0.44)
- B_dem loads on: payrolls_12m (+0.33), gdp_yoy (+0.31), real_pce_12m (+0.30)
- B_fin loads on: real_10y_clev (+0.35), dgs10 (+0.35), term_premium_10y (+0.34)

![Global and block-specific factors.](figures/factors.png)
*Global and block-specific factors.*


## 3. Forecasting core PCE

Core PCE is the target. The dependent variables are future annualized core PCE inflation over 3, 6, 12 and 24 months, its change relative to today's 12-month rate, and an indicator for deceleration. Three nested direct regressions are compared: M1 uses inflation history and momentum only (12m rate, its 12-month lag, 3m and 6m rates, the 3-month change in the 12m rate, acceleration); M2 adds the two global factors; M3 adds the five block factors.

Forecasts are evaluated pseudo-out-of-sample with an expanding window, its change relative to today's 12m rate, and the deceleration indicator. Direct regressions with three nested information sets: M1 inflation history and momentum, M2 plus the global factors, M3 plus the block factors. Expanding-window pseudo-out-of-sample from 2000 with full-sample factor loadings (a look-ahead in the factor construction).

*Out-of-sample RMSFE, RMSFE relative to M1, and directional accuracy for acceleration/deceleration, by horizon (months)*

| model | RMSFE 3 | RMSFE 6 | RMSFE 12 | rel_RMSFE 3 | rel_RMSFE 6 | rel_RMSFE 12 | dir_acc 3 | dir_acc 6 | dir_acc 12 |
|---|---|---|---|---|---|---|---|---|---|
| M1 history | 0.94 | 0.81 | 0.84 | 1.00 | 1.00 | 1.00 | 0.57 | 0.58 | 0.64 |
| M2 +global | 0.97 | 0.85 | 0.86 | 1.03 | 1.04 | 1.02 | 0.55 | 0.56 | 0.60 |
| M3 +global+block | 0.99 | 0.87 | 0.91 | 1.05 | 1.07 | 1.09 | 0.56 | 0.56 | 0.61 |

*In-sample factor coefficients (HAC t-statistics, lag = horizon) in the M3 regression*

|  | 3m | 6m | 12m |
|---|---|---|---|
| G1 | -0.03 (-0.8) | -0.04 (-1.1) | -0.05 (-1.5) |
| G2 | +0.04 (+1.7) | +0.03 (+1.5) | +0.02 (+0.7) |
| B_infl | -0.14 (-4.0) | -0.16 (-4.9) | -0.16 (-3.9) |
| B_dist | +0.05 (+1.6) | +0.05 (+1.8) | +0.07 (+2.5) |
| B_exp | -0.02 (-0.3) | -0.02 (-0.3) | -0.04 (-0.5) |
| B_dem | +0.03 (+0.6) | +0.05 (+1.2) | +0.05 (+0.9) |
| B_fin | +0.02 (+0.3) | +0.02 (+0.3) | +0.02 (+0.3) |
| R2 M3 / M1 | 0.58 / 0.55 | 0.67 / 0.62 | 0.66 / 0.60 |


## 4. What the model says today

*Forecast origin July 2026; annualized percent; band from the out-of-sample RMSFE*

|  | 3m | 6m | 12m |
|---|---|---|---|
| current 12m core PCE | 3.289442706823209 | 3.289442706823209 | 3.289442706823209 |
| current h-month core PCE | 3.0022534820087543 | 3.4009147883450552 | 3.289442706823209 |
| forecast M3 | 3.1702092797229766 | 3.1520108259111677 | 3.0960768370066134 |
| forecast M1 history | 3.1839559168582685 | 3.1246702462890807 | 3.033274924455645 |
| forecast change vs 12m | -0.11923342710023244 | -0.1374318809120414 | -0.19336586981659565 |
| direction | decelerating | decelerating | decelerating |
| 90% band | [1.5, 4.8] | [1.7, 4.6] | [1.6, 4.6] |


## 5. Current-signal and news decompositions


### Current-signal decomposition

For the linear M3 equation each contribution is the coefficient times the current value's deviation from its sample mean, so contributions sum to the forecast's deviation from the target's mean. This says which signals, at their current values, push the forecast away from its mean; it is not a news decomposition.

![Current-signal decomposition of the core PCE forecast.](figures/decomposition.png)
*Current-signal decomposition of the core PCE forecast.*

*Contributions (pp)*

|  | 3m | 6m | 12m |
|---|---|---|---|
| sample mean of target | 2.35 | 2.34 | 2.33 |
| history | 0.97 | 0.99 | 1.00 |
| G1 | -0.00 | -0.01 | -0.01 |
| G2 | 0.03 | 0.03 | 0.01 |
| inflation | -0.13 | -0.14 | -0.14 |
| distribution | -0.00 | -0.00 | -0.00 |
| expectations | -0.05 | -0.04 | -0.08 |
| demand | -0.02 | -0.04 | -0.04 |
| financial | 0.01 | 0.02 | 0.02 |
| forecast | 3.16 | 3.14 | 3.08 |


### News decomposition

The factor system in state-space form (loadings from the PCA, VAR(1) dynamics, diagonal idiosyncratic variances), filtered month by month through the ragged edge (Sep 2026). News in each released series is its surprise relative to the previous month's information set; the revision of the factor-only 12m forecast is attributed through the Kalman gain. Latest-vintage values, so data revisions are ignored and publication lags enter only at the ragged edge. Filtered factors track the PCA factors (correlations G1 1.00, G2 0.97, B_infl 0.96, B_dist 0.98, B_exp 0.97, B_dem 0.97, B_fin 0.96). Sep 2026 revision +0.08 pp (exp +0.10, fin -0.01); cumulative over 12 months +0.14 pp; largest monthly revision Jun 2026 (0.57).

![News decomposition of forecast revisions.](figures/news.png)
*News decomposition of forecast revisions.*


## 6. Agreement and disagreement

Do today's indicators agree about inflation more or less than they usually do? Four complementary measures are used.

A: cross-sectional SD of the seven standardized factors. B: residual RMS after fitting one common factor to the seven signals (it explains 46% of their variance): how poorly can today's signals be reconciled by one common state? C: SD across the eleven alternative inflation measures (pp). D: breadth versus dispersion within the distribution block.

*Disagreement measures, current value and history*

|  | current | percentile | median | p90 |
|---|---|---|---|---|
| D_sd (A) | 0.56 | 19.84 | 0.80 | 1.56 |
| D_res (B) | 0.57 | 46.49 | 0.59 | 0.99 |
| D_infl_12m (C) | 0.90 | 53.46 | 0.84 | 2.15 |
| D_infl_3m (C) | 1.27 | 41.95 | 1.39 | 3.25 |

![Cross-block disagreement and the current residual by signal.](figures/disagreement.png)
*Cross-block disagreement and the current residual by signal.*

![Disagreement among inflation measures, and breadth versus dispersion.](figures/disagreement_inflation.png)
*Disagreement among inflation measures, and breadth versus dispersion.*


## 7. Historical analogs

When in the past did the configuration of inflation signals look most like today?

Nearest neighbors of today's standardized factor vector (Euclidean distance, excluding the last 24 months, at most one match per six-month window). Across the 15 analogs the median subsequent 12m core PCE is 1.68 (median change -0.03 pp, decelerating in 53%). Matching on the pattern of disagreement instead gives 2006-09, 2004-04, 2006-03, 2003-09, 2007-07 (median change -0.03). Not causal.

*Analogs on the factor vector, origin Jul 2026*

|  | distance | core PCE 12m then | next 3m | next 6m | next 12m | change 12m ahead | D_res then |
|---|---|---|---|---|---|---|---|
| 2006-08 | 0.96 | 2.64 | 1.54 | 2.28 | 1.97 | -0.67 | 0.46 |
| 2004-04 | 1.00 | 1.99 | 1.65 | 1.71 | 2.09 | 0.09 | 0.55 |
| 2003-09 | 1.03 | 1.45 | 1.78 | 2.06 | 1.93 | 0.48 | 0.45 |
| 2007-07 | 1.14 | 2.02 | 2.73 | 2.55 | 2.22 | 0.20 | 0.32 |
| 2005-01 | 1.21 | 2.15 | 2.11 | 1.90 | 2.12 | -0.03 | 0.42 |
| 2006-02 | 1.23 | 2.12 | 3.32 | 2.77 | 2.52 | 0.41 | 0.44 |
| 2014-01 | 1.48 | 1.44 | 1.47 | 1.64 | 1.20 | -0.24 | 0.55 |
| 2005-07 | 1.52 | 2.09 | 2.36 | 2.34 | 2.51 | 0.42 | 0.35 |
| 2014-07 | 1.53 | 1.60 | 1.03 | 0.76 | 1.17 | -0.43 | 0.57 |
| 2018-05 | 1.65 | 1.96 | 0.93 | 1.52 | 1.55 | -0.41 | 0.51 |
| 2019-03 | 1.78 | 1.60 | 1.94 | 1.58 | 1.52 | -0.09 | 0.42 |
| 2013-01 | 1.85 | 1.58 | 1.00 | 1.33 | 1.44 | -0.14 | 0.66 |
| 2017-01 | 1.88 | 1.85 | 1.36 | 1.25 | 1.62 | -0.23 | 0.50 |
| 2013-07 | 1.93 | 1.48 | 1.58 | 1.55 | 1.60 | 0.12 | 0.78 |
| 2020-01 | 1.96 | 1.58 | -0.82 | 0.82 | 1.68 | 0.10 | 0.49 |


## 8. Supply-like versus demand-like episodes and disagreement

Hypothesis: disagreement between inflation indicators and demand or financial indicators may be especially common when inflation is driven by supply or relative-price shocks rather than aggregate demand. This section is descriptive: episodes are classified by inflation and demand, disagreement is compared across them, and its correlates and predictive content are tested.

Regimes from core PCE 12m and the demand block's first PC, each above or below its median. Current regime: adverse-supply-like (infl high, demand weak). Descriptive only; a sign-restricted VAR or external instruments would be the structural extension.

*Disagreement by regime*

|  | months | D_res mean | D_res median | share D_res > p75 | next-12m change, median |
|---|---|---|---|---|---|
| adverse-supply-like (infl high, demand weak) | 105 | 0.59 | 0.54 | 0.27 | -0.43 |
| demand-like (infl high, demand high) | 144 | 0.70 | 0.60 | 0.28 | -0.23 |
| favorable-supply-like (infl low, demand strong) | 106 | 0.56 | 0.55 | 0.09 | -0.01 |
| weak-demand (infl low, demand weak) | 144 | 0.73 | 0.65 | 0.32 | 0.04 |

*Contemporaneous correlates of disagreement (standardized regressors, HAC t)*

|  | corr | t (HAC) |
|---|---|---|
| headline_core_gap | -0.11 | -0.67 |
| flex_less_sticky | -0.01 | -0.06 |
| xs_sd_3m | 0.62 | 5.85 |
| oil_12m | -0.20 | -1.14 |
| abs_oil_12m | 0.49 | 4.16 |

*Subsequent change in core PCE on disagreement, current inflation, and the demand factor (HAC t)*

|  | 3m | 6m | 12m |
|---|---|---|---|
| beta D_res (pp per sd) | 0.06 | 0.07 | 0.11 |
| t | 0.95 | 1.34 | 1.87 |
| gamma pi12 | -0.18 | -0.21 | -0.29 |
| t  | -3.28 | -3.43 | -3.91 |
| delta B_dem | -0.06 | -0.05 | -0.05 |
| t   | -1.88 | -1.33 | -0.97 |
| R2 | 0.08 | 0.12 | 0.20 |


## 9. Additional evidence

Four further pieces of evidence feed the answers in the next section: the probability that inflation will be lower over each horizon, a horse race of individual statistics as additions to core PCE 12m, the history of inflation conditional on breadth, and an event study of episodes in which the 3-month rate fell well below the 12-month rate.

*Probability that core PCE inflation is lower over the next h months than the current 12m rate*

|  | 3m | 6m | 12m |
|---|---|---|---|
| P(lower) normal approx. | 0.55 | 0.56 | 0.58 |
| P(lower) logit | 0.65 | 0.69 | 0.69 |
| unconditional | 0.51 | 0.57 | 0.57 |

*Horse race: each statistic added to core PCE 12m; relative RMSFE < 1 beats core PCE 12m alone*

| measure | rel RMSFE 3m | rel RMSFE 6m | rel RMSFE 12m | corr with core PCE 12m | type |
|---|---|---|---|---|---|
| core PCE 3m | 1.00 | 0.99 | 0.99 | 0.85 | contemporaneous |
| core PCE 6m | 0.98 | 0.97 | 0.99 | 0.95 | contemporaneous |
| core PCE 3m-12m | 1.00 | 0.99 | 0.99 | -0.01 | no gain |
| core CPI 12m | 1.00 | 1.01 | 1.01 | 0.94 | contemporaneous |
| median CPI 12m | 1.00 | 1.01 | 1.02 | 0.81 | contemporaneous |
| median CPI 3m | 1.01 | 1.01 | 1.00 | 0.83 | contemporaneous |
| trimmed PCE 12m | 1.02 | 1.05 | 1.08 | 0.91 | contemporaneous |
| trimmed CPI 12m | 1.01 | 1.01 | 1.00 | 0.91 | contemporaneous |
| sticky CPI 12m | 0.99 | 1.00 | 1.01 | 0.86 | contemporaneous |
| flexible CPI 12m | 1.01 | 1.03 | 1.03 | 0.49 | no gain |
| breadth >3% (3m) | 1.01 | 1.01 | 1.02 | 0.72 | no gain |
| breadth >3% (12m) | 1.02 | 1.03 | 1.04 | 0.79 | no gain |
| xs dispersion (3m) | 1.01 | 1.01 | 1.00 | -0.01 | no gain |
| xs median (3m) | 1.01 | 1.01 | 1.02 | 0.75 | no gain |
| SPF dispersion | 1.04 | 1.07 | 1.07 | 0.36 | no gain |
| Michigan 1y | 1.01 | 1.03 | 1.03 | 0.60 | no gain |

*Conditional history by breadth (share of categories above 3% at 12m)*

|  | high breadth (top quartile) | low breadth (bottom quartile) | all |
|---|---|---|---|
| months | 117.00 | 122.00 | 499.00 |
| core PCE 12m then | 3.64 | 1.57 | 2.37 |
| core PCE next 12m | 3.27 | 1.76 | 2.33 |
| P(next 12m > 2.5%) | 0.79 | 0.11 | 0.33 |
| mean change | -0.37 | 0.19 | -0.02 |
| P(decelerate) | 0.69 | 0.52 | 0.56 |

*Spells with core PCE 3m at least 1 pp below 12m*

| date | core 12m | gap | 12m change ahead | turning point | reaccelerated within 6m |
|---|---|---|---|---|---|
| 1985-11 | 4.01 | -1.56 | -0.72 | True | True |
| 1989-08 | 3.87 | -1.22 | 0.39 | False | True |
| 1990-12 | 3.95 | -1.56 | -0.53 | True | False |
| 1997-08 | 1.70 | -1.00 | -0.28 | False | False |
| 2001-09 | 1.21 | -2.26 | 1.20 | False | True |
| 2008-10 | 1.62 | -1.29 | -0.39 | False | False |
| 2020-04 | 0.99 | -1.81 | 2.09 | False | True |
| 2023-07 | 4.21 | -1.45 | -1.44 | True | False |


## 10. Answers


### 1. Best estimate of underlying inflation today

- Core PCE 3.0 / 3.4 / 3.3 (3m/6m/12m); median CPI 2.7, trimmed PCE 2.3, sticky 2.8, flexible 4.7 (12m).
- Common signal across the 11 12m measures (median): 2.7. Above it by more than 0.25: cpi_12m, pce_12m, pce_core_12m, cpi_flex_12m; below: pce_trim_12m, cpi_core_flex_12m.
- Disagreement among measures at the 53rd percentile (12m) and 42nd (3m): not unusual.


### 2. Accelerating or decelerating

- 10 of 11 measures have 3m below 12m; core PCE 3m-12m gap -0.3 pp, 6m-12m +0.1.
- Factor model: 3.2 / 3.2 / 3.1 over 3/6/12m against a 12m rate of 3.3: decelerating (-0.19 pp at 12m).
- P(lower over 3/6/12m): normal approximation 55% / 56% / 58%; logit 65% / 69% / 69% (unconditional about 57%).


### 3. Breadth

- Share of categories above 2/3/4/5%: 52 / 45 / 15 / 9% at 3m; 76 / 56 / 35 / 18% at 12m.
- Breadth (above 3%) is falling over three months at 3m (-18 pp) and rising over a year at 12m (+13 pp).
- Historical position: breadth 45th percentile (3m), 65th (12m); cross-sectional SD 52nd; upper-tail share 13th.
- Reading: broad-based at 12m; at 3m the rise is not unusually concentrated.


### 4. Does breadth predict future inflation

- High-breadth months (top quartile): core PCE averaged 3.3% over the next 12m and stayed above 2.5% in 79% of cases, against 1.8% and 11% for low breadth. Inflation stayed elevated, but it was already high.
- Given core PCE 12m and 3m, breadth (3m) has HAC t = +1.0 / +0.7 / +0.7 for the 3/6/12m change and relative RMSFE 1.01 / 1.01 / 1.02: little incremental content. Breadth at 12m: t -0.0, rel RMSFE 1.04.
- Against median CPI (rel RMSFE 12m 1.02) and trimmed PCE (1.08), breadth is not more useful. In the factor regression the distribution block is the one block with a significant coefficient (+0.07 (+2.5) at 12m).


### 5. Most useful current statistics

- Best single addition to core PCE 12m by horizon: 3m core PCE 6m (0.98); 6m core PCE 6m (0.97); 12m core PCE 6m (0.99). Gains are small everywhere.
- Forward-looking (beats core PCE 12m alone at two or more horizons): none. Contemporaneous summaries (|corr| > 0.8, no out-of-sample gain): core PCE 3m, core PCE 6m, core CPI 12m, median CPI 12m, median CPI 3m, trimmed PCE 12m, trimmed CPI 12m, sticky CPI 12m.


### 6. Recent favorable readings: signal or noise

- Spells with core PCE 3m at least 1 pp below 12m: 8 since 1985; a genuine turning point (12m rate down at least 0.5 pp a year later) in 38%, reacceleration within six months in 50%.
- Today's gap is -0.29 pp (below the event threshold). The factor-space analogs saw a median 12m change of -0.03 pp with deceleration in 53% of cases: closer to a soft patch than a sustained disinflation.


### 7. Are financial conditions restrictive

- Financial factor (+ = looser) +0.34 z, 62nd percentile: near its historical middle.
- 83% of 12 indicators sit on the loose side of their median: loose = fedfunds, dgs10, nfci, vix, baa_spread, ebp, equity_12m_ret, usd_12m, mortgage30, sloos_ci; tight = real_10y_clev, term_premium_10y.
- Predictive content given inflation history: +0.02 (+0.3) / +0.02 (+0.3) / +0.02 (+0.3) at 3/6/12m (coefficient, HAC t); contribution to today's 12m forecast +0.02 pp.


### 8. Is demand pressure still inflationary

- Demand factor -0.44 z (24th percentile); G2 +0.21. Predictive content given history: +0.03 (+0.6) / +0.05 (+1.2) / +0.05 (+0.9); contribution to the 12m forecast -0.04 pp.
- Drivers today (loading x z): sentiment -0.64, claims_log +0.41, unrate +0.28, capu -0.18, comp_12m -0.16. Unemployment 4.1 (18th pct), V/U 1.05, wages 3.2%, real PCE 6m 3.0%.


### 9. Are expectations a problem

- Levels: Michigan 1y 4.2 (79th pct), SPF 4q 2.3 (48th), 5y breakeven 2.37 (75th), 5y5y 2.33 (55th), SPF 10y 2.3.
- Disagreement: SPF cross-sectional SD 0.94 (95th pct); households minus professionals +1.9 pp (96th).
- Predictive content: expectations block given history -0.04 (-0.5) at 12m; SPF dispersion as a single addition, rel RMSFE 1.07 (t +1.5); Michigan 1y 1.03 (t -0.1). Contribution to the 12m forecast -0.08 pp; the block is the most inflationary residual in the disagreement decomposition (+1.17).


### 10. What drives the current forecast

- 12m forecast 3.1: history +1.00, all factors together -0.25 (table in section 5).
- Pushing up: history +1.00, G2 +0.01, financial +0.02; pushing down: inflation -0.14, expectations -0.08, demand -0.04.


### 11. Agreement or disagreement

- Cross-block disagreement 0.57, 46th percentile (SD across factors 20th). Outliers: B_exp +1.17, B_infl +0.69, B_fin +0.52.
- Within inflation measures 53rd percentile; between price and non-price blocks 46th: similar within and between; overall not historically unusual.


### 12. Historical analogs

- Closest configurations: 2006-08, 2004-04, 2003-09, 2007-07, 2005-01, 2006-02.
- Subsequent 3/6/12m core PCE (median) 1.6 / 1.6 / 1.7; 12m change median -0.03. Outcomes: sustained disinflation 7%, reacceleration 0%, mixed 93%.


### 13. Disagreement and supply-versus-demand

- Mean disagreement by regime: adverse-supply-like 0.59, demand-like 0.70, favorable-supply-like 0.56, weak-demand 0.73: not higher in supply-like than in demand-led episodes.
- Correlates: cross-sectional dispersion +0.62 (t +5.9), |oil shock| +0.49, flexible minus sticky -0.01, headline-core gap -0.11.
- Given current inflation and demand, a 1-sd rise in disagreement changes the subsequent 12m inflation change by +0.11 pp (t +1.9): no faster mean reversion. Descriptive, not structural.


### 14. Implications for the Fed debate

- Projected core PCE stays above 2% at all horizons (3.2 / 3.2 / 3.1); projected change -0.19 pp over 12m (history-only model -0.26).
- Evidence for deceleration: 10/11 measures decelerating, P(lower in 12m) 58%, analogs decelerating 53%: moderate.
- Uncertainty: 90% band [1.6, 4.6]; block disagreement at the 46th percentile.
- Risks implied by the outputs: persistence high (forecast level); reacceleration elevated (expectations residual +1.17, historical reacceleration frequency 50%); premature tightening notable (demand factor at the 24th percentile).


### 15. Warsh, Waller, Kashkari

- Warsh (inflation broad, policy not restrictive): breadth at 12m at the 65th percentile (56% above 3%) and financial conditions at the 62nd percentile on the loose side, so both legs of the argument find support; demand at the 24th percentile does not.
- Waller (underlying inflation declining): 10/11 measures show 3m below 12m; the model projects -0.19 pp over 12m with P(lower) 58%, so the momentum is only partly confirmed; comparable gaps were turning points 38% of the time.
- Kashkari (entrenchment from waiting): the 12m forecast stays at 3.1%, the expectations block is the most inflationary residual (+1.17) with households +1.9 pp above professionals, and analogs reaccelerated in 0% of cases: supports the concern on level and expectations, less so on historical reacceleration.

Caveat: latest-vintage data and full-sample factor loadings; the news decomposition is pseudo-real-time (no data revisions; publication lags only at the ragged edge). Rule-based wording thresholds are in the answers section of run.py.
