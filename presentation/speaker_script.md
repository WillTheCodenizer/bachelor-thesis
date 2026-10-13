# Speaker Script: Bachelor Thesis Defense

**Probing Fast Radio Burst Environments: Cross-Correlating Deep and Shallow FRB Surveys with KiDS DR5**
Will Ruppert, October 27, 2026

Slide source: [thesis_presentation.tex](thesis_presentation.tex)

## How to use this script

- Every slide has three parts:
  - **On the slide**: a reminder of what the audience sees.
  - **Say**: the full spoken text. Spoken pace is roughly 130 words per minute.
  - **Key sentence**: the one sentence you must not forget.
- Lines in *[brackets]* are stage directions (point, pause, gesture). Do not read them aloud.
- Learn the key sentences and transitions by heart. The rest may be paraphrased freely.
- Target is about 29:10 min, which leaves under a minute of buffer for the 30 min slot.
- If you fall behind, shorten slides 8 and 15 to their key sentences. That saves about 1 min.

## Timing overview

| # | Slide | Duration | Cumulative |
|---|-------|---------:|-----------:|
| 1 | Title | 0:20 | 0:20 |
| 2 | Outline | 0:20 | 0:40 |
| 3 | Fast radio bursts | 1:30 | 2:10 |
| 4 | Dispersion measure | 1:00 | 3:10 |
| 5 | Progenitor channels | 1:45 | 4:55 |
| 6 | Idea and research question | 1:15 | 6:10 |
| 7 | Flat ΛCDM | 1:00 | 7:10 |
| 8 | Linear bias | 1:00 | 8:10 |
| 9 | Angular power spectrum | 1:30 | 9:40 |
| 10 | Cosmology and P(k) | 1:00 | 10:40 |
| 11 | FRB survey configurations | 1:15 | 11:55 |
| 12 | KiDS-Legacy | 1:15 | 13:10 |
| 13 | FRB bias models | 1:30 | 14:40 |
| 14 | FRB auto-correlation | 1:45 | 16:25 |
| 15 | Galaxy auto-spectra | 0:50 | 17:15 |
| 16 | Cross-correlation | 1:15 | 18:30 |
| 17 | Fisher formalism | 1:30 | 20:00 |
| 18 | Fisher contours | 1:30 | 21:30 |
| 19 | Constraints table | 1:45 | 23:15 |
| 20 | Progenitor discrimination (KiDS) | 1:15 | 24:30 |
| 21 | Limitations | 1:00 | 25:30 |
| 22 | Outlook: KiDS vs. LSST Y10 contours | 1:15 | 26:45 |
| 23 | Outlook: LSST progenitor discrimination | 1:00 | 27:45 |
| 24 | Conclusion | 1:15 | 29:00 |
| 25 | Thank you | 0:10 | 29:10 |

**Checkpoints:** By slide 9 you should be at about 9:30. By slide 17 at about 19:00 to 20:00. By slide 22 at no later than 26:30.

---

## Introduction

### Slide 1: Title (0:20, cumulative 0:20)

**On the slide:** Title, name, research groups, supervisors.

**Say:**
Good morning, and thank you for being here. My name is Will Ruppert, and today I will present my bachelor thesis on probing the environments of fast radio bursts by cross-correlating FRB surveys with the Kilo-Degree Survey. The thesis was supervised by Dr. Elsässer here in Dortmund and Professor Hildebrandt in Bochum.

### Slide 2: Outline (0:20, cumulative 0:40)

**On the slide:** Five sections.

**Say:**
The talk follows the structure of the thesis. I will start with the motivation and the physical background. Then I will explain the forecasting pipeline I developed. After that I will show the results of the Fisher forecast, and I will close with the conclusions and an outlook.

### Slide 3: Fast radio bursts (1:30, cumulative 2:10)

**On the slide:** FRB properties, sky map of known FRBs.

**Say:**
So what are fast radio bursts? FRBs are extremely bright radio pulses that last only a millisecond or less. Their peak flux densities range from about fifty millijansky up to a hundred jansky, and they have been detected from 110 megahertz up to 8 gigahertz.

To give you a feeling for the energetics: a single burst releases about as much energy as the Sun emits in three days. Yet by the time the signal reaches us, it is roughly a thousand times weaker than a mobile phone on the Moon would be. *[smile, short pause]* This tells us immediately that these sources must be very far away.

The first FRB, the Lorimer Burst, was published in 2007. For years, only a handful were known. That changed with the CHIME telescope. Its second catalog now contains more than four and a half thousand bursts from over three and a half thousand sources, including 83 repeating sources.

