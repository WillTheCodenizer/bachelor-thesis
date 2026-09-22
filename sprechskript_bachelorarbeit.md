# Bachelor Thesis Presentation Script

**Thesis title:** *Probing Fast Radio Burst Environments: Cross-Correlating Deep and Shallow FRB Surveys with KiDS DR5*  
**Target duration:** approximately 17 minutes  
**Length:** 13 slides

> The items under **On the slide** are intentionally concise. The full text under **Speaker notes** belongs in the presentation notes and should not be displayed on the slide.

---

## Slide 1 - Title and Research Question (approx. 0:45 min)

### On the slide

- Thesis title
- Will Ruppert, TU Dortmund University, 2026
- Research question: What can the spatial distribution of FRBs tell us about their progenitors?

### Visual

- Use the FRB sky distribution as a subtle background or place it on the right:  
  `programming/frb-cosmology/plots/frb/frb_sky_distribution_petroff.png`

### Speaker notes

Good morning, and thank you for being here. Today I will present my bachelor thesis on Fast Radio Bursts, or FRBs, and their spatial correlation with galaxies. FRBs are extremely short radio flashes originating at cosmological distances. Although several thousand sources are now known, the astrophysical objects that produce them have not yet been conclusively identified. Rather than studying individual bursts, my thesis investigates their statistical distribution across the sky. The central question is whether cross-correlations between FRBs and galaxies can distinguish between different progenitor models. To answer it, I developed a numerical pipeline for angular power spectra and used a Fisher analysis to forecast how accurately the relevant model parameters could be measured.

---

## Slide 2 - Motivation: Why Fast Radio Bursts? (approx. 1:15 min)

### On the slide

- Extremely bright radio pulses lasting milliseconds
- Large dispersion measures imply cosmological distances
- 4,539 bursts from 3,641 sources in the second CHIME/FRB catalogue
- Their astrophysical origin remains uncertain

### Visual

- Sky distribution of known FRBs:  
  `programming/frb-cosmology/plots/frb/frb_sky_distribution_petroff.png`
- Optional small schematic of the frequency-dependent arrival time of a dispersed pulse

### Speaker notes

Fast Radio Bursts last only milliseconds or less, but release an enormous amount of energy during that short interval. One important observable is dispersion: lower radio frequencies arrive later than higher frequencies because the signal travels through ionised matter. For many FRBs, the resulting dispersion measure is much larger than the contribution expected from the Milky Way alone. This shows that most sources are extragalactic and are often located at cosmological distances.

CHIME has dramatically increased the number of observations. The latest catalogue considered in this thesis contains 4,539 bursts from 3,641 distinct sources. Nevertheless, their emission mechanisms and progenitors remain uncertain. Precisely localising individual bursts and assigning them to host galaxies is difficult. A statistical approach therefore offers an alternative: even without an individual redshift for every FRB, the population as a whole can be compared with the known large-scale distribution of galaxies.

---

## Slide 3 - Two Possible Progenitor Models (approx. 1:25 min)

### On the slide

| Model | Expected environment | Bias model |
|---|---|---|
| Young magnetars | Active star formation, short delay | $b_0=1.0$, $\delta=0.8$ |
| Delayed neutron-star channels | Older populations, long delay | $b_0=1.5$, $\delta=0.2$ |

- Parameterisation: $b(z)=b_0(1+z)^\delta$

### Visual

- Bias evolution of both populations:  
  `programming/frb-cosmology/plots/frb/FRB_bias_bz.pdf`

### Speaker notes

In this thesis, I compare two simplified classes of possible progenitors. The first model describes young magnetars. They are primarily formed through the collapse of massive stars and should therefore follow the cosmic star-formation rate with little delay. This interpretation is also supported by the detection of an FRB-like burst from the Galactic magnetar SGR 1935+2154.

The second model represents delayed neutron-star channels, such as compact-object mergers or accretion-induced collapse. These events may occur billions of years after the original star formation and can therefore also be found in older galaxy populations.

Their different evolution is represented by a linear tracer bias, $b(z)=b_0(1+z)^\delta$. Here, $b_0$ sets the present-day amplitude, while $\delta$ determines how strongly the bias grows with redshift. The two models consequently leave different signatures in their spatial distributions. The goal of the cross-correlation analysis is to constrain these two bias parameters.

