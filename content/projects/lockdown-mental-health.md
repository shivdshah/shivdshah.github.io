---
title: "Do Lockdowns Damage Mental Health? Evidence from Turkey's Age-Specific Curfews"
tags:
  - rd-design
  - 2sls
  - covid-19
  - mental-health
description: A replication and extension of Altındağ et al. (2022) using regression discontinuity design.
---

*A replication and extension of Altındağ et al. (2022) using regression discontinuity design · Tools: Stata · ivregress · rd*

<div class="abstract">
<p>During the COVID-19 pandemic, Turkey imposed strict curfews on everyone aged 65 and over, a policy that created a natural experiment. Because eligibility was determined purely by date of birth relative to a fixed cutoff, people just above and just below the age threshold were essentially identical in every observable way, except that one group was confined to their homes. This project replicates the original paper's regression discontinuity analysis (which uses that cutoff to isolate the causal effect of the curfew on mental health) and extends it by examining how the effects varied across different demographic groups.</p>
</div>

<span class="section-number">Section 01</span>

## The research design

Measuring the mental health impact of a lockdown is harder than it sounds. People under stricter restrictions might be more distressed, but they might also be older, have fewer social connections, or be in worse health to begin with. Simply comparing people under different restrictions tells you very little, because the groups differ in too many ways.

To get around this, the study exploits a feature of Turkey's COVID-19 policy: anyone born before January 1956 was subject to an age-specific curfew that effectively confined them to their homes for an extended period. This creates a clean threshold (a date of birth) that determines treatment, and allows for a *regression discontinuity (RD) design*.

### The logic of regression discontinuity

An RD design compares people who fall just above and just below the threshold (in this case, those born just before and just after January 1956). The key insight is that people born a few months apart on either side of this boundary should be nearly identical in every respect that matters: their health, education, life history, and social circumstances. The only thing that differs is whether they happened to be born in time to fall under the curfew. Any difference in mental health outcomes between the two groups can therefore be attributed to the curfew itself, rather than to pre-existing differences between the people.

The reduced-form specification used to estimate this effect is:

$$y_i = \alpha + \beta z_i + f(x_i) + \epsilon_i \qquad \forall\, x_i \in (c - h,\; c + h)$$

where $y_i$ is the outcome of interest (a mental health index), $z_i$ is a dummy equal to one if the respondent was born before January 1956 (i.e., subject to the curfew), $x_i$ is the forcing variable (months relative to the cutoff), $f(x_i)$ is a local linear function estimated separately on each side of the cutoff $c$, and $h$ is the bandwidth. The coefficient $\beta$ is the parameter of interest: it captures the discontinuous jump in outcomes at the age threshold.

> [!note] What is the running variable?
> The "forcing variable" in this design is the number of months a respondent's age differs from the cutoff birthday of January 1956. Negative values mean they were born after the cutoff (not subject to the curfew); positive values mean they were born before it (subject to the curfew). By looking at outcomes as a smooth function of this variable on either side of zero, and measuring any sudden jump at zero, we can isolate the causal effect of the policy.

### Validating the design

Two checks confirm that the RD design is valid. The first tests whether respondents manipulated their reported birth dates to avoid the curfew — a concern the authors address by noting that curfew enforcement relied on national ID cards, making falsification essentially impossible. Statistical tests confirm no suspicious bunching of birth dates just below the threshold.

The second check examines whether respondents' background characteristics (education, gender, marital status, ethnicity, pre-existing health conditions, and household size) change smoothly across the cutoff. If they do, it confirms that the two groups are genuinely comparable. The covariate balance graphs show no meaningful discontinuities at the threshold, validating the design.

### Controls and standard errors

The regressions control for fixed effects at the level of birth month, province, and surveyor. Birth month controls account for any seasonal patterns in health; province controls absorb regional differences in healthcare access or the stringency of enforcement; surveyor controls prevent any interviewer-level patterns from contaminating the estimates. Additional indicator variables for education level, ethnicity, and gender are included, since these characteristics may independently affect mental health outcomes.

Standard errors are clustered at the year-month of birth level, following Lee and Card (2008). This accounts for the fact that people born in the same calendar month share common experiences and may therefore have correlated outcomes that, if ignored, would understate the true uncertainty in the estimates.

<span class="section-number">Section 02</span>

## Did the curfew actually keep people indoors?

Before examining mental health, it is important to establish that the curfew had its intended effect: actually reducing mobility. Three outcomes are measured: the number of days spent outside the previous week, whether the respondent reported being under the curfew, and whether they reported never going outside at all.