*[point at the sky map]* Here you can see the known FRBs in Galactic coordinates. The distribution is roughly isotropic. There is no concentration toward the Galactic plane, which already hints at an extragalactic population.

**Key sentence:** One burst carries the energy the Sun emits in three days, yet arrives a thousand times weaker than a phone on the Moon.

**Transition:** The strongest evidence for their distance comes from the dispersion measure.

### Slide 4: Dispersion measure (1:00, cumulative 3:10)

**On the slide:** DM equation, Milky Way vs. observed DM.

**Say:**
When a radio pulse travels through ionized gas, the low frequencies are delayed relative to the high frequencies. From this delay we obtain the dispersion measure, DM. Physically, it is the column density of free electrons along the line of sight.

*[point at the two blocks]* For a source inside the Milky Way, electron-density models predict at most about fifty parsec per cubic centimeter. Observed FRBs, however, often show a thousand or more.

This excess means FRBs are at cosmological distances. And that is the starting point of this thesis: if FRBs are cosmological, they must trace the large-scale structure of the Universe.

**Key sentence:** FRBs are cosmological, so they trace the large-scale structure.

**Transition:** What actually produces these bursts is still an open question.

### Slide 5: Progenitor channels (1:45, cumulative 4:55)

**On the slide:** Two blocks: young magnetars (prompt) vs. neutron star mergers (delayed).

**Say:**
Some FRB sources repeat. Repetition rules out a purely cataclysmic origin, at least for those sources. Among the many proposed models, compact objects like neutron stars and magnetars are the most promising candidates. In this thesis I compare two channels.

*[left block]* The first channel is young magnetars. These are neutron stars with extreme magnetic fields. They are born in core-collapse supernovae, only a few to a few tens of millions of years after star formation. Their formation rate should therefore follow the cosmic star-formation history. The strongest evidence came in 2020, when an FRB-like burst was detected from the Galactic magnetar SGR 1935+2154.

*[right block]* The second channel is delayed. Some FRBs sit in massive galaxies with little star formation and at large offsets from the host center. These environments resemble the hosts of short gamma-ray bursts, which come from neutron star mergers. One FRB was even localized to a globular cluster, an extremely old environment. Here the delay times extend up to several billion years, so this population evolves only slowly with redshift.

*[point at bottom line]* In my work, the difference between the two channels is encoded entirely in a redshift-dependent bias. I will come back to this.

**Key sentence:** Prompt magnetars follow star formation; delayed neutron stars live in old, massive hosts.

**Transition:** So how can we tell these two scenarios apart without localizing every single burst?

### Slide 6: Idea and research question (1:15, cumulative 6:10)

**On the slide:** Bullet chain from clustering to cross-correlation; research question block.

**Say:**
Identifying the host of a single FRB requires arcsecond localizations, which are still rare. But we do not need to look at single bursts. Because FRBs trace the large-scale structure, their angular clustering on the sky tells us how strongly their hosts are biased relative to dark matter. And this host bias depends on the progenitor channel.

The problem is that FRB samples are sparse, so any clustering measurement is dominated by shot noise. The solution I study is to cross-correlate the FRBs with a dense photometric galaxy sample, here KiDS-Legacy.

*[point at block]* This leads to the research question: How well can the FRB host bias be constrained by this cross-correlation, and can we distinguish a prompt magnetar origin from a delayed neutron-star origin? To answer it, I consider a shallow, CHIME-like survey and a deep, SKA-like survey, each combined with both progenitor models, and I propagate everything into a Fisher forecast.

**Key sentence:** Can cross-correlating FRBs with KiDS constrain the host bias well enough to distinguish prompt from delayed progenitors?

**Transition:** Before the pipeline, a brief look at the theoretical framework.

---

## Theoretical Background

### Slide 7: Flat ΛCDM (1:00, cumulative 7:10)

**On the slide:** FLRW metric, redshift, E(z), comoving distance.

**Say:**
I work in a spatially flat ΛCDM universe. The geometry is described by the FLRW metric with the scale factor a of t, and the redshift is directly related to the scale factor.

At late times, radiation can be neglected, and the expansion rate depends only on the matter and dark energy densities. *[point at chi]* Integrating the inverse expansion rate gives the comoving distance χ. This is the quantity we need, because it maps redshift distributions onto the line of sight. And its derivative, H over c, converts all radial kernels from redshift to comoving distance.

**Key sentence:** The comoving distance maps redshift distributions onto the line of sight.