---

## Slide 4 - The Basic Idea of Cross-Correlation (approx. 1:25 min)

### On the slide

- FRBs and galaxies trace the same underlying matter distribution
- Angular power spectrum $C_\ell$: clustering as a function of angular scale
- A cross-signal requires spatial overlap
- Tomography provides several redshift windows

### Visual

- Create a simple schematic showing:
  1. the underlying matter structure,
  2. FRB and galaxy positions on top of it,
  3. six galaxy redshift windows along the line of sight.
- No external figure is required

### Speaker notes

The basic idea is that both galaxies and FRB host objects trace the same underlying matter distribution. If a region of the sky contains more galaxies than average and we also observe more FRBs there, this produces a positive cross-correlation signal.

This signal is quantified by the angular power spectrum, $C_\ell$. Small multipoles correspond to large angular structures, while large multipoles probe small angular scales. The overlap along the line of sight is crucial: a low-redshift galaxy population only correlates with the fraction of FRBs located in the same redshift range.

KiDS divides its galaxies into six tomographic redshift bins. This means that FRB clustering is measured through six different radial weighting functions instead of one integrated projection. The resulting redshift information should help separate the overall bias amplitude, $b_0$, from its redshift evolution, $\delta$.

---

## Slide 5 - Data and Survey Scenarios (approx. 1:20 min)

### On the slide

- Two simulated FRB surveys:
  - **Shallow:** 5,000 bursts, $\alpha=3.5$
  - **Deep:** 50,000 bursts, $\alpha=2.0$
- FRB distribution: $n(z)\propto z^2\exp(-\alpha z)$
- KiDS DR5: 1,347 deg² and six tomographic bins

### Visual

- Left: FRB redshift distributions  
  `programming/frb-cosmology/plots/frb/FRB_nz_shallow_deep.pdf`
- Right: KiDS redshift bins  
  `programming/frb-cosmology/plots/galaxy/Galaxy_nz_bins.pdf`

### Speaker notes

Because individual redshifts are not assumed to be available for the FRB population, I model its normalised distribution as $n(z)\propto z^2\exp(-\alpha z)$. I consider two scenarios. The shallow survey contains 5,000 bursts and is more strongly concentrated at low redshift. The deep survey contains 50,000 bursts and has a substantially longer high-redshift tail. Both are assumed to cover 90 percent of the sky.

For the galaxy sample, I use the published redshift distributions from KiDS DR5. The survey covers 1,347 square degrees and is divided into six tomographic bins. These plots already indicate which combinations should provide the strongest signal. The lower KiDS bins overlap considerably with both FRB scenarios, whereas the higher bins benefit mainly from the deep survey. Alongside the number of objects, this radial overlap is the key factor determining the eventual parameter constraints.

---

## Slide 6 - Numerical Pipeline (approx. 1:35 min)

### On the slide

1. Planck 2018 $\Lambda$CDM cosmology
2. Non-linear matter power spectrum $P(k,z)$
3. Selection functions and bias $\rightarrow$ radial kernels
4. Limber projection $\rightarrow C_\ell$
5. Shot noise and Fisher matrix

$$
C_\ell^{AB}\approx\int\frac{\mathrm d\chi}{\chi^2}
W^A(\chi)W^B(\chi)
P\!\left(\frac{\ell+1/2}{\chi},z\right)
$$

### Visual

- Show the pipeline as a horizontal flow chart
- Optionally include a small version of:  
  `programming/frb-cosmology/plots/power_spectrum/Pk_nonlinear.pdf`

### Speaker notes

The calculation starts with a flat $\Lambda$CDM cosmology using the Planck 2018 parameters. I calculate the non-linear three-dimensional matter power spectrum, $P(k,z)$, with the Python package `hmf`. All quantities are evaluated on a common redshift grid from 0.01 to 5.

For each population, I then construct a radial kernel. It is essentially the product of the normalised redshift distribution and the bias. The angular power spectrum is obtained through the Limber projection shown here, which combines both radial kernels with the matter power spectrum. I calculate multipoles from $\ell=10$ to 1,000 because the Limber approximation is unreliable on the very largest angular scales.

