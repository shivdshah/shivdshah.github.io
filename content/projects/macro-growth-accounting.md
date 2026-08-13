---
title: "Growth Accounting and TFP Analysis: Portugal and Ethiopia"
tags:
  - macroeconomics
  - growth-accounting
  - tfp
  - python
description: Decomposing economic growth using the Penn World Tables, 1950–2019.
---

*Decomposing economic growth using the Penn World Tables, 1950–2019 · Tools: Python · pandas · NumPy · Matplotlib*

<div class="abstract">
<p>This project applies the Solow growth accounting framework to national accounts data from the Penn World Tables to understand how Portugal and Ethiopia each generated GDP growth between 1950 and 2019. It fits additive and exponential trend models to each country's GDP time path, extracts an implied measure of Total Factor Productivity (TFP) using the Cobb-Douglas production function, and decomposes annual GDP growth into the contributions of capital, labour, and productivity. The two countries were chosen deliberately as a contrast: a middle-income European economy and a lower-income Sub-Saharan African economy, allowing structural differences in the sources of growth to emerge clearly from the data.</p>
</div>

<span class="section-number">Section 01</span>

## The dataset: Penn World Tables

The Penn World Tables (version 10.0) provide harmonised national accounts data for 183 countries from 1950 onwards, expressed on a consistent 2017 USD basis. This cross-country comparability is what makes the dataset well-suited to a study like this one. Because purchasing power and price levels differ between Portugal and Ethiopia, raw GDP figures in local currency are not directly comparable. The PWT adjusts for these differences.

| Variable | Code | Description |
|----------|------|-------------|
| Real GDP | rgdpna | At constant 2017 national prices (millions USD) |
| Employment | emp | Number of employed persons (millions) |
| Capital stock | rnna | At constant 2017 national prices (millions USD) |
| Population | pop | Total population (millions) |

The analysis uses data from 1950 to 2019, giving 70 annual observations per country. After loading the data with pandas, the relevant rows were filtered by country name and the index reset to a standard integer sequence. Lower-case variable names throughout the code denote log-transformed equivalents of their upper-case counterparts: *yp* is the natural log of *YP*, Portugal's real GDP.

```python
# Load the Penn World Tables Excel file
data = pd.read_excel("pwt100.xlsx", sheet_name="Data", header=0)

# Filter to each country and select the four variables needed
data_p = data.loc[data["country"] == "Portugal", ("year", "rgdpna", "emp", "rnna", "pop")]
data_e = data.loc[data["country"] == "Ethiopia", ("year", "rgdpna", "emp", "rnna", "pop")]

# Reset index, then log-transform real GDP
data_p = data_p.reset_index(drop=True)
YP     = data_p["rgdpna"]
yp     = np.log(YP)   # lowercase = log of uppercase
T      = len(YP)      # sample size = 70
```

<span class="section-number">Section 02</span>

## Part A: trend analysis of GDP time paths

The first task was to plot the GDP time paths for both countries. First as log real GDP, then as real GDP per capita. Four trend specifications were fit to each. Working in logs is standard practice in macroeconomics because it linearises multiplicative growth: a straight line through log GDP implies a constant percentage growth rate, and deviations from the trend are interpretable directly as percentage differences.

The four trend specifications combine two functional forms (additive and exponential) with two polynomial orders (linear and quadratic):

$$\text{Additive linear:} \quad \hat{Y}_t = a + bt$$

$$\text{Additive quadratic:} \quad \hat{Y}_t = a + b_1 t + b_2 t^2$$

$$\text{Exponential linear:} \quad \log(\hat{y}_t) = a + bt$$

$$\text{Exponential quadratic:} \quad \log(\hat{y}_t) = a + b_1 t + b_2 t^2$$

All four regressions were estimated using OLS via a custom `get_regression_coefs` function, which implements the closed-form OLS formula directly rather than relying on a statistical library. The regressors were built manually: $x_1$ is a vector of ones (the intercept), $x_2$ is a time index running from 1 to $T$, and $x_3$ is its element-wise square.