**Transition:** On top of this smooth background we need the structure.

### Slide 8: Linear bias (1:00, cumulative 8:10)

**On the slide:** Density contrast, growth factor, power spectrum, linear bias block.

**Say:**
Structure is described by the density contrast δ, the relative deviation from the mean density. As long as it is small, all modes grow with the same linear growth factor D plus. The statistics of the field are summarized by the power spectrum P of k.

*[point at block]* The central concept of this thesis is the linear bias. Galaxies, and also FRB hosts, form in the peaks of the matter field, so their density contrast is the matter contrast times a bias factor b. A bias above one means stronger clustering than the matter. So the bias of the FRB hosts tells us in which halos FRBs live, and that is exactly what differs between the progenitor channels.

**Key sentence:** The bias tells us which halos host the FRBs.

**Transition:** We observe positions on the sky, though, so we need to project.

### Slide 9: Angular power spectrum (1:30, cumulative 9:40)

**On the slide:** Limber equation, P_AB, weight functions, key point block.

**Say:**
We do not observe the three-dimensional field directly, only projected positions on the sky. The relevant statistic is therefore the angular power spectrum C ell. For two tracers A and B, I use the Limber approximation, which is valid for multipoles above about ten. The angular spectrum is then a line-of-sight integral over the two radial weight functions, times the 3D power spectrum evaluated at k equals ell plus one half over χ.

The tracer power spectrum is just the matter power spectrum times the two biases. The weight functions are bias times redshift distribution: for the FRBs with the redshift-dependent bias, for each galaxy bin with a constant galaxy bias.

*[point at block]* The key point is the following. The cross-spectrum only receives contributions where the FRB kernel and a galaxy kernel overlap. Each tomographic galaxy bin therefore probes the FRB bias in a different redshift range, and this is what gives us leverage on the redshift evolution of the bias.

**Key sentence:** Each galaxy bin probes the FRB bias at a different redshift.

**Transition:** Now let me show how I turned this into a numerical pipeline.

---

## Methodology

### Slide 10: Cosmology and P(k) (1:00, cumulative 10:40)

**On the slide:** Planck 2018 table, grids, nonlinear P(k,z) plot.

**Say:**
The pipeline is written in Python, using NumPy, SciPy, astropy, and the hmf package. All cosmological parameters are fixed to the Planck 2018 baseline values shown in the table.

Redshift-dependent quantities are evaluated on a grid of a thousand logarithmically spaced points between z equals 0.01 and 5. Multipoles run from 10, the Limber limit, up to 1000, where the nonlinear prescription is still reliable.

*[point at plot]* Here you see the nonlinear matter power spectrum at six redshifts. The amplitude drops toward high redshift because structure has had less time to grow. This drop will appear again in the angular spectra.

**Key sentence:** Planck 2018 cosmology, nonlinear P(k), ell from 10 to 1000.

**Transition:** Next, where are the FRBs along the line of sight?

### Slide 11: FRB survey configurations (1:15, cumulative 11:55)

**On the slide:** n(z) ∝ z² exp(−αz), survey table, n(z) plot.

**Say:**
Since we do not have measured redshifts for the FRB population, the redshift distribution is modeled. Following Reischke and collaborators, it is z squared times an exponential cutoff. The z squared reflects the growing volume, and the exponential reflects the decreasing detectability at large distances. The parameter α sets the depth.

I consider two configurations. The shallow one has α equals 3.5 and five thousand bursts, which is roughly what CHIME has today. The deep one has α equals 2 and fifty thousand bursts, representative of the Square Kilometre Array. Both cover 90 percent of the sky.

*[point at plot]* You can see that the deep distribution extends much further. About 40 percent of its bursts lie above redshift 1.5. Keep that number in mind; it will matter later.

**Key sentence:** Shallow is CHIME-like, deep is SKA-like with ten times more bursts and 40 percent above z = 1.5.

**Transition:** The second ingredient is the galaxy sample.

### Slide 12: KiDS-Legacy (1:15, cumulative 13:10)

**On the slide:** KiDS facts, galaxy bias formula, six n_i(z).

**Say:**
For the galaxies I use KiDS-Legacy, the fifth and final data release of the Kilo-Degree Survey. It was observed with the 2.6-meter VLT Survey Telescope on Paranal and covers 1347 square degrees, which is a sky fraction of only about three percent. Together with VIKING it provides nine-band photometry down to a limiting magnitude of 24.8 in the r band. The photometric redshifts are calibrated with about 126 thousand spectra.

