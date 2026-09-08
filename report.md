
# US inflation signals: agreement, disagreement, and forecasting

**Summary**

- Core PCE runs at 3.3 percent over 12 months and 3.0 percent annualized over 3 months.
- We collect data across five blocks: inflation measures, inflation distribution measures, inflation expectations measures, demand-side measures, and financial-side measures.
- The dynamic factor model that leverages data across all five blocks projects 12-month core PCE inflation of 3.3 / 2.9 / 2.4 / 2.4 percent at 3/6/12/24 months ahead, that is, a deceleration of 0.9 pp over the 12 months, and inflation is not expected to return to target over the near term.
- The first common factor in each of the five blocks is near its historical average, so while we don't see evidence of overheating, we also don't see evidence of current conditions being significantly restrictive.
- Across the second principal components, we see secondary evidence of a higher-than-average wedge between household and professional inflation expectations, a tighter-than-average labor market, and signs of lower-than-usual financial stress.


## Introduction

We ask what current inflation-related indicators imply for future US inflation, how much the indicators agree or disagree with one another, and what they say about the distribution of today's shocks relative to historical episodes.

This is motivated by the current debate around the Fed's September meeting, in which policymakers emphasize different statistics: recent inflation momentum, median and trimmed measures, the breadth of price increases, expectations, labor-market conditions, demand, and financial conditions.

All of these are potentially useful signals for future inflation. Our analysis takes the following steps. Indicators are organized into five blocks and each block is first examined on its own. Then we combine information across all five blocks to forecast core PCE inflation 3, 6, 12, and 24 months ahead, and this current forecast is decomposed into contributions from different sources of news. Finally, we investigate the degree of disagreement across signals, and look toward what this implies for today's configuration of shocks.


## 1. The five blocks


### Block 1: inflation measures

*Block 1 indicators*

| shorthand | indicator | source | transformation |
|---|---|---|---|
| cpi_{1,3,6,12}m | CPI, all items | BLS via FRED | annualized 1/3/6/12-month log change of the index |
| cpi_core_{1,3,6,12}m | CPI ex food and energy | BLS via FRED | annualized 1/3/6/12-month log change of the index |
| pce_{1,3,6,12}m | PCE price index | BEA via FRED | annualized 1/3/6/12-month log change of the index |
| pce_core_{1,3,6,12,24}m | PCE ex food and energy | BEA via FRED | annualized 1/3/6/12/24-month log change of the index |
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

PC1 is the general inflation factor, comoving positively with all inflation measures and correlating most strongly with recent core and trimmed-mean measures. It currently sits close to its historical average.

PC2 captures momentum, loading positively on 3m measures and negatively on 12m measures, so it turns negative when inflation is decelerating. It rose with the Iran war and has since returned to average, without yet turning negative.


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

PC1 is the breadth factor, comoving positively with the share of categories rising quickly and with median category inflation, and correlating most strongly with the 6-month measures. Breadth spiked to +1.5 standard deviations three months ago and has since returned to average.

PC2 separates wide two-sided dispersion from right-tailed concentration, loading positively on the interquartile range and negatively on skewness and the upper-tail share, so it turns negative when a few categories are accelerating rather than the whole distribution shifting. It ran close to -1.5 through the middle of the year, possibly reflecting energy and tariff-related passthrough, and has since returned to average.


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

PC1 is the level of expected inflation, comoving positively with every source and correlating most strongly with the Cleveland Fed measures and the SPF one-year forecast. It currently sits close to its historical average.

PC2 is the wedge between near-term disagreement and long-run expectations, loading positively on forecaster dispersion and household expectations and negatively on the 10-year measures, so it turns positive when households and near-term forecasters run ahead of the long-run view. It sits modestly above average, having partially unwound its spike earlier in the year.


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

PC1 is the standard business-cycle factor, comoving positively with output, employment and real spending growth, and correlating most strongly with year-on-year GDP and compensation growth. Activity sits a little below its historical average.