The pipeline produces auto-spectra for the FRBs and for each KiDS bin, as well as all FRB-galaxy cross-spectra. With two progenitor models, two FRB surveys, and six galaxy bins, this gives 24 cross-spectra. In the final step, these spectra and their noise contributions enter the Fisher forecast.

---

## Slide 7 - Why FRB Auto-Correlation Is Not Enough (approx. 1:15 min)

### On the slide

- Discrete sources produce Poisson noise: $N_\ell=1/\bar n$
- Shallow survey: noise is about three orders of magnitude above the signal
- The FRB auto-spectrum is strongly shot-noise dominated

### Visual

- Main figure:  
  `programming/frb-cosmology/plots/frb/FRB_magnetar_Cell_shallow_shotnoise.pdf`
- Optional shallow-versus-deep comparison:  
  `programming/frb-cosmology/plots/frb/FRB_magnetar_Cell_comparison.pdf`

### Speaker notes

Before considering the cross-correlation, the FRB auto-correlation reveals the central problem. FRBs are discrete and rare compared with galaxies. The measured auto-spectrum therefore contains a constant Poisson contribution of $1/\bar n$.

For the shallow survey with 5,000 bursts, this shot noise lies roughly three orders of magnitude above the clustering signal throughout the multipole range considered. In principle, the auto-spectrum contains information about the host bias, but in practice that information is overwhelmed by noise.

The deep survey reduces shot noise through its ten times larger source count. Its projected clustering signal is also slightly smaller because of the broader redshift distribution. The essential point remains that more FRBs help, but the auto-correlation still relies on a sparse sample. Combining it with the much denser galaxy population is therefore not a minor optimisation; it is the central element of the method.

---

## Slide 8 - Tomographic Cross-Signal (approx. 1:20 min)

### On the slide

- 24 cross-spectra: 2 populations × 2 surveys × 6 KiDS bins
- Signal strength follows radial overlap
- Low-redshift bins: stronger signal from the shallow survey
- High-redshift bins: relatively more information from the deep survey

### Visual

- Use the full slide for:  
  `programming/frb-cosmology/plots/frb_x_galaxy/comparisons/survey_magnetar_all_bins.pdf`
- Highlight individual curves or groups of bins while presenting

### Speaker notes

Here we see the cross-spectra for the magnetar model, including all six KiDS bins and both FRB surveys. Their amplitudes depend directly on the overlap between each galaxy distribution and the corresponding FRB distribution.

The shallow survey is concentrated at low redshift and therefore produces a stronger signal in the lower KiDS bins. The deep survey spreads its sources across a wider radial range. This broad projection dilutes its low-redshift signal, but leaves comparatively more signal in the higher bins.

Each galaxy bin therefore observes the FRB bias through a different redshift window. This is the value of tomography. A change in $b_0$ rescales all windows, while a change in $\delta$ affects high redshifts differently from low redshifts. The cross-correlation can consequently separate the two parameters more effectively.

---

## Slide 9 - Fisher Forecast (approx. 1:15 min)

### On the slide

- Parameters: $\theta=(b_0,\delta)$
- Central finite differences with a 1% step size
- All cosmological parameters held fixed
- Larger Figure of Merit = smaller error ellipse

$$
\mathrm{FoM}=\frac{1}{\sqrt{\det(\mathrm{Cov})}}
$$

### Visual

- Use a simplified error ellipse with axes labelled $b_0$ and $\delta$
- Introduce the actual result figure on the next slide

### Speaker notes

To translate the spectra into expected parameter uncertainties, I use a Fisher matrix. It measures how sensitively all auto- and cross-spectra respond to small changes in $b_0$ and $\delta$. I calculate the derivatives numerically using central differences with a relative step size of one percent, while holding the cosmological parameters fixed.

The inverse Fisher matrix gives the expected covariance. Its diagonal elements provide the marginalised one-sigma uncertainties, while the shape and orientation of the ellipse show the degeneracy between the two parameters. I also summarise the joint two-dimensional precision with a Figure of Merit. It is inversely proportional to the area of the error ellipse, so a larger value indicates a stronger constraint.