*[point at plot]* The sample is divided into six tomographic bins, shown here, with mean redshifts from about 0.3 to 1.2.

For the galaxy bias I use a constant-clustering model: 0.95 divided by the growth factor at the mean redshift of the bin. This gives values from about 1.1 in the first bin to 1.7 in the last bin.

**Key sentence:** Six well-calibrated tomographic bins, but on only three percent of the sky.

**Transition:** Now to the most important model ingredient: the FRB bias.

### Slide 13: FRB bias models (1:30, cumulative 14:40)

**On the slide:** b(z) = b0 (1+z)^δ, fiducial table, bias plot.

**Say:**
The FRB host bias is modeled as a power law: an amplitude b zero at redshift zero, times one plus z to the power δ. These two numbers, b zero and δ, are the parameters I want to constrain.

*[point at table]* For magnetars I choose a low amplitude of 1.0 and a strong evolution of 0.8. Young magnetars sit in star-forming galaxies, which are only mildly biased today, and their bias grows with redshift like that of star-forming tracers.

For delayed neutron stars I choose a higher amplitude of 1.5, because their hosts are massive and old, but a weak evolution of only 0.2.

*[point at plot]* As a result, the two curves cross at about redshift one. Below that, the neutron-star model is more biased. Above it, the magnetar model is more biased. So the difference between the models lies mainly in how the bias evolves, and that is exactly what tomography can access.

**Key sentence:** The models differ in amplitude and evolution; the curves cross near z = 1.

**Transition:** With all ingredients in place, let me show the resulting spectra, starting with FRBs alone.

### Slide 14: FRB auto-correlation (1:45, cumulative 16:25)

**On the slide:** Shot noise equations, two FRB auto-spectrum plots, alert line.

**Say:**
FRBs are discrete points, so their auto-spectrum contains Poissonian shot noise. Shot noise is simply one over the number density per steradian, and for FRBs the number density is the total number of bursts divided by the observed solid angle.

*[point at left plot]* On the left you see the magnetar auto-spectrum for the shallow survey. The blue line is the clustering signal. The dashed orange line is signal plus shot noise. The shot noise lies about three orders of magnitude above the signal, at every multipole. In other words, with five thousand bursts, the FRB clustering is completely buried in noise.

*[point at right plot]* On the right I compare the signal of the two surveys. Interestingly, the deep survey has the lower amplitude. There are two reasons. Its bursts are at higher redshift, where structure is less evolved. And the one over χ squared factor in the Limber integral suppresses distant sources. The neutron-star model behaves the same way qualitatively.

**Key sentence:** For the shallow survey, shot noise exceeds the FRB signal by three orders of magnitude at all scales.

**Transition:** Galaxies are a completely different story.

### Slide 15: Galaxy auto-spectra (0:50, cumulative 17:15)

**On the slide:** Galaxy C_ell for six bins; bin 5 with shot noise.

**Say:**
*[left plot]* These are the galaxy auto-spectra for the six bins. The amplitude decreases toward higher bins, even though the bias increases. This is because the high-redshift bins are radially broader, and again the χ to the minus two factor suppresses distant structure.

*[right plot]* For bin five you can see that the signal is well above the shot noise and only approaches it at the highest multipoles. So the galaxies provide a high signal-to-noise tracer of the same structure.

**Key sentence:** The galaxies are a dense, high signal-to-noise tracer.

**Transition:** Now we combine the two.

### Slide 16: Cross-correlation (1:15, cumulative 18:30)

**On the slide:** Cross-spectra for shallow vs. deep in all six bins.

**Say:**
For every combination of two progenitor models, two surveys, and six bins, I computed the cross-spectrum. That makes 24 spectra in total.

The crucial point is that the FRB and galaxy samples are independent. Their cross-spectrum therefore has no shot-noise term. The noise only enters through the auto-spectra in the covariance, and there the dense galaxy sample helps a lot.

*[point at plot]* Here you see the magnetar cross-spectra for all six bins. Solid lines are shallow, dashed lines are deep. The shallow survey gives the stronger signal in every bin, even in bin six. The reason is that the Limber kernel weights low redshifts more strongly, and bin six is broad enough to receive substantial weight below the redshift where the two FRB distributions cross.

**Key sentence:** The cross-spectrum has no shot noise, and six bins give six different redshift weightings.

**Transition:** How much information about b zero and δ is in these spectra? That is what the Fisher matrix tells us.

---

## Results

### Slide 17: Fisher formalism (1:30, cumulative 20:00)