PC2 is the wage-pressure factor, loading positively on wage growth, the vacancy-unemployment ratio and quits and negatively on unemployment, so it turns positive when the labor market is tight relative to activity. It remains above average, though it has drifted down steadily over the year.


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

PC1 is the common factor of interest rates, inverted so that positive implies looser financial conditions, and correlating most strongly with the mortgage rate, the 10-year real rate and the 10-year Treasury yield. Rates sit at about their historical average.

PC2 is the risk-pricing dimension, loading positively on credit spreads, the excess bond premium, the VIX and the NFCI, so it turns positive when financial stress is elevated. It sits well below average: risk pricing is unusually benign.


## 2. A dynamic factor model of the panel

We next combine the five blocks in a dynamic factor model, X = Lambda_G G + lambda_B B + e, allowing two global factors common to the whole panel and one factor specific to each block, with the seven evolving as a joint VAR(1) and each series carrying an AR(1) idiosyncratic component. We estimate it by expectation-maximization, so the Kalman smoother handles missing observations and the ragged edge directly and no imputation step is needed. Signs are normalized so that every factor is positively related to inflation.

The panel has 141 variables from 1985-01 to 2026-07. EM converged in 84 iterations. Averaged over the series in each block, the two global factors account for dem 17%, dist 44%, exp 26%, fin 23%, infl 74% of the variance, and all seven factors together for dem 48%, dist 55%, exp 33%, fin 30%, infl 77%. Every factor is oriented so that higher = more inflationary pressure (financial: looser) and scaled to unit standard deviation. First-order autocorrelation: G1 0.98, G2 0.97, B_infl 0.78, B_dist 0.96, B_exp 0.99, B_dem 0.94, B_fin 0.99; the largest eigenvalue of the factor VAR is 0.99, so the system is stationary.

G1 is the common inflation level: it loads most heavily on the SPF one-year forecast and on trimmed-mean CPI and PCE at 3 and 6 months, and accounts for roughly three quarters of the variance of the average inflation series. G2 is a relative-price state rather than a demand state: it loads on flexible-price CPI, the upper-tail share of the category distribution and commodity PPI, so it rises when a narrow set of volatile prices moves rather than the whole distribution.

The block factors are what remains in each block once the two global states are accounted for:

- B_infl: 1-month core and flexible-price deviations, inverted and weakly loaded; it lifts the share of inflation-block variance explained from 74 to 77 percent, so it adds little the global states do not already carry.
- B_dist: dispersion across categories, loading on the cross-sectional standard deviation and the 90-10 spread.
- B_exp: near-term disagreement against long-run anchoring, positive on SPF dispersion and negative on the Cleveland and SPF 10-year expectations.
- B_dem: the business cycle, loading on year-on-year GDP, real consumption and industrial production. It is not a labor-market tightness factor: wages and the vacancy-unemployment ratio load on the second principal component of the block, which the model does not carry.
- B_fin: the level of interest rates, inverted, loading on the 10-year real rate, the 10-year yield and the term premium.

![Global and block-specific factors.](figures/factors.png)
*Global and block-specific factors.*


### Forecasts

Core PCE is running at 3.3 percent over 12 months and 3.0 annualized over the latest 3 months. The model's forecast of the next eight quarters, annualized, is 2.49, 2.33, 2.30, 2.32, 2.35, 2.37, 2.39, 2.41. Combined with the months already realized, the 12-month rate is projected at 3.3 / 2.9 / 2.4 / 2.4 percent 3/6/12/24 months from now. Within a year the window still contains realized months, so the near-term path is largely arithmetic: the quarters ending January and April 2026 ran at 3.8 and 3.8 annualized, and the 12-month rate falls as they roll out.

*Projected 12-month core PCE inflation at each horizon, origin July 2026 (percent)*

