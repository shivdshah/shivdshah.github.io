---
title: Forecasting Portfolio Risk Using GARCH and Value-at-Risk
tags:
  - risk-management
  - garch
  - value-at-risk
  - r
description: A quantitative analysis of six large-cap US stocks across a ten-year window using PCA and GARCH modelling.
---

*A quantitative analysis of six large-cap US stocks, 2010–2020 · Tools: R · rugarch · quantmod*

<div class="abstract">
<p>This project builds a risk model for a diversified equity portfolio, starting from raw stock prices and ending with a statistical forecast of how much the portfolio could lose on any given day. It documents the key statistical features of financial returns (fat tails and volatility clustering) before using Principal Component Analysis (PCA) and GARCH models to estimate and forecast portfolio volatility. The model's accuracy is then tested against historical data through a process called backtesting.</p>
</div>

<span class="section-number">Section 01</span>

## Building the portfolio

The portfolio consists of six large-cap US companies, chosen to span three distinct economic sectors and thereby reduce the impact of any single industry downturn on overall performance.

| Company | Ticker | Sector | Weight |
|---------|--------|--------|--------|
| Microsoft | MSFT | Technology | 16.7% |
| Apple | AAPL | Technology | 16.7% |
| Verizon | VZ | Telecommunications | 16.7% |
| AT&T | T | Telecommunications | 16.7% |
| Mastercard | MA | Payments | 16.7% |
| Visa | V | Payments | 16.7% |

Ten years of daily adjusted closing prices were downloaded from Yahoo Finance, covering 1 January 2010 to 1 January 2020. Adjusted prices account for events like stock splits and dividend payments, ensuring the data reflects actual investor returns rather than raw price movements.

Prices were then converted into *log returns* (the natural logarithm of today's price divided by yesterday's price). Log returns have several mathematical advantages over simple percentage changes: they can be added across time periods, they treat gains and losses symmetrically, and they are not artificially bounded, making it easier to fit statistical models to them.

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

> [!note] Why 2,515 observations, not ~3,650?
> A decade spans roughly 3,650 calendar days, but stock markets are closed on weekends and public holidays. After removing non-trading days and losing the very first observation (a return requires two prices), the dataset contains 2,515 daily log returns. Each day's portfolio return is a simple equal-weighted average of the six individual stock returns.

<span class="section-number">Section 02</span>

## The statistical properties of financial returns

Before building a risk model, it is important to understand what the underlying data actually looks like. Financial returns are well-known to exhibit two features that distinguish them sharply from a simple bell curve (normal distribution): *fat tails* and *volatility clustering*. Both features have important practical implications for risk management.

| Statistic | Microsoft | Apple | Verizon | AT&T | Mastercard | Visa |
|-----------|-----------|-------|---------|------|------------|------|
| Avg. daily return | 0.07% | 0.10% | 0.05% | 0.04% | 0.10% | 0.09% |
| Daily std. deviation | 1.43% | 1.62% | 1.05% | 1.06% | 1.59% | 1.47% |
| Best single day | +9.94% | +8.50% | +7.40% | +4.88% | +12.57% | +13.97% |
| Worst single day | −12.10% | −13.19% | −5.66% | −8.40% | −11.19% | −13.55% |
| Skewness | −0.108 | −0.341 | −0.082 | −0.693 | −0.078 | −0.144 |
| Kurtosis | 6.44 | 4.82 | 2.45 | 4.80 | 7.58 | 9.21 |

A few things stand out immediately. Average daily returns are very small, a fraction of a percent, while the worst and best single days can be ten times larger than the typical daily swing. Skewness is negative for all six stocks, meaning extreme losses are slightly more common than extreme gains. Kurtosis values well above 3 (the normal distribution benchmark) confirm what the extreme daily returns already suggest: there is far more action in the tails than a normal distribution would predict.

### Fat tails: why extreme events happen more often than expected

A fat-tailed distribution is one where the probability of an extreme outcome (a very large gain or a very large loss) is higher than a normal distribution with the same average and standard deviation would suggest. This is not just a statistical curiosity. A risk model that assumes normality will systematically underestimate the likelihood of large losses, leading managers and regulators to hold too little capital as a buffer.

Two complementary methods were used to confirm fat tails in the data. QQ-plots (quantile-quantile plots) compare the actual distribution of returns against a theoretical normal distribution: if returns were normally distributed, the dots would fall neatly on a straight line. For all six stocks, the dots curve sharply away from the line at both ends, the signature shape of fat tails. Histograms tell the same story visually. The actual return distributions have a taller, narrower peak than the fitted normal curve, and noticeably heavier wings.

The Jarque-Bera test formalises this observation. It combines skewness and excess kurtosis into a single test statistic and asks whether, jointly, they are consistent with a normal distribution. For all six stocks the test statistic is dramatically larger than the critical value and the p-value is effectively zero, giving overwhelming statistical evidence that none of the return series are normally distributed.

$$JB = \frac{T}{6}\left(S^2 + \frac{(K-3)^2}{4}\right) \sim \chi^2_2$$

where $T$ is the number of observations, $S$ is skewness, and $K$ is kurtosis. Under the null hypothesis of normality, $JB$ follows a chi-squared distribution with two degrees of freedom. We reject normality for all six stocks at the 1% significance level.

### Volatility clustering: calm and storm arrive in runs

A second well-documented feature of financial returns is that periods of high volatility tend to cluster together: a turbulent day is more likely to be followed by another turbulent day than by a calm one, and vice versa. This means that, while tomorrow's return is essentially unpredictable, tomorrow's *level of risk* is partially predictable from recent history. This is a crucial insight for risk management.

Autocorrelation is the statistical tool used to detect this pattern. It measures how strongly a series is correlated with its own past values at different time lags. Plotting the autocorrelation of the raw returns shows little beyond noise. There is no consistent pattern to predict whether tomorrow's return will be positive or negative. Plotting the autocorrelation of the *squared* returns (a proxy for the magnitude of daily moves) tells a completely different story: large positive autocorrelations persist across many lags for all six stocks, particularly Mastercard. Squaring the returns captures the size of the move regardless of direction, so this pattern confirms that large moves, in either direction, tend to follow other large moves.

The Ljung-Box test confirms this formally. Tested at lags of 1, 10, and 30 trading days, the test overwhelmingly rejects the hypothesis that the squared returns are independent across time for all six stocks. The data exhibit statistically significant volatility clustering.

$$J_K = T(T+2)\sum_{k=1}^{K}\frac{\hat{\rho}_k^2}{T-k} \sim \chi^2_K$$

where $T$ is the sample size, $K$ is the number of lags tested, and $\hat{\rho}_k$ is the estimated autocorrelation at lag $k$. The null hypothesis is that the first $K$ autocorrelations are jointly zero (no serial correlation). We reject this for all six stocks at lags 1, 10, and 30.

<span class="section-number">Section 03</span>

## Estimating the model: PCA and GARCH

With the properties of the data established, the next step is to build a model that can produce a forward-looking estimate of portfolio volatility. The challenge is doing this for a portfolio of six stocks simultaneously, since the volatility of the overall portfolio depends not just on how volatile each stock is individually, but also on how they move relative to one another.

### The dimensionality problem

A full multivariate model would require estimating a 6x6 variance-covariance matrix (21 distinct quantities) at every point in time. As the number of assets grows, this becomes computationally unwieldy and statistically unreliable. A portfolio of 50 stocks, for example, would require over 1,200 parameters. Two additional problems arise: the matrix may not always be mathematically well-behaved (technically, it may fail to be positive semi-definite), and with many parameters comes substantial estimation error.

The solution is to exploit the fact that the bulk of correlated movement across assets typically comes from a small number of common risk factors, such as broad market direction. Most of the information in six individual return series can be captured by just a handful of underlying drivers.

### Step 1: Principal Component Analysis

Principal Component Analysis (PCA) is a dimensionality-reduction technique that finds the directions in which the data varies most, and expresses each original series as a combination of these underlying directions, called principal components (PCs).

Intuitively, PCA asks: if you had to describe the movement of six stocks using a single number, what combination of those stocks would give you the most information? That combination is the first PC. The second PC is the most informative combination that is uncorrelated with the first, and so on. By construction, the PCs are independent of each other, which makes subsequent modelling much cleaner.

> [!note] How much variance do the PCs explain?
> The first PC alone explains 55% of total return variation across the six stocks. This is effectively the market factor, capturing the tendency for all stocks to rise and fall together. The second PC (15%) can be interpreted as a tilt between technology/telecoms stocks on one side and payments stocks on the other. Together, the first four PCs account for over 85% of total variation, allowing the model to reduce from six variables to four without significant loss of information.

### Step 2: GARCH(1,1) on each principal component

A GARCH (Generalised Autoregressive Conditional Heteroskedasticity) model is the standard tool for capturing volatility clustering in financial data. Rather than assuming that volatility is constant, it models it as a dynamic quantity that evolves over time, influenced by both yesterday's return and yesterday's volatility estimate.

The GARCH(1,1) model (the most widely-used variant) describes today's variance as a weighted sum of three terms: a long-run average, last period's squared return (which captures how large yesterday's shock was), and last period's variance estimate (which provides persistence). If yesterday's move was large, today's estimated volatility rises. If markets have been calm for a while, the estimated volatility gradually drifts back towards its long-run level.

$$\sigma_t^2 = \omega + \alpha\, r_{t-1}^2 + \beta\, \sigma_{t-1}^2$$

where $\omega > 0$ is the long-run variance component, $\alpha \geq 0$ is the coefficient on last period's squared return (the ARCH term), and $\beta \geq 0$ is the coefficient on last period's conditional variance (the GARCH term). The condition $\alpha + \beta < 1$ ensures the process is stationary and that volatility reverts to its long-run mean over time.

A separate GARCH(1,1) model was fitted to each of the four retained principal components. Because the PCs are uncorrelated by construction, these four models can be estimated independently, which is a major practical advantage. The resulting time-varying variances for each PC are then combined, along with the residual variation not explained by the PCs, to reconstruct a full 6x6 conditional variance-covariance matrix for the portfolio at every point in time.

<span class="section-number">Section 04</span>

## Results: conditional volatility and Value-at-Risk

With the model estimated, it becomes possible to produce a volatility forecast for any target date. The goal here was to estimate the portfolio's risk on the first trading day of 2020 (2 January 2020), using all information available up to the last trading day of 2019, 31 December 2019.

<div class="stat-grid">
  <div class="stat-card">
    <span class="stat-label">Conditional volatility</span>
    <span class="stat-value">0.663%</span>
    <span class="stat-sub">forecast for 2 Jan 2020</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">VaR at 5%</span>
    <span class="stat-value">1.09%</span>
    <span class="stat-sub">of portfolio value</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Violations</span>
    <span class="stat-value">133</span>
    <span class="stat-sub">vs 123 expected</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Violation ratio</span>
    <span class="stat-value">1.08×</span>
    <span class="stat-sub">slight under-forecast</span>
  </div>
</div>

### What is Value-at-Risk?

Value-at-Risk (VaR) summarises the downside risk of a portfolio in a single number. A VaR of 1.09% at the 5% level means that there is a 95% probability that the portfolio will not lose more than 1.09% of its value on a given day. Put differently, on roughly one trading day in twenty, the loss is expected to exceed this threshold.

The parametric approach used here computes VaR by multiplying the conditional volatility estimate by the relevant point from the normal distribution (−1.645 for the 5% level). This is fast and analytically clean, but inherits the known limitation that actual returns have fatter tails than the normal distribution implies, meaning the true probability of exceeding VaR may be slightly higher than 5%.

$$\text{VaR}_p = -P_{T-1}\,\sigma_T\,\Phi^{-1}(p)$$

where $P_{T-1}$ is the portfolio value at the previous period, $\sigma_T$ is the conditional volatility forecast for period $T$, and $\Phi^{-1}(p)$ is the inverse of the standard normal CDF at probability level $p$. At the 5% level, $\Phi^{-1}(0.05) = -1.645$, giving $\text{VaR}_{5\%} = 1.645 \times \sigma_T \times P_{T-1}$.

<div class="result-banner">
  <div>
    <span class="result-label">5% parametric VaR — 2 January 2020</span>
    <span class="result-value">1.091%</span>
  </div>
  <p class="result-context">On the first trading day of 2020, the model forecast that the equally-weighted portfolio would lose more than 1.091% of its value with a probability of 5%. Multiplied by the portfolio's market value, this translates directly into a monetary loss threshold for risk management purposes.</p>
</div>

It is worth noting that VaR is a quantile measure. It tells you the threshold, but says nothing about how bad losses could be *beyond* that threshold. A complementary measure, Expected Shortfall (also called Conditional VaR), addresses this by averaging the losses that occur in the worst 5% of days, providing a fuller picture of tail risk.

<span class="section-number">Section 05</span>

## Backtesting: how good was the forecast?

Producing a VaR estimate is only useful if that estimate is reliable. Backtesting evaluates a model's performance by applying it systematically to historical data and comparing its forecasts to what actually happened.

### The rolling-window approach

The backtesting procedure works as follows. A window of 60 trading days (chosen as three divided by the VaR confidence level of 5%, following standard practice) is used to estimate the model. A VaR forecast is made for the day immediately following the window. The window then rolls forward by one day and the process repeats, generating a sequence of daily VaR forecasts that can be compared against actual portfolio returns.

A *violation* occurs whenever the realised portfolio return falls below (i.e., is worse than) the VaR forecast for that day. If the model is well-calibrated, violations should occur exactly 5% of the time.

### Unconditional coverage test

The backtesting period yielded 133 violations against an expected 122.75, giving a violation ratio of 1.08. The model slightly underestimated risk, with losses exceeding the VaR threshold a little more often than predicted. However, a formal likelihood-ratio test (the Bernoulli unconditional coverage test) finds that this discrepancy is not statistically significant: we cannot reject the hypothesis that the true violation rate is 5%. The number of exceptions is within the range of what sampling variation alone could produce.

### Conditional coverage test

A well-functioning VaR model should not only get the overall frequency of violations right; it should also ensure that violations are *independent* of one another. If a loss breach today makes another breach tomorrow more likely, the model is failing to capture the persistence of volatility, and a firm relying on it may face consecutive bad days without adequate warning.

The conditional coverage test checks whether violations cluster in time by modelling the sequence of violations as a Markov chain and testing whether the probability of a violation on a given day depends on whether one occurred the day before. The test finds no statistically significant evidence of clustering. Violations appear to be independent across time, which is a positive result for the model's reliability.

### Rolling-window re-estimation

As a separate check, the full PCA-GARCH model was re-estimated using only the 60 most recent trading days as of 31 December 2019. This rolling-window approach places more weight on recent market conditions and less on data from several years earlier. The resulting conditional volatility estimate for 2 January 2020 was 0.438%, somewhat lower than the full-sample estimate of 0.663%, implying a VaR of 0.72% rather than 1.09%.

The discrepancy reflects the fact that by late 2019, markets had been relatively calm for an extended period. A model trained on only the most recent 60 days naturally produces lower volatility estimates than one informed by a decade of data including more turbulent episodes. Which approach is preferable depends on how quickly the practitioner believes market conditions change, which is a genuine judgement call at the heart of risk modelling.

<span class="section-number">Section 06</span>

## What I would do differently

This project necessarily involved simplifying assumptions. Reflecting on them is itself a useful exercise in understanding the limits of any quantitative model.

<ol class="steps">
  <li><p><strong>Non-normal GARCH innovations.</strong> The GARCH(1,1) model used here assumes that the random shocks driving returns follow a normal distribution even after volatility is accounted for. Given the evidence of fat tails, a Student's t-distribution would be more appropriate (t-GARCH), better capturing the probability of extreme events. This would require a larger dataset to estimate the additional shape parameter reliably.</p></li>
  <li><p><strong>Asymmetric volatility (GJR-GARCH).</strong> Empirically, negative shocks tend to increase volatility more than positive shocks of the same size, a phenomenon known as the leverage effect. The GJR-GARCH model adds a term to capture this asymmetry, which would likely improve the model's performance during market downturns.</p></li>
  <li><p><strong>Historical simulation for VaR.</strong> Rather than assuming a parametric distribution, historical simulation uses the empirical distribution of past returns directly, making no assumptions about normality. Comparing parametric and historical VaR estimates would reveal how much the normality assumption matters in practice.</p></li>
  <li><p><strong>DCC and CCC correlation models.</strong> The PCA-GARCH approach models correlations implicitly through the factor structure. Dynamic Conditional Correlation (DCC) models time-varying correlations more directly, and comparing the two approaches would give insight into how much correlation dynamics matter for portfolio risk.</p></li>
</ol>