**On the slide:** Fisher equation, finite differences, Cov, σ, FoM, sky fractions block.

**Say:**
Assuming a Gaussian likelihood around the fiducial model, the Fisher matrix gives the expected parameter covariance. Here C ell is the full matrix of all auto- and cross-spectra, with the shot noise on the auto-spectra. The derivatives with respect to b zero and δ are computed with central finite differences, using a step of one percent of the fiducial value. All cosmological parameters are kept fixed.

Inverting the Fisher matrix gives the covariance. The square roots of its diagonal are the marginalized uncertainties. To compress the two-dimensional constraint into one number, I use the figure of merit, one over the square root of the determinant. It is inversely proportional to the area of the confidence ellipse, so larger is better.

*[point at block]* One important detail: the FRB-only forecast uses 90 percent of the sky. The joint forecast is limited to the KiDS footprint, three percent of the sky. That is roughly 28 times less area. So the comparison is, if anything, conservative for the joint analysis.

**Key sentence:** The joint forecast uses about 28 times less sky area than the FRB-only forecast.

**Transition:** Here are the results.

### Slide 18: Fisher contours (1:30, cumulative 21:30)

**On the slide:** Four panels of b0–δ contours (green FRB-only, blue joint).

**Say:**
These are the forecast contours in the b zero–δ plane for all four combinations. Top row: magnetars. Bottom row: neutron stars. Left: deep survey. Right: shallow survey.

*[point at green lines in panel a]* The green lines are the one- and two-sigma contours from the FRB auto-correlation alone. They are so wide that they extend far beyond the plotted range in every panel. The FRB-only analysis essentially constrains nothing.

*[point at blue ellipse]* The blue ellipses show the joint analysis with the six KiDS bins. They are closed, compact, and centered on the fiducial value.

Note also the orientation: b zero and δ are anti-correlated. A higher amplitude can be partly compensated by a weaker evolution. The tomographic bins help to break this degeneracy.

**Key sentence:** Without galaxies, nothing is constrained; with galaxies, we get closed contours.

**Transition:** Let me quantify this.

### Slide 19: Constraints table (1:45, cumulative 23:15)

**On the slide:** Table of σ and FoM; two blocks.

**Say:**
The table lists the marginalized uncertainties and figures of merit. FRB-only, the uncertainty on b zero ranges from 21 to 92, and on δ from 28 to 172. That is one to two orders of magnitude larger than the parameters themselves.

With the galaxies, σ of b zero drops to between 1.3 and 2.4, and σ of δ to between 1.9 and 3.7.

*[left block]* So the individual uncertainties shrink by factors of 15 to 46, and the figure of merit increases by factors of 51 to 377, despite the 28 times smaller area. The joint analysis is not a small refinement. It is what makes a measurement possible in the first place.

*[right block]* Comparing deep and shallow surveys shows an interesting effect. FRB-only, the deep survey improves σ of b zero by a factor of three to four, as expected from ten times more bursts. In the joint analysis, the gain is only about 1.4 to 1.5. The reason is radial overlap. About 40 percent of the deep bursts lie above redshift 1.5, beyond most of the KiDS galaxies, so they add little to the cross-correlation. This is also why the relative gain is largest for the shallow survey.

**Key sentence:** Uncertainties shrink by 15 to 46 times, and the figure of merit grows by 51 to 377 times.

**Transition:** But can we tell the two progenitors apart?

### Slide 20: Progenitor discrimination with KiDS (1:15, cumulative 24:30)

**On the slide:** Overlap of magnetar (blue) and neutron-star (orange) contours, deep and shallow.

**Say:**
Here I overlay the joint contours of both models, magnetars in blue and neutron stars in orange, for the deep survey on the left and the shallow survey on the right.

*[point at the two crosses]* The fiducial values differ by 0.5 in b zero and 0.6 in δ. This separation lies well within the one-sigma contours, and the ellipses overlap almost entirely.

In relative terms, both models are constrained similarly well. In the deep configuration, σ of b zero over b zero is 1.3 for magnetars and 1.1 for neutron stars. So the cross-correlation with KiDS improves the measurement by about two orders of magnitude in the figure of merit, but it does not yet reach the precision needed to distinguish a prompt from a delayed origin.

**Key sentence:** With KiDS, the two progenitor models still overlap within one sigma.

**Transition:** Before the outlook, let me be clear about what these numbers assume.

---

## Conclusion & Outlook

### Slide 21: Limitations (1:00, cumulative 25:30)

**On the slide:** Five limitations.