```python
# Build regressor arrays for the linear case
x1, x2 = np.empty(T), np.empty(T)

for t in range(T):
    x1[t] = 1        # intercept column
    x2[t] = t + 1   # time index 1 … T

# OLS on log GDP: returns intercept and slope
a_exp_lin, b_exp_lin = get_regression_coefs(yp, x1, x2)

# Compute fitted trend values
yphat_exp_lin = np.empty(T)
for t in range(T):
    yphat_exp_lin[t] = a_exp_lin + b_exp_lin * (t + 1)
```

> [!note] Why plot log GDP rather than levels?
> A trend line through log GDP implies a constant annual growth rate, which is the natural baseline for a growing economy. In levels, the same trend would be an exponential curve, making deviations from trend harder to read visually. Working in logs also means all four trend specifications are plotted on the same axis scale, with linear and quadratic variants directly comparable.

Plotting confirmed the broad narrative each country's history suggests. Portugal shows a steep upward trajectory through the 1960s and 1970s, a levelling-off around EU accession in 1986, and a visible interruption around the 2008-2012 sovereign debt crisis. Ethiopia's log GDP path is lower and more volatile through the mid-20th century, reflecting political instability and periodic famine, before accelerating sharply from the early 2000s on the back of sustained public investment.

For Portugal, the exponential quadratic trend fits the data most closely, capturing the acceleration in early decades and the post-2008 flattening. For Ethiopia, the exponential linear trend is a reasonable summary over the full period, though it masks the structural break visible around 2000.

<span class="section-number">Section 03</span>

## Part B: extracting Total Factor Productivity

Total Factor Productivity (TFP) is the component of output not attributable to the measurable inputs of capital and labour. It captures improvements in technology, management, institutions, and efficiency more broadly. Because TFP cannot be observed directly, you must back it out from data using an assumed production function.

### The Cobb-Douglas production function

The standard workhorse in growth accounting is the Cobb-Douglas function, which relates real output to capital and labour through a simple multiplicative structure:

$$Y_t = A_t \cdot K_t^{\alpha} \cdot L_t^{1-\alpha}$$

where $Y_t$ is real GDP, $K_t$ is the capital stock, $L_t$ is employment, $A_t$ is TFP, and $\alpha$ is the capital share of income, set at the conventional empirical value of 0.3. Rearranging algebraically gives an expression for implied TFP at each point in time:

$$A_t = Y_t \cdot K_t^{-\alpha} \cdot L_t^{\alpha - 1}$$

This formula requires no estimation. It is a straightforward computation once the production function parameters are specified. The code below applies it to both countries simultaneously.

```python
alpha = 0.3

# Implied TFP: rearrange Y = A * K^alpha * L^(1-alpha) for A
data_p["A"] = (data_p["rgdpna"]
              * data_p["rnna"] ** (-alpha)
              * data_p["emp"]  ** (alpha - 1))

data_e["A"] = (data_e["rgdpna"]
              * data_e["rnna"] ** (-alpha)
              * data_e["emp"]  ** (alpha - 1))
```

<div class="stat-grid">
  <div class="stat-card">
    <span class="stat-label">Capital share (α)</span>
    <span class="stat-value">0.30</span>
    <span class="stat-sub">empirical assumption</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Labour share (1 − α)</span>
    <span class="stat-value">0.70</span>
    <span class="stat-sub">consistent with national accounts</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Portugal avg. TFP</span>
    <span class="stat-value">~700</span>
    <span class="stat-sub">steadily rising 1950–2007</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Ethiopia avg. TFP</span>
    <span class="stat-value">~170</span>
    <span class="stat-sub">volatile until 2000s</span>
  </div>
</div>

Both levels and logs of TFP were plotted for each country. Portugal's TFP grew broadly upwards through most of the period, consistent with sustained technology adoption and efficiency gains accompanying EU integration. The post-2008 plateau is clearly visible, reflecting the combined impact of the global financial crisis and the subsequent sovereign debt crisis on productivity.