It is important to note that a Fisher analysis assumes a locally Gaussian likelihood. These results should therefore be interpreted as optimistic forecasts rather than uncertainties that have already been measured.

---

## Slide 10 - Main Result: Cross-Correlation Enables the Measurement (approx. 1:40 min)

### On the slide

- Uncertainties on $b_0$ and $\delta$ improve by factors of **17-51**
- Figure of Merit improves by factors of **61-449**
- Deep + magnetar + KiDS: $\sigma_{b_0}=1.27$, $\sigma_\delta=1.88$
- KiDS still cannot distinguish the two progenitor models

### Visual

- Central result figure:  
  `programming/frb-cosmology/plots/fisher/fisher_comparison_2x2.pdf`
- Optionally add a compact table with only “FRB”, “FRB × KiDS”, and “gain”

### Speaker notes

This is the central result of the thesis. The blue contours show the forecasts from FRB auto-correlation alone, while the orange contours show the joint analysis with the six KiDS bins. In all four cases, the blue contours extend far beyond the plotted range. This quantitatively confirms that the FRB auto-correlation cannot meaningfully constrain the host bias.

Adding the cross-correlations reduces the marginalised uncertainties on the two parameters by factors between 17 and 51. The two-dimensional Figure of Merit improves by factors between 61 and 449. This is particularly notable because the joint analysis uses only the small KiDS overlap area, about 3.3 percent of the sky, whereas the FRB auto-correlation assumes 90 percent sky coverage. The additional tracer and redshift information more than compensates for the loss of area.

The deep survey provides tighter constraints in every case, mainly because it contains ten times as many bursts. Once cross-correlation mitigates the shot-noise problem, however, its relative advantage becomes smaller. At that point, the overlap of the redshift distributions and the limited KiDS area become the dominant restrictions.

Despite the considerable improvement, the two fiducial progenitor models still lie within the one-sigma contours. KiDS makes a meaningful bias constraint possible, but it cannot yet reliably distinguish between the magnetar and delayed neutron-star scenarios.

---

## Slide 11 - Outlook: From KiDS to LSST (approx. 1:25 min)

### On the slide

- KiDS: 1,347 deg² and 6 bins
- LSST Y10: approximately 18,000 deg² and 10 bins
- Deep magnetar scenario:
  - $\sigma_{b_0}: 1.27\rightarrow0.25$
  - FoM: $1.59\rightarrow42.01$
- Models lie outside each other's $1\sigma$ contours

### Visual

- KiDS-versus-LSST Fisher contours:  
  `programming/frb-cosmology/plots/fisher_lsst/fisher_kids_vs_lsst_2x2.pdf`

### Speaker notes

The most direct next step is to use a larger galaxy survey. LSST will cover approximately 18,000 square degrees, around thirteen times the area of KiDS. It will also provide ten rather than six tomographic bins and a deeper galaxy sample.

I therefore ran the same pipeline with an LSST Year 10 model distribution. In the deep magnetar scenario, the uncertainty on $b_0$ decreases from 1.27 with KiDS to 0.25 with LSST. The Figure of Merit increases from 1.59 to 42.01, a factor of about 26. Most of this improvement follows directly from the larger sky area, with additional information coming from finer tomography and greater depth.

In this forecast, the separation between the two progenitor models lies outside their respective one-sigma contours for the deep survey. Cross-correlating FRBs with an LSST-like data set could therefore genuinely distinguish between a prompt and a delayed progenitor population.

---

## Slide 12 - Limitations (approx. 1:15 min)

### On the slide

- Limber approximation excludes $\ell<10$
- Gaussian Fisher forecast gives optimistic lower bounds
- FRB $n(z)$ and bias are model assumptions
- Survey geometry is simplified to $f_\mathrm{sky}$
- Residual cross-shot noise is neglected

### Visual

- Do not introduce another result plot
- Instead, use five restrained icons or a simple “assumption → possible effect” diagram

### Speaker notes

The forecast relies on several simplifications. First, I use the Limber approximation and therefore start at $\ell=10$. However, the largest angular scales may be particularly sensitive to differences between the radial models.