**Say:**
There are several simplifying assumptions. First, the Limber approximation restricts the analysis to multipoles above ten, so the largest scales are excluded. Second, the Gaussian likelihood and Gaussian covariance neglect non-Gaussian contributions from nonlinear growth, so the uncertainties are optimistic lower bounds. Third, the power-law bias is adequate where the constraints come from, below redshift about 1.5. At higher redshift the bias is expected to evolve more strongly and to depend on halo mass. Fourth, the FRB redshift distribution and the fiducial bias values are assumptions, not measurements. And finally, the survey geometry enters only through the sky fraction. A real analysis would need a full pseudo-spectrum treatment with the actual masks.

**Key sentence:** The forecast uncertainties are optimistic lower bounds.

**Transition:** The most direct improvement, however, is clear from the Fisher matrix itself.

### Slide 22: Outlook, KiDS vs. LSST Y10 contours (1:15, cumulative 26:45)

**On the slide:** Four panels of b0–δ contours (blue KiDS, red LSST Y10), same layout as slide 18; LSST facts.

**Say:**
The Fisher information scales linearly with the sky fraction. So the obvious step is a wider galaxy survey. The Legacy Survey of Space and Time at the Rubin Observatory will cover about 18,000 square degrees, roughly 13 times the KiDS area. I ran exactly the same pipeline with the ten-bin year-ten lens sample of the LSST DESC, changing nothing else.

*[point at panel a]* The layout is the same as before: magnetars on top, neutron stars below, deep on the left, shallow on the right. Blue are the KiDS contours you have already seen, red is LSST.

*[point at red ellipse]* In every panel the LSST ellipse is much smaller. The figure of merit improves by a factor of 9 to 12. For deep magnetars, σ of b zero drops from 1.26 to 0.42. The gain is slightly below the factor 13 from the area alone, because the LSST lens bins end at about redshift 1.2, whereas the last KiDS bin reaches beyond 1.5.

**Key sentence:** LSST improves the figure of merit by 9 to 12 times, almost the full area gain.

**Transition:** The decisive question is again: can we now separate the two progenitor models?

### Slide 23: Outlook, LSST progenitor discrimination (1:00, cumulative 27:45)

**On the slide:** LSST overlap contours of magnetar and neutron-star models (deep, shallow).

**Say:**
This is the LSST counterpart of the overlap plot I showed for KiDS. Magnetars in blue, neutron stars in orange.

*[point at left plot]* In the deep configuration, the neutron-star fiducial now lies just outside the one-sigma contour of the magnetar model, although both are still within two sigma. *[point at right plot]* In the shallow configuration, the models still overlap at one sigma.

So an LSST-like galaxy sample would substantially improve the prospects of distinguishing a prompt from a delayed origin, though not yet decisively. Further extensions would be using the measured redshift distribution of the second CHIME catalog, full likelihood sampling, and a halo-model bias.

**Key sentence:** With LSST, the separation of the two models becomes comparable to the uncertainties.

**Transition:** Let me summarize.

### Slide 24: Conclusion (1:15, cumulative 29:00)

**On the slide:** Five numbered results; take-home block.

**Say:**
In this thesis I developed a complete forecasting pipeline, from the nonlinear matter power spectrum to auto- and cross-spectra of FRBs and six KiDS-Legacy bins, and finally to a Fisher forecast for the FRB host bias.

The FRB auto-correlation alone is shot-noise dominated and does not constrain the bias. Cross-correlating with KiDS reduces the uncertainties by factors of 15 to 46 and increases the figure of merit by 51 to 377, despite a 28 times smaller sky area. With the current KiDS footprint, the two progenitor channels cannot yet be distinguished. With LSST, the separation becomes comparable to the uncertainties.

*[point at block]* So the take-home message is: FRB-galaxy cross-correlation is a promising probe of FRB progenitors, and next-generation galaxy surveys can make it decisive.

**Key sentence:** FRB × galaxy cross-correlation is a promising probe of FRB progenitors.

### Slide 25: Thank you (0:10, cumulative 29:10)

**Say:**
Thank you very much for your attention. I am happy to take your questions.

---

## Backup slides (only during questions)

| Backup | Use it when asked about |
|--------|------------------------|
| Fiducial cosmology and KiDS bins | exact parameter values, galaxy bias per bin |
| Full-sky spectrum and Limber | validity of Limber, choice of ell range |
| KiDS versus LSST Y10 in numbers | exact LSST σ and FoM values per configuration |
| LSST Y10 lens sample | LSST redshift coverage, why the gain is below 13 |
| FRB vs. mobile phone on the Moon | the "phone on the Moon" claim |
| Further extensions | "What would you do next?" |