| Outcome | ±17 months | ±30 months | ±45 months | ±60 months |
|---------|-----------|-----------|-----------|-----------|
| Days outside last week | −1.011 | −1.106 | −1.090 | −1.023 |
| Under curfew (probability) | +0.609 | +0.663 | +0.708 | +0.723 |
| Never goes out (probability) | +0.213 | +0.301 | +0.297 | +0.245 |

The effects are large and consistent across all four bandwidth choices. Being born before the cutoff (and therefore subject to the curfew) reduced the number of days spent outside by approximately one per week. It increased the probability of being under the curfew by around 70 percentage points, and the probability of never going outside by roughly 30 percentage points.

To put the latter in context: the control group mean probability of never going outside was around 20%. A 30 percentage point increase on top of that represents a 149% rise, so the curfew nearly tripled the proportion of people who were entirely housebound. These are not marginal effects.

<span class="section-number">Section 03</span>

## The mental health consequences

Mental health is measured using the SRQ-20, a validated 20-question screening instrument developed by the World Health Organisation. Respondents answer yes or no to questions about symptoms experienced over the past month — covering physical manifestations of distress (headaches, poor sleep, shaking hands), emotional symptoms (feeling frightened, unhappy, worthless), cognitive symptoms (trouble concentrating, difficulty making decisions), and more severe indicators (suicidal ideation). From these responses, three composite indices are constructed: an overall mental distress index, a somatic index (covering physical symptoms), and a non-somatic index (covering emotional and cognitive symptoms). All three are expressed as standardised scores, allowing effects across different scales to be directly compared.

<div class="stat-grid">
  <div class="stat-card">
    <span class="stat-label">Mental distress index</span>
    <span class="stat-value">+0.21 SD</span>
    <span class="stat-sub">increase from curfew</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Somatic symptoms</span>
    <span class="stat-value">+0.18 SD</span>
    <span class="stat-sub">headaches, sleep, digestion</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">Non-somatic symptoms</span>
    <span class="stat-value">+0.16 SD</span>
    <span class="stat-sub">mood, cognition, motivation</span>
  </div>
  <div class="stat-card">
    <span class="stat-label">SRQ-20 raw score</span>
    <span class="stat-value">+0.73 SD</span>
    <span class="stat-sub">≈ 10% above control mean</span>
  </div>
</div>

These are the reduced-form estimates. They capture the direct effect of being born before the cutoff (and therefore being subject to the curfew) on mental health, without yet translating that into the effect of each additional day spent indoors. All effects are statistically significant at standard levels and robust across different bandwidth choices.

<span class="section-number">Section 04</span>

## Instrumental variables: the effect of each day indoors

The reduced-form results show that being subject to the curfew worsened mental health. But how much of that is driven by the reduction in mobility specifically? To answer this, the analysis uses the age cutoff as an *instrumental variable (IV)*, a technique for estimating the causal effect of one variable (days spent outside) on an outcome (mental health), when that variable is itself affected by other things we cannot fully observe or control for.

### Why a simple regression is not enough

A person who goes outside less might do so because of the curfew, but also because they feel unwell, are already depressed, or have fewer reasons to leave. This means days spent outside is *endogenous*: it is correlated with the unobserved factors that also affect mental health. A standard regression of mental health on days outside would therefore produce a biased estimate of the true causal effect.

### The two-stage approach

The IV approach resolves this by using the age cutoff as a source of variation in mobility that is entirely unrelated to the person's health or character. Eligibility is determined purely by date of birth. The estimation proceeds in two stages. In the first stage, the number of days spent outside is regressed on the age cutoff dummy (and the other controls), generating a predicted value of mobility that reflects only the exogenous push from the curfew. In the second stage, mental health is regressed on this predicted mobility measure. The resulting coefficient captures the causal effect of a reduction in mobility on mental health, purged of the reverse causality and confounding that would bias a direct regression.

The second-stage equation is:

$$y_i = \gamma + \tau\, \widehat{\text{days}}_i + f(x_i) + u_i \qquad \forall\, x_i \in (c - h,\; c + h)$$

where $\widehat{\text{days}}_i$ is the predicted value of days spent outside from the first stage, and $\tau$ is the coefficient of interest: the causal effect of one additional day per week spent outdoors on mental health, for compliers around the age threshold. Because $\widehat{\text{days}}_i$ is instrumented by $z_i$ (the curfew eligibility dummy), $\tau$ is a fuzzy RD estimate, also interpretable as the ratio of the reduced-form to the first-stage coefficient.

> [!note] The three assumptions required
> For IV estimation to be valid, the instrument must be relevant (the age cutoff must genuinely affect mobility, confirmed by the first-stage results), must satisfy the exclusion restriction (it can only affect mental health through its effect on mobility, not directly; this is an untestable assumption but plausible given the mechanism), and must be as good as randomly assigned around the threshold, which is confirmed by the covariate balance tests.

<div class="result-banner">
  <div>
    <span class="result-label">IV estimate per day less outside</span>
    <span class="result-value">+0.19 SD</span>
  </div>
  <p class="result-context">Each additional day per week spent indoors (caused by the curfew) increased overall depression by 0.19 standard deviations, somatic symptoms by 0.18 SD, and non-somatic symptoms by 0.14 SD. All three are significant at the 5% level. A simple OLS regression produces estimates around 0.07 SD, less than half as large, underscoring how much endogeneity bias distorts the picture without the IV correction.</p>
</div>

Twelve IV regressions in total were run, combining three mental health outcomes with four bandwidth choices. The results are consistent throughout, providing confidence that the findings are not an artefact of any particular specification choice.

<span class="section-number">Section 05</span>

## Extension: who was hit hardest?

The average effects above conceal meaningful variation across different groups of people. As an extension to the original replication, a series of interaction regressions were run to examine how the mental health impact of the curfew varied by gender, marital status, financial situation, and attitudes towards the restrictions. Understanding this heterogeneity is directly relevant for policymakers who want to design targeted support measures.

The specification augments the baseline reduced-form with an interaction term:

$$y_i = \alpha + \beta z_i + \delta X_i + \gamma (z_i \times X_i) + f(x_i) + \epsilon_i$$

where $X_i$ is a binary indicator for a subgroup characteristic (e.g. female, widowed, financial strain), and $\gamma$ captures the differential treatment effect for that subgroup relative to the baseline.

<ul class="findings">
  <li>
    <div class="finding-num">Women</div>
    <p>Females reported mental distress scores 0.13 standard deviations higher than their male counterparts, after accounting for the curfew and other controls. This gap may reflect differences in social roles, greater exposure to domestic stressors during confinement, or differential use of mental health services.</p>
  </li>
  <li>
    <div class="finding-num">Widowed or separated</div>
    <p>Those who were widowed or separated experienced distress 0.69 standard deviations higher than their married peers, by far the largest gap across any subgroup examined. This is consistent with the idea that isolation is most harmful when individuals have no co-resident partner, and that lockdowns compound pre-existing loneliness rather than creating it from scratch. Targeted outreach (such as digital therapy programmes or community check-ins) could be particularly valuable for this group.</p>
  </li>
  <li>
    <div class="finding-num">Financial strain</div>
    <p>Those who reported not having enough money for usual needs were 0.06 standard deviations more distressed. The curfew likely exacerbated financial precarity for those with limited savings or informal income, and the mental health burden of economic stress compounds the psychological cost of immobility. This points to the value of financial support measures running in parallel with mobility restrictions.</p>
  </li>
  <li>
    <div class="finding-num">Policy opposition</div>
    <p>Those who did not support the government's restrictions were 0.04 standard deviations more distressed than those who did. This is perhaps unsurprising. Compliance with restrictions one considers unjust or ineffective is likely to be more psychologically taxing than accepting constraints one believes are necessary.</p>
  </li>
</ul>

<span class="section-number">Section 06</span>

## What this tells us

The results paint a clear picture. Turkey's age-specific curfew during the COVID-19 pandemic substantially reduced the mobility of those over 65, and that reduction in mobility carried a significant mental health cost. Being subject to the curfew increased overall distress by around 0.21 standard deviations; when translated into the per-day effect of reduced outdoor time using the IV approach, each additional day per week spent indoors raised depression by 0.19 standard deviations. For elderly populations already at elevated risk of depression, these are material effects.

The heterogeneity analysis adds texture to the headline findings. The burden was not evenly distributed. Those living alone (widowed or separated), women, and those facing financial stress bore a disproportionate share of the mental health cost. Effective pandemic policy therefore requires not just mobility restrictions, but accompanying support structures that specifically reach the most vulnerable.

More broadly, the study illustrates the value of natural experiments and quasi-experimental methods in economics. The causal question (does confinement damage mental health?) cannot be answered with a simple survey comparison, because the people who are confined and those who are not differ in too many ways. The RD design, by exploiting the sharp age cutoff, allows for a credible causal answer where a naive analysis would mislead.