|  | 3m | 6m | 12m | 24m |
|---|---|---|---|---|
| forecast | 3.27 | 2.91 | 2.36 | 2.38 |
| change vs current 12m | -0.02 | -0.38 | -0.93 | -0.91 |
| realized months in window | 9 | 6 | 0 | 0 |

![Implied 12-month core PCE inflation every three months, to 24 months ahead. Windows ending within a year of the origin still contain realized quarters.](figures/forecast.png)
*Implied 12-month core PCE inflation every three months, to 24 months ahead. Windows ending within a year of the origin still contain realized quarters.*


### Sources of news in the current projection

![Monthly news contributions to the current 12-month-ahead forecast, by block.](figures/news.png)
*Monthly news contributions to the current 12-month-ahead forecast, by block.*

Holding the target date fixed at July 2027, each month's data releases revise the 12-month forecast. Over the last 12 months the cumulative revision is +0.30 pp: dem -0.12, exp +0.06, fin +0.08, dist +0.08, infl +0.20. News is measured against the previous month's information set with the parameters held fixed.


### Information sets

How much of the projection depends on the breadth of the panel? Three nested information sets, all iterated: M1 an AR(12) on monthly core PCE chosen by AIC; M2 the two global factors; M3 the global and block factors. M2 and M3 are separately estimated dynamic factor models, since the parameters of a restricted set cannot be read off the full fit. Forecasts are recursive from 2000: at each origin the filtered state uses data through that month only, but the parameters are estimated once on the full sample, which is a look-ahead that favours the factor models. Latest-vintage data throughout, so revisions are ignored.

*Projected 12-month core PCE inflation by information set, origin July 2026 (percent)*

|  | 3m | 6m | 12m | 24m |
|---|---|---|---|---|
| M1 time series | 3.48 | 3.31 | 3.12 | 2.85 |
| M2 global factors | 3.34 | 3.06 | 2.72 | 2.73 |
| M3 global + block | 3.27 | 2.91 | 2.36 | 2.38 |

*Pseudo-out-of-sample RMSE of the 12-month rate h months ahead, 2000 onward, 316 origins at 3m; forecasts accumulated from the 3-month rate. Within a year the window contains realized months, so errors are mechanically smaller at short horizons*

| model | RMSE 3m | RMSE 6m | RMSE 12m | RMSE 24m | relative to M1 3m | relative to M1 6m | relative to M1 12m | relative to M1 24m |
|---|---|---|---|---|---|---|---|---|
| M1 time series | 0.22 | 0.37 | 0.73 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 |
| M2 global factors | 0.24 | 0.43 | 0.89 | 1.19 | 1.10 | 1.16 | 1.22 | 1.22 |
| M3 global + block | 0.24 | 0.42 | 0.83 | 1.12 | 1.10 | 1.13 | 1.14 | 1.15 |

*The same evaluation reading each h-month rate off its own series instead of accumulating; the gap is the cost of ignoring the accounting identity*

| model | 3m | 6m | 12m | 24m |
|---|---|---|---|---|
| M1 time series | 0.22 | 0.37 | 0.73 | 0.97 |
| M2 global factors | 0.24 | 0.41 | 0.82 | 1.14 |
| M3 global + block | 0.24 | 0.40 | 0.79 | 1.12 |

![Implied 12-month core PCE inflation under each information set. Paths coincide over the first quarter, where nine of twelve months are realized, and diverge as the forecast share of the window grows.](figures/forecast_sets.png)
*Implied 12-month core PCE inflation under each information set. Paths coincide over the first quarter, where nine of twelve months are realized, and diverge as the forecast share of the window grows.*


## 3. Agreement and disagreement

Do today's indicators agree about inflation more or less than they usually do? Four complementary measures are used.

The five block factors share one common state that explains 60 percent of their joint variance. Its correlation with each block is infl +0.92, dist +0.84, exp +0.90, dem +0.46, fin -0.64: the blocks do not all move together. The common state stands at +0.01 standard deviations (48th percentile). Relative to what it implies, no block is unusually strong; none unusually weak. Disagreement, the root mean square of these residuals, is 0.11, the 0th percentile of its history.