---

## Anticipated questions and prepared answers

**Q1: Why is the cross-spectrum free of shot noise?**
Shot noise arises when a point is correlated with itself. FRBs and galaxies are different, independent samples, so no object appears in both catalogs, and the Poisson term vanishes in the cross-spectrum. The noise still enters the Fisher matrix through the auto-spectra in the covariance. Strictly, an FRB host that is also in the KiDS catalog would create a small shared term, but this is negligible for these number densities.

**Q2: Why do the FRB-only and joint forecasts use different sky fractions? Is the comparison fair?**
The FRB survey covers 90 percent of the sky, but the cross-correlation is only possible where both surveys overlap, which is the KiDS footprint of 3.3 percent. If anything, this makes the comparison conservative for the joint analysis. It wins despite about 28 times less area.

**Q3: Why does the shallow survey gain more from the galaxies than the deep survey?**
The shallow FRBs sit mostly below redshift 1.5, exactly where the KiDS galaxies are, so the radial overlap is large. About 40 percent of the deep bursts lie above 1.5, beyond most KiDS galaxies. In addition, the FRB-only baseline for the shallow survey is much worse, so the relative gain is larger.

**Q4: Why does the deep survey have a lower auto-spectrum amplitude?**
Two reasons. Its bursts are at higher redshift, where the matter power spectrum has a lower amplitude because structure is less evolved. And the χ to the minus two factor in the Limber integral, together with the broader kernel, dilutes the projected signal.

**Q5: When is the Limber approximation valid, and why ell from 10 to 1000?**
The spherical Bessel functions peak sharply at k χ ≈ ell + 1/2. When the radial kernels vary slowly compared to that oscillation, only this k contributes. This holds for ell of order ten and above, and for broad kernels like ours. The upper limit of 1000 keeps us on scales where the nonlinear power-spectrum prescription is reliable. *[Backup: Limber]*

**Q6: Why are the uncertainties "optimistic lower bounds"?**
The Fisher matrix gives the Cramér–Rao bound for a Gaussian likelihood. I assumed a purely Gaussian covariance, which neglects non-Gaussian contributions such as the connected trispectrum and super-sample covariance. I also ignored masks, systematics, and uncertainties in n(z). All of these would widen the contours.

**Q7: Is a power-law bias b0 (1+z)^δ justified?**
It is a common parametrization that describes the observed low-redshift FRB hosts well. Pan and collaborators fit similar forms to multiwavelength tracers. At high redshift the bias of halos grows faster and depends on halo mass, as in Tinker et al. Since the constraints are dominated by redshifts below about 1.5, the power law is adequate here. The magnetar model remains reasonable to higher redshift than the neutron-star model, whose evolution is likely too flat beyond z ≈ 1 to 1.5.

**Q8: Where do the fiducial bias values come from?**
They are model assumptions that represent the two scenarios: a star-formation tracer with low amplitude and strong evolution, and an old, massive-galaxy tracer with high amplitude and weak evolution. They are not measured values. That is listed as a limitation.

**Q9: Why are b0 and δ anti-correlated?**
The spectra are mainly sensitive to the bias at some effective redshift. Increasing b0 and decreasing δ can leave b0 (1+z_eff)^δ almost unchanged. The tomographic bins sample different effective redshifts and therefore partly break this degeneracy, which is why the joint contours are both smaller and less elongated.

**Q10: Why does LSST improve the FoM by only 9 to 12, not 13?**
The Fisher matrix, and the FoM for this case, scale linearly with the sky fraction, so the area alone would give a factor of 13. But the LSST lens bins end at redshift about 1.2, whereas the sixth KiDS bin extends beyond 1.5 into the high-redshift tail. Per unit area, LSST lenses are therefore slightly less informative, especially for the deep FRB survey.

**Q11: How significant is the LSST separation in the deep case?**
For two parameters, the one-sigma region corresponds to Δχ² = 2.30. Evaluated at the neutron-star fiducial, the magnetar Fisher matrix gives Δχ² ≈ 2.8, just outside one sigma. The other direction gives about 0.95, still inside. In the shallow case the values are about 1.7 and 0.5. So it is a hint, not a discrimination.

**Q12: Why did you fix the cosmological parameters?**
The focus is the FRB host bias. Cosmology is very well constrained by Planck and other probes compared to the bias uncertainties here. Marginalizing over cosmology would widen the contours slightly, especially through the degeneracy between bias and σ8. That is a natural extension.