Ethiopia's TFP in levels is harder to interpret because the absolute values are much lower. The log TFP plot tells a more interesting story: significant volatility through the 1970s-90s followed by a structural improvement from the early 2000s. This matches the broader literature on Ethiopian growth, which identifies infrastructure-led development and improved governance as key drivers of the acceleration.

<span class="section-number">Section 04</span>

## Part C: decomposing GDP growth

Growth accounting translates the Cobb-Douglas production function into a statement about growth rates. Taking logs of the production function and differencing over time yields:

$$\Delta \log Y_t = \Delta \log A_t + \alpha \cdot \Delta \log K_t + (1-\alpha) \cdot \Delta \log L_t$$

This says the growth rate of GDP equals the growth rate of TFP plus the capital-share-weighted growth rate of capital plus the labour-share-weighted growth rate of labour. The contribution of each factor to GDP growth is its term divided by the total, expressing how much of GDP growth in each year is attributable to each input.

```python
# Initialise arrays: T-1 periods (no log change for year zero)
dlog_Y_p = np.empty(T-1)
dlog_A_p = np.empty(T-1)
dlog_K_p = np.empty(T-1)
dlog_L_p = np.empty(T-1)

for t in range(T-1):
    dlog_Y_p[t] = np.log(data_p["rgdpna"][t+1]) - np.log(data_p["rgdpna"][t])
    dlog_A_p[t] = np.log(data_p["A"][t+1])      - np.log(data_p["A"][t])
    dlog_K_p[t] = np.log(data_p["rnna"][t+1])    - np.log(data_p["rnna"][t])
    dlog_L_p[t] = np.log(data_p["emp"][t+1])     - np.log(data_p["emp"][t])

# Fractional contribution of each input to GDP growth
p_contr_TFP = dlog_A_p / dlog_Y_p
p_contr_K   = alpha * dlog_K_p / dlog_Y_p
p_contr_L   = (1 - alpha) * dlog_L_p / dlog_Y_p
```

The results were collected into a pandas DataFrame with one row per year-pair (e.g. "1950-1951"), covering all 69 year-on-year periods in the sample. A line chart was then produced for each country plotting the three contribution series over time.

```python
p_contr_data = {
    "Growth of Y":         dlog_Y_p,
    "Growth of TFP":       dlog_A_p,
    "Growth of K":         dlog_K_p,
    "Contribution of TFP": p_contr_TFP,
    "Contribution of K":   p_contr_K,
    "Contribution of L":   p_contr_L
}

# Index rows as "1950-1951", "1951-1952", …
growth_table_p = pd.DataFrame(
    data=p_contr_data,
    index=[str(1950+x) + "-" + str(1950+x+1) for x in range(0, T-1)]
)
growth_table_p.index.name = "Time Period"
```

> [!note] Interpreting contributions greater than 1 or less than 0
> In any given year, if one factor's contribution exceeds 1 (or falls below 0), it means a factor contributed more than 100% of GDP growth. This is only possible because another factor was dragging on growth. For example, capital might contribute 120% of growth while labour subtracts 20%, still summing to 100% overall. Years with very small or negative GDP growth are particularly prone to large, volatile contribution estimates, which is why the average over many years is more informative than any individual year-pair.

<span class="section-number">Section 05</span>

## Key findings

Averaging the annual contribution figures over the full 1950-2019 period reveals a marked difference in the structure of growth between the two countries.

<div class="stat-grid">
  <div class="stat-card">
    <span class="stat-label">Portugal: avg. TFP contribution</span>
    <span class="stat-value">~40%</span>
    <span class="stat-sub">of annual GDP growth</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Ethiopia: avg. TFP contribution</span>
    <span class="stat-value">~25%</span>
    <span class="stat-sub">of annual GDP growth</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Portugal: avg. TFP growth rate</span>
    <span class="stat-value">~1.5%</span>
    <span class="stat-sub">per year</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Ethiopia: avg. TFP growth rate</span>
    <span class="stat-value">~1.2%</span>
    <span class="stat-sub">per year, more volatile</span>
  </div>