Second, the Fisher method assumes a Gaussian likelihood and Gaussian covariance. Non-linear structure formation and potentially non-Gaussian posterior shapes are not fully captured, so the reported uncertainties should be regarded as optimistic lower bounds.

Third, the FRB redshift distribution and the fiducial bias parameters are model assumptions rather than direct measurements. Survey geometry is also represented only through the factor $f_\mathrm{sky}$; a real analysis would require a mask or pseudo-$C_\ell$ treatment. Finally, a small cross-shot-noise term may arise if FRB host galaxies are themselves included in the KiDS catalogue. This contribution was neglected because the source densities differ so strongly.

---

## Slide 13 - Conclusion (approx. 1:00 min)

### On the slide

1. FRB auto-correlation is strongly limited by shot noise.
2. Tomographic galaxy cross-correlation recovers bias information.
3. KiDS improves the FoM by factors of 61-449, but cannot yet separate the models.
4. An LSST-like survey can reach the required precision.

**Take-home message:** FRB environments can be studied statistically without localising every individual source.

### Visual

- Reuse a simplified version of the orange KiDS contours or the KiDS-versus-LSST figure
- Alternatively, show one clear schematic: **FRBs + galaxy tomography → FRB progenitors**

### Speaker notes

To conclude, my thesis demonstrates three main points. First, the auto-correlation of current or near-future FRB samples is strongly limited by shot noise. Second, cross-correlation with a dense and tomographically divided galaxy sample recovers a substantial amount of the clustering information. With KiDS, the Figure of Merit improves by factors between 61 and 449, although the limited survey area is not yet sufficient to distinguish the two assumed progenitor models.

Third, the LSST forecast shows that the next generation of wide-area surveys can reach the required precision. The main take-home message is therefore that we do not need to localise every Fast Radio Burst individually to learn about its typical environment and origin. Its statistical connection to the large-scale galaxy distribution already provides an independent and promising route. Thank you for your attention.

---

## Optional Backup Slides

These slides are not part of the regular 15-to-20-minute presentation but can be prepared for questions.

### Backup A - Fiducial Cosmology

- $H_0=67.36\,\mathrm{km\,s^{-1}\,Mpc^{-1}}$
- $\Omega_{m,0}=0.3153$
- $\sigma_8=0.8111$
- $n_s=0.9649$
- Figure: `programming/frb-cosmology/plots/power_spectrum/Pk_nonlinear.pdf`

### Backup B - Complete Results Table

| Population | Survey | $\sigma_{b_0}$ FRB | $\sigma_{b_0}$ FRB×KiDS | $\sigma_\delta$ FRB | $\sigma_\delta$ FRB×KiDS | FoM gain |
|---|---:|---:|---:|---:|---:|---:|
| Magnetar | Deep | 23.48 | 1.27 | 31.07 | 1.88 | 60.7 |
| Magnetar | Shallow | 91.32 | 1.91 | 190.60 | 3.76 | 448.7 |
| Neutron star | Deep | 33.04 | 1.70 | 32.35 | 1.77 | 72.1 |
| Neutron star | Shallow | 101.0 | 2.42 | 153.00 | 3.41 | 348.3 |

### Backup C - Possible Methodological Extensions

- Measured rather than parameterised FRB redshift distributions
- Full likelihood sampling instead of a local Fisher approximation
- Non-Gaussian covariance
- Scale-dependent halo-bias model
- Real survey masks with pseudo-$C_\ell$ methods

---

## Timing Overview

| Slide | Topic | Time |
|---:|---|---:|
| 1 | Title and research question | 0:45 |
| 2 | Motivation | 1:15 |
| 3 | Progenitor models | 1:25 |
| 4 | Cross-correlation | 1:25 |
| 5 | Data | 1:20 |
| 6 | Numerical pipeline | 1:35 |
| 7 | FRB auto-correlation | 1:15 |
| 8 | Tomographic cross-signal | 1:20 |
| 9 | Fisher forecast | 1:15 |
| 10 | Main result | 1:40 |
| 11 | LSST outlook | 1:25 |
| 12 | Limitations | 1:15 |
| 13 | Conclusion | 1:00 |
|  | **Total** | **17:20** |