**Q13: How is the galaxy bias chosen, and what happens if it is wrong?**
I use 0.95 over D+(⟨z⟩), a standard constant-clustering prescription in photometric forecasts such as Johnston et al. 2025. In a real analysis, the galaxy bias would be measured from the galaxy auto-spectra themselves, which have high signal-to-noise. The galaxy auto-spectra in the data vector already provide that information.

**Q14: How does the measured CHIME catalog fit in?**
The second CHIME/FRB catalog already contains a sample of the size of my shallow configuration. Using its measured selection function and redshift information instead of the parametric n(z) would be the next step toward an actual measurement. Rafiei-Ravandi et al. have already detected an FRB-galaxy cross-correlation with the first catalog.

**Q15: Why is the step size one percent, and did you check stability?**
One percent is small enough for a linear derivative but large enough to avoid numerical noise from the spectra. The spectra are smooth functions of b0 and δ. For b0, C_ell is even exactly quadratic in the FRB-only case and linear in the cross-spectra, so the central difference is very accurate.

**Q16: What is the DM used for in your analysis?**
In this thesis, DM is only the argument for the cosmological distance of FRBs. I use angular positions only. Combining clustering with DM information, for example DM-galaxy cross-correlations, is a possible extension.

**Q17: Where does the "phone on the Moon" number come from?**
A GSM phone transmits 2 watts in a 200 kilohertz channel. Emitted isotropically from the Moon, that gives about 540 jansky on Earth. A typical FRB has about half a jansky, so the ratio is about a thousand. It is an order-of-magnitude illustration. *[Backup: phone]*

## General tips for the defense

- Speak slowly at the key numbers (15 to 46, 51 to 377, 28 times, within one sigma). Pause briefly after each.
- Point at the plot before explaining it. Say what the axes and colors are first, then the message.
- If you do not know an answer, say what you do know and how you would find out. Do not guess numbers.
- Keep water nearby, and look at the examiners, not at the screen.

Die Folien und das Sprechskript sind fertig. Kompiliert habe ich die Präsentation noch nicht, weil auf diesem Windows-Rechner kein LaTeX installiert ist. Bitte auf deinem Mac in presentation einmal make ausführen; das PDF landet in build/.

Folien: thesis_presentation.tex hat 24 Hauptfolien und 6 Backup-Folien. Die Backup-Folien zählen nicht in die Gesamtzahl der Folien. Die Abschnitte folgen den Kapiteln der Thesis.
Grafiken: Es werden nur Abbildungen verwendet, die in der Thesis eingebunden sind. Auskommentierte Abbildungen sind nicht dabei. Die Pfade sind dieselben wie in der Thesis.
Logo: Ich habe rub_logo.png nach logos kopiert, weil der Ordnername „writing thesis“ ein Leerzeichen enthält.
Zahlen: Alle Werte stammen aus den aktuellen Tabellen der Thesis (Verbesserung der Unsicherheiten 15–46×, FoM 51–377×, LSST 9–12×).
Sprechskript: speaker_script.md ist auf Englisch und auf etwa 28:40 min angelegt. Es enthält:
eine Zeittabelle mit Kontrollpunkten,
pro Folie den vollständigen Sprechtext, Regieanweisungen, einen Kernsatz zum Auswendiglernen und eine Überleitung,
eine Übersicht, welche Backup-Folie zu welcher Frage passt,
17 mögliche Prüfungsfragen mit vorbereiteten Antworten.
Beim ersten Kompilieren bitte vor allem darauf achten:

Platz: Ob die vollen Folien in die Höhe passen, besonders Folie 5 (Progenitoren), 17 (Fisher), 19 (Tabelle) und 22 (LSST). Falls etwas überläuft, reicht meist eine etwas kleinere Bildhöhe.
Titelfolie: Der lange Titel bricht über mehrere Zeilen um. Die Schrift dafür habe ich schon auf \LARGE verkleinert.
Antwort 11 in den Prüfungsfragen nennt Δχ²-Werte zur LSST-Trennung (2.8 bzw. 0.95; shallow 1.7 bzw. 0.5). Diese Zahlen stehen nicht in der Thesis, sondern stammen aus meinen Notizen zu einer früheren Pipeline-Auswertung. Prüf sie bitte vor der Verteidigung nach.

Lies das Skript einmal laut mit Stoppuhr. Wenn du über 29 min liegst, kürze zuerst Folie 8 und 15 auf ihren Kernsatz.