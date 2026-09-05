# LSST Y10 vs KiDS: Fisher Forecast Comparison

Forecast constraints on the FRB host-bias parameters $b_0$ and $\delta$ (with $b(z) = b_0 (1+z)^\delta$) from a multi-tracer analysis that combines the FRB auto-correlation with the galaxy tomographic auto- and cross-correlations of two lensing surveys: KiDS (6 bins) and LSST Y10 (10 bins).

## Method

For each FRB configuration (host population × survey depth) the Fisher matrix is built from the Reischke estimator

$$F_{ij} = f_{\rm sky}\sum_\ell \frac{2\ell+1}{2}\, \mathrm{Tr}\!\left[\hat C_\ell^{-1}\,\partial_i C_\ell\,\hat C_\ell^{-1}\,\partial_j C_\ell\right],$$

with $\hat C_\ell = C_\ell + N_\ell$ the signal-plus-noise covariance. The **FRB-only** forecast uses only the FRB auto-spectrum (a $1\times1$ covariance, galaxy-survey independent). The **multi-tracer** forecast uses the full $(N_{\rm bin}+1)\times(N_{\rm bin}+1)$ tracer covariance $[g_1,\dots,g_N,\mathrm{FRB}]$. Marginal errors are $\sigma_p = \sqrt{(F^{-1})_{pp}}$ and the figure of merit is $\mathrm{FoM} = 1/\sqrt{\det\,\mathrm{Cov}}$ (larger is tighter).

## Survey configuration

| Survey | Tomographic bins | $f_{\rm sky}$ (Fisher) | Sky area [deg²] | $\bar n_{\rm tot}$ [arcmin⁻²] |
|---|---|---|---|---|
| KiDS | 6 | 0.0327 | 1347 | 8.38 |
| LSST Y10 | 10 | 0.4363 | 18000 | 26.94 |

## Marginal 1σ constraints

Multi-tracer marginal errors for each survey, with the shared FRB-only baseline. Improvement factors are $\sigma_{\rm FRB\text{-}only}/\sigma_{\rm multi}$.

| Population | FRB survey | $\sigma_{b_0}$ FRB-only | $\sigma_{b_0}$ KiDS | $\sigma_{b_0}$ LSST | $\sigma_{\delta}$ FRB-only | $\sigma_{\delta}$ KiDS | $\sigma_{\delta}$ LSST |
|---|---|---|---|---|---|---|---|
| Magnetars | Deep | 23.45 | 1.273 | 0.2498 | 31.03 | 1.875 | 0.31 |
| Magnetars | Shallow | 91.27 | 1.906 | 0.4829 | 190.5 | 3.76 | 0.922 |
| Neutron Stars | Deep | 33.01 | 1.701 | 0.3604 | 32.32 | 1.769 | 0.3267 |
| Neutron Stars | Shallow | 100.9 | 2.414 | 0.6187 | 153 | 3.412 | 0.8536 |

## Figure of merit and improvement

| Population | FRB survey | FoM FRB-only | FoM KiDS | FoM LSST | LSST/KiDS FoM | KiDS gain vs FRB-only | LSST gain vs FRB-only |
|---|---|---|---|---|---|---|---|
| Magnetars | Deep | 0.02633 | 1.596 | 42.08 | 26.36× | 60.6× | 1598.3× |
| Magnetars | Shallow | 0.0009192 | 0.4123 | 6.297 | 15.27× | 448.6× | 6850.3× |
| Neutron Stars | Deep | 0.01604 | 1.156 | 25.76 | 22.29× | 72.0× | 1605.7× |
| Neutron Stars | Shallow | 0.0009908 | 0.345 | 5.134 | 14.88× | 348.2× | 5181.5× |

## Discussion

Across all 4 FRB configurations, LSST Y10 delivers the tighter multi-tracer constraint (higher FoM) in **4/4** cases. Three effects drive the difference:

1. **Sky area / $f_{\rm sky}$.** The Fisher information scales linearly with $f_{\rm sky}$. LSST Y10 covers $f_{\rm sky}=0.4363$ (18000 deg²) against KiDS' $f_{\rm sky}=0.0327$ (1347 deg²), a factor $\approx13.4$ more area — the single largest advantage.
2. **Tomographic resolution.** LSST Y10 splits the lens sample into 10 redshift bins versus 6 for KiDS, giving finer cross-correlation leverage against the FRB kernel and a larger multi-tracer covariance.
3. **Redshift coverage & bias.** Both samples use $b_g(z)=0.95/D_+(z)$; LSST Y10's deeper lens sample extends the useful overlap with the FRB distribution to higher redshift.

## Conclusion

**LSST Y10** provides the stronger constraints on the FRB host-bias parameters in the multi-tracer analysis. Both galaxy surveys improve substantially on the FRB-only forecast (which is noise-dominated), but the larger footprint and finer tomography of LSST Y10 make it the preferred cross-correlation partner for FRB bias measurements.

## Caveats

- The comparison uses each survey's **own footprint**; much of the LSST advantage is the larger sky area rather than intrinsic data quality. At matched $f_{\rm sky}$ the gap narrows to the tomographic/redshift terms.
- LSST per-bin number density assumes the total $\bar n = 26.94$ arcmin⁻² is split **equally** across the 10 bins; the true DESC lens counts are not uniform per bin.
- Constraints are Gaussian Fisher forecasts (linear bias, Limber approximation, $\ell = 10$–$1000$); they neglect non-Gaussian covariance and systematics.