*Block factors, July 2026: level, what the common state implies, and the residual*

|  | correlation with common state | current level (z) | implied by common state | residual (z) |
|---|---|---|---|---|
| infl | 0.92 | -0.03 | 0.01 | -0.04 |
| dist | 0.84 | -0.01 | 0.01 | -0.02 |
| exp | 0.90 | 0.19 | 0.01 | 0.18 |
| dem | 0.46 | -0.15 | 0.00 | -0.15 |
| fin | -0.64 | 0.07 | -0.01 | 0.08 |

*Disagreement measures, current value and history*

|  | current | percentile | median | p90 |
|---|---|---|---|---|
| D_res: residual RMS | 0.11 | 0.40 | 0.46 | 0.81 |
| D_sd: SD across blocks | 0.13 | 0.20 | 0.81 | 1.29 |
| D_infl_12m: SD across 12m measures | 0.90 | 53.46 | 0.84 | 2.15 |
| D_infl_3m: SD across 3m measures | 1.27 | 41.95 | 1.39 | 3.25 |

![Common state across the block factors, and the current residual by block.](figures/disagreement.png)
*Common state across the block factors, and the current residual by block.*

![Disagreement among inflation measures, and breadth versus dispersion.](figures/disagreement_inflation.png)
*Disagreement among inflation measures, and breadth versus dispersion.*


## 4. Historical analogs

When in the past did the configuration of inflation signals look most like today?

Cosine similarity between today's vector of five block factors (infl -0.0, dist -0.0, exp +0.2, dem -0.1, fin +0.1) and every past month, excluding the last 24 months and keeping at most one match per six-month window. The closest profiles are 1993-08, 2011-04, 2005-10, 1991-10, 1996-01 (cosine 0.83, 0.74, 0.69, 0.66, 0.63). Across the 15 analogs the median subsequent 12m core PCE is 2.06 (median change -0.02 pp, decelerating in 53%). Matching on the pattern of residuals instead, which asks when the blocks last disagreed in the same way, gives 1993-05, 2006-07, 2005-10, 1991-11, 2011-04 (median change -0.28). Not causal.