</div>

### Portugal: productivity-led convergence

A substantial share of Portugal's growth over the period came from TFP rather than raw factor accumulation. This is consistent with a convergence story: as a lower-income country adopting the technologies and practices of its more advanced European neighbours, Portugal generated productivity gains at relatively low cost. EU accession in 1986 accelerated this process, opening the economy to trade, capital flows, and institutional improvements.

Capital also made a significant contribution, particularly in the 1960s and 1970s as the country industrialised. Labour's contribution was more modest on average, partly reflecting demographic pressures and emigration in earlier decades.

<div class="result-banner">
  <div>
    <span class="result-label">Portugal: dominant growth driver</span>
    <span class="result-value">TFP</span>
  </div>
  <p class="result-context">Productivity gains, rather than simply deploying more capital or labour, account for the largest single share of Portugal's GDP growth across the 70-year sample, consistent with a lower-income economy converging on its richer EU neighbours through technology adoption rather than raw input growth.</p>
</div>

### Ethiopia: investment-driven acceleration

Ethiopia's growth story is structurally different. Capital accumulation, driven largely by large-scale public infrastructure programmes in roads, energy, and telecommunications, accounts for a higher share of growth than TFP. This is especially true in the post-2000 acceleration phase. This pattern is typical of early-stage development: before the productivity benefits of new infrastructure materialise, much of the growth is the mechanical result of adding more capital to the production process.

Labour's contribution was positive and more visible in Ethiopia than in Portugal, consistent with a younger, faster-growing workforce being drawn from subsistence agriculture into more productive employment in industry and services. TFP growth, while positive on average, was volatile across the full period and pulled down by the episodes of political disruption in the 1970s-80s.

<div class="result-banner">
  <div>
    <span class="result-label">Ethiopia: dominant growth driver</span>
    <span class="result-value">Capital (K)</span>
  </div>
  <p class="result-context">Capital accumulation, particularly public investment in infrastructure, accounts for the largest share of Ethiopia's GDP growth across the sample, with TFP and labour playing supporting roles. The growth model is consistent with early-stage development driven by input expansion rather than efficiency gains.</p>
</div>

<span class="section-number">Section 06</span>

## What I would do differently

The analysis relies on a number of simplifying assumptions standard in the growth accounting literature. Each represents a direction in which the analysis extends further.

<ol class="steps">
  <li><p><strong>Estimating α from the data.</strong> The capital share of 0.3 was imposed rather than estimated. In practice, the labour share of income (which gives 1 − α directly) is readable from national accounts data. Using country-specific, time-varying estimates of α would give a more accurate picture, particularly for Ethiopia where factor shares are likely to differ from OECD norms and have evolved over the development process.</p></li>
  <li><p><strong>Human capital adjustment.</strong> The standard Cobb-Douglas used here treats all workers as equivalent. A richer specification, following Hall and Jones (1999), adjusts the labour input for education levels, constructing a human capital index from average years of schooling and Mincerian returns. This would allow TFP to capture pure technology and institutions more cleanly, rather than absorbing differences in workforce quality.</p></li>
  <li><p><strong>Capacity utilisation.</strong> The capital stock variable measures the total stock of physical capital, not how intensively it is being used. During recessions, capital is underutilised, and the measured contribution of capital understates the role of demand conditions. Cyclically adjusting the capital input would help separate structural growth from cyclical fluctuations.</p></li>
  <li><p><strong>Sub-period analysis.</strong> Averaging contributions over 70 years obscures the distinct phases visible in both countries' time paths. Breaking the sample into sub-periods, say 1950-1985, 1986-2007, and 2008-2019 for Portugal, would reveal how the sources of growth shifted around major structural events such as EU accession and the financial crisis.</p></li>
</ol>