![Cosine similarity of the historical block-factor profile to today's.](figures/analogs.png)
*Cosine similarity of the historical block-factor profile to today's.*

*Analogs by cosine similarity of the block-factor profile, origin Jul 2026*

|  | cosine | magnitude ratio | core PCE 12m then | next 3m | next 6m | next 12m | change 12m ahead | D_res then |
|---|---|---|---|---|---|---|---|---|
| 1993-08 | 0.83 | 3.43 | 2.77 | 2.29 | 1.82 | 2.17 | -0.60 | 0.38 |
| 2011-04 | 0.74 | 5.88 | 1.39 | 1.98 | 1.62 | 1.95 | 0.56 | 0.65 |
| 2005-10 | 0.69 | 4.32 | 2.24 | 2.33 | 2.65 | 2.47 | 0.23 | 0.37 |
| 1991-10 | 0.66 | 7.14 | 3.25 | 2.82 | 3.11 | 2.79 | -0.47 | 0.63 |
| 1996-01 | 0.63 | 1.27 | 1.99 | 1.99 | 1.87 | 1.84 | -0.15 | 0.13 |
| 2008-05 | 0.62 | 6.77 | 2.13 | 2.13 | 0.90 | 0.82 | -1.31 | 0.68 |
| 1992-09 | 0.55 | 4.00 | 2.62 | 3.15 | 2.97 | 2.75 | 0.13 | 0.39 |
| 2006-08 | 0.53 | 4.08 | 2.64 | 1.54 | 2.28 | 1.97 | -0.67 | 0.25 |
| 2007-06 | 0.52 | 3.58 | 1.97 | 2.29 | 2.46 | 2.19 | 0.22 | 0.31 |
| 1995-05 | 0.51 | 4.94 | 2.21 | 1.94 | 1.85 | 1.85 | -0.36 | 0.48 |
| 2004-06 | 0.47 | 2.70 | 2.09 | 1.38 | 1.81 | 2.06 | -0.02 | 0.29 |
| 2002-04 | 0.40 | 4.35 | 1.56 | 1.89 | 1.84 | 1.59 | 0.03 | 0.46 |
| 1991-04 | 0.38 | 8.98 | 3.49 | 3.67 | 3.62 | 3.36 | -0.13 | 0.86 |
| 2009-08 | 0.35 | 14.04 | 0.65 | 2.52 | 1.90 | 1.41 | 0.76 | 1.16 |
| 2005-04 | 0.31 | 3.69 | 2.09 | 1.68 | 2.02 | 2.33 | 0.25 | 0.39 |


## 5. Supply-like versus demand-like episodes and disagreement

Hypothesis: disagreement between inflation indicators and demand or financial indicators may be especially common when inflation is driven by supply or relative-price shocks rather than aggregate demand. This section is descriptive: episodes are classified by inflation and demand, disagreement is compared across them, and its correlates and predictive content are tested.

Regimes from core PCE 12m and the demand block's first PC, each above or below its median. Current regime: adverse-supply-like (infl high, demand weak). Descriptive only; a sign-restricted VAR or external instruments would be the structural extension.

*Disagreement by regime*

|  | months | D_res mean | D_res median | share D_res > p75 | next-12m change, median |
|---|---|---|---|---|---|
| adverse-supply-like (infl high, demand weak) | 105 | 0.48 | 0.46 | 0.23 | -0.43 |
| demand-like (infl high, demand high) | 143 | 0.56 | 0.45 | 0.25 | -0.22 |
| favorable-supply-like (infl low, demand strong) | 106 | 0.51 | 0.51 | 0.28 | -0.01 |
| weak-demand (infl low, demand weak) | 144 | 0.57 | 0.42 | 0.24 | 0.04 |

*Contemporaneous correlates of disagreement (standardized regressors, HAC t)*

|  | corr | t (HAC) |
|---|---|---|
| headline_core_gap | -0.02 | -0.12 |
| flex_less_sticky | 0.10 | 0.43 |
| xs_sd_3m | 0.52 | 3.88 |
| oil_12m | -0.13 | -0.65 |
| abs_oil_12m | 0.49 | 3.19 |

*Subsequent change in core PCE on disagreement, current inflation, and the demand factor (HAC t)*

|  | 3m | 6m | 12m |
|---|---|---|---|
| beta D_res (pp per sd) | 0.13 | 0.13 | 0.17 |
| t | 1.64 | 1.50 | 1.89 |
| gamma pi12 | -0.19 | -0.21 | -0.29 |
| t  | -3.35 | -3.34 | -3.61 |
| delta B_dem | 0.01 | 0.01 | -0.00 |
| t   | 0.12 | 0.11 | -0.00 |
| R2 | 0.07 | 0.11 | 0.20 |


## 6. Additional evidence

Four further pieces of evidence feed the answers in the next section: the probability that inflation will be lower over each horizon, a horse race of individual statistics as additions to core PCE 12m, the history of inflation conditional on breadth, and an event study of episodes in which the 3-month rate fell well below the 12-month rate.

*Probability that core PCE inflation is lower over the next h months than the current 12m rate*

|  | 3m | 6m | 12m | 24m |
|---|---|---|---|---|
| P(lower) model | 0.53 | 0.82 | 0.87 | 0.79 |
| unconditional | 0.51 | 0.57 | 0.57 | 0.56 |

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


## 7. Answers


### 1. Best estimate of underlying inflation today

- Core PCE 3.0 / 3.4 / 3.3 (3m/6m/12m); median CPI 2.7, trimmed PCE 2.3, sticky 2.8, flexible 4.7 (12m).
- Common signal across the 11 12m measures (median): 2.7. Above it by more than 0.25: cpi_12m, pce_12m, pce_core_12m, cpi_flex_12m; below: pce_trim_12m, cpi_core_flex_12m.
- Disagreement among measures at the 53rd percentile (12m) and 42nd (3m): not unusual.


### 2. Accelerating or decelerating

- 10 of 11 measures have 3m below 12m; core PCE 3m-12m gap -0.3 pp, 6m-12m +0.1.
- Iterated DFM forecast of the 12-month rate: 3.3 / 2.9 / 2.4 / 2.4 at 3/6/12/24 months ahead, against 3.3 today: decelerating (-0.93 pp at 12m).
- P(12-month rate below today's): 53% / 82% / 87% / 79% at 3/6/12/24 months ahead (unconditional about 57%).


### 3. Breadth

- Share of categories above 2/3/4/5%: 52 / 45 / 15 / 9% at 3m; 76 / 56 / 35 / 18% at 12m.
- Breadth (above 3%) is falling over three months at 3m (-18 pp) and rising over a year at 12m (+13 pp).
- Historical position: breadth 45th percentile (3m), 65th (12m); cross-sectional SD 52nd; upper-tail share 13th.
- Reading: broad-based at 12m; at 3m the rise is not unusually concentrated.


### 4. Does breadth predict future inflation

- High-breadth months (top quartile): core PCE averaged 3.3% over the next 12m and stayed above 2.5% in 79% of cases, against 1.8% and 11% for low breadth. Inflation stayed elevated, but it was already high.
- Given core PCE 12m and 3m, breadth (3m) has HAC t = +1.0 / +0.7 / +0.7 for the 3/6/12m change and relative RMSFE 1.01 / 1.01 / 1.02: little incremental content. Breadth at 12m: t -0.0, rel RMSFE 1.04.
- Against median CPI (rel RMSFE 12m 1.02) and trimmed PCE (1.08), breadth is not more useful. Adding the block factors to the global-factor model moves the 12m projection by -0.35 pp.


### 5. Most useful current statistics

- Best single addition to core PCE 12m by horizon: 3m core PCE 6m (0.98); 6m core PCE 6m (0.97); 12m core PCE 6m (0.99). Gains are small everywhere.
- Forward-looking (beats core PCE 12m alone at two or more horizons): none. Contemporaneous summaries (|corr| > 0.8, no out-of-sample gain): core PCE 3m, core PCE 6m, core CPI 12m, median CPI 12m, median CPI 3m, trimmed PCE 12m, trimmed CPI 12m, sticky CPI 12m.


### 6. Recent favorable readings: signal or noise

- Spells with core PCE 3m at least 1 pp below 12m: 8 since 1985; a genuine turning point (12m rate down at least 0.5 pp a year later) in 38%, reacceleration within six months in 50%.
- Today's gap is -0.29 pp (below the event threshold). The factor-space analogs saw a median 12m change of -0.02 pp with deceleration in 53% of cases: closer to a soft patch than a sustained disinflation.


### 7. Are financial conditions restrictive

- Financial factor (+ = looser) -0.27 z, 45th percentile: near its historical middle.
- 83% of 12 indicators sit on the loose side of their median: loose = fedfunds, dgs10, nfci, vix, baa_spread, ebp, equity_12m_ret, usd_12m, mortgage30, sloos_ci; tight = real_10y_clev, term_premium_10y.
- Financial conditions reach inflation only through the factor VAR; the block factors together move the 12m projection by -0.35 pp relative to the global-only model.


### 8. Is demand pressure still inflationary

- Demand factor -0.54 z (20th percentile); G2 +0.85. the block factors together move the 12m projection by -0.35 pp relative to the global-only model.
- Drivers today (loading x z): unrate +nan, payrolls_3m +nan, payrolls_12m +nan, claims_log +nan, vu_ratio +nan. Unemployment 4.1 (18th pct), V/U 1.05, wages 3.2%, real PCE 6m 3.0%.


### 9. Are expectations a problem

- Levels: Michigan 1y 4.2 (79th pct), SPF 4q 2.3 (48th), 5y breakeven 2.37 (75th), 5y5y 2.33 (55th), SPF 10y 2.3.
- Disagreement: SPF cross-sectional SD 0.94 (95th pct); households minus professionals +1.9 pp (96th).
- Predictive content: SPF dispersion as a single addition to core PCE 12m, rel RMSFE 1.07 (t +1.5); Michigan 1y 1.03 (t -0.1). The block is the most inflationary residual in the disagreement decomposition (+0.18).


### 10. What drives the current forecast

- 12m projection 2.4 against a current 12m rate of 3.3; the block factors account for -0.35 pp of it relative to the global-only model.
- Over the last 12 months, news revised this projection by +0.30 pp. Pushing up: exp +0.06, fin +0.08, dist +0.08, infl +0.20; pushing down: dem -0.12.


### 11. Agreement or disagreement

- Cross-block disagreement 0.11, 0th percentile (SD across factors 0th). Outliers: exp +0.18, dem -0.15, fin +0.08.
- Within inflation measures 53rd percentile; between price and non-price blocks 0th: mainly within the inflation measures; overall not historically unusual.


### 12. Historical analogs

- Closest configurations: 1993-08, 2011-04, 2005-10, 1991-10, 1996-01, 2008-05.
- Subsequent 3/6/12m core PCE (median) 2.1 / 1.9 / 2.1; 12m change median -0.02. Outcomes: sustained disinflation 20%, reacceleration 13%, mixed 67%.


### 13. Disagreement and supply-versus-demand

- Mean disagreement by regime: adverse-supply-like 0.48, demand-like 0.56, favorable-supply-like 0.51, weak-demand 0.57: not higher in supply-like than in demand-led episodes.
- Correlates: cross-sectional dispersion +0.52 (t +3.9), |oil shock| +0.49, flexible minus sticky +0.10, headline-core gap -0.02.
- Given current inflation and demand, a 1-sd rise in disagreement changes the subsequent 12m inflation change by +0.17 pp (t +1.9): no faster mean reversion. Descriptive, not structural.


### 14. Implications for the Fed debate

- Projected core PCE stays above 2% at all horizons (3.3 / 2.9 / 2.4 / 2.4); projected change -0.93 pp over 12m (time-series benchmark -0.17).
- Evidence for deceleration: 10/11 measures decelerating, P(lower in 12m) 87%, analogs decelerating 53%: strong.
- Uncertainty: 12m pseudo-out-of-sample RMSE 0.83 pp; block disagreement at the 0th percentile.
- Risks implied by the outputs: persistence moderate (forecast level); reacceleration moderate (expectations residual +0.18, historical reacceleration frequency 50%); premature tightening notable (demand factor at the 20th percentile).


### 15. Warsh, Waller, Kashkari

- Warsh (inflation broad, policy not restrictive): breadth at 12m at the 65th percentile (56% above 3%) and financial conditions at the 45th percentile on the loose side, so the breadth leg of the argument find support; demand at the 20th percentile does not.
- Waller (underlying inflation declining): 10/11 measures show 3m below 12m; the model projects -0.93 pp over 12m with P(lower) 87%, so the momentum is confirmed; comparable gaps were turning points 38% of the time.
- Kashkari (entrenchment from waiting): the 12m forecast stays at 2.4%, the expectations block is the most inflationary residual (+0.18) with households +1.9 pp above professionals, and analogs reaccelerated in 13% of cases: partly supports the concern on level and expectations, less so on historical reacceleration.

Caveat: latest-vintage data and full-sample factor loadings; the news decomposition is pseudo-real-time (no data revisions; publication lags only at the ragged edge). Rule-based wording thresholds are in the answers section of run.py.
