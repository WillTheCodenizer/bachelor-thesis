"""
Statistical analysis and significance testing.
"""

import numpy as np
from scipy import stats


class StatisticalAnalyzer:
    """
    Compute statistical measures and hypothesis tests.
    """
    
    @staticmethod
    def compute_significance(counts_real, counts_random=None, method='poisson'):
        """
        Compute significance of excess/deficit.
        
        Parameters
        ----------
        counts_real : array
            Observed counts
        counts_random : array, optional
            Expected counts
        method : str
            'poisson' or 'gaussian'
        
        Returns
        -------
        significance : array
            Significance in sigma (standard deviations)
        p_value : array
            P-values
        """
        if counts_random is None:
            counts_random = np.mean(counts_real) * np.ones_like(counts_real)
        
        if method == 'poisson':
            # Poisson significance
            significance = (counts_real - counts_random) / np.sqrt(np.maximum(counts_random, 1))
            p_value = 1 - stats.chi2.cdf((counts_real - counts_random)**2 / np.maximum(counts_random, 1), 1)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return significance, p_value
    
    @staticmethod
    def correlation_significance_test(xi_values, xi_error, bin_centers):
        """
        Test if correlation is significantly different from zero.
        
        Parameters
        ----------
        xi_values : array
            Cross-correlation values
        xi_error : array
            Error on each bin
        bin_centers : array
            Bin centers for reference
        
        Returns
        -------
        significance : dict
            Dictionary with significance measures
        """
        # Chi-squared test
        chi2 = np.sum((xi_values / np.maximum(xi_error, 1e-10))**2)
        dof = len(xi_values)
        p_value_chi2 = 1 - stats.chi2.cdf(chi2, dof)
        
        # Integrated correlation (amplitude)
        xi_integrated = np.sum(xi_values * np.gradient(bin_centers, axis=0))
        
        # Detection significance (in sigma)
        xi_overall = np.mean(xi_values)
        xi_overall_error = np.mean(xi_error)
        detection_sigma = xi_overall / np.maximum(xi_overall_error, 1e-10)
        
        significance = {
            'chi2': chi2,
            'dof': dof,
            'p_value_chi2': p_value_chi2,
            'xi_integrated': xi_integrated,
            'xi_overall': xi_overall,
            'xi_overall_error': xi_overall_error,
            'detection_sigma': detection_sigma,
            'is_significant': p_value_chi2 < 0.05
        }
        
        return significance
    
    @staticmethod
    def ks_test_separations(sep_real, sep_random):
        """
        Kolmogorov-Smirnov test comparing two separation distributions.
        
        Parameters
        ----------
        sep_real : array
            Real separations
        sep_random : array
            Random separations
        
        Returns
        -------
        ks_stat : float
            KS statistic
        p_value : float
            P-value
        """
        ks_stat, p_value = stats.ks_2samp(sep_real, sep_random)
        return ks_stat, p_value
    
    @staticmethod
    def anderson_darling_test(sep_real, sep_random):
        """
        Anderson-Darling test for comparing distributions.
        
        Parameters
        ----------
        sep_real : array
            Real separations
        sep_random : array
            Random separations
        
        Returns
        -------
        ad_stat : float
            Anderson-Darling statistic
        """
        # Normalize
        combined = np.concatenate([sep_real, sep_random])
        sep_real_norm = (sep_real - np.mean(combined)) / np.std(combined)
        sep_random_norm = (sep_random - np.mean(combined)) / np.std(combined)
        
        # AD test
        ad_result = stats.anderson_ksamp([sep_real_norm, sep_random_norm])
        
        return ad_result.statistic, ad_result.critical_values, ad_result.significance_level


class ResultInterpreter:
    """
    Interpret cross-correlation results scientifically.
    """
    
    @staticmethod
    def interpret_correlation(significance_dict, xi_values, xi_error):
        """
        Generate scientific interpretation of results.
        
        Parameters
        ----------
        significance_dict : dict
            Output from correlation_significance_test
        xi_values : array
            Cross-correlation values
        xi_error : array
            Errors
        
        Returns
        -------
        interpretation : str
            Human-readable interpretation
        """
        p_val = significance_dict['p_value_chi2']
        det_sig = significance_dict['detection_sigma']
        xi_int = significance_dict['xi_integrated']
        xi_mean = significance_dict['xi_overall']
        
        lines = []
        lines.append("=" * 70)
        lines.append("CROSS-CORRELATION ANALYSIS RESULTS")
        lines.append("=" * 70)
        
        # Significance
        if p_val < 0.001:
            sig_str = "highly significant (p < 0.001, ≥ 3σ)"
        elif p_val < 0.01:
            sig_str = "very significant (p < 0.01, 2-3σ)"
        elif p_val < 0.05:
            sig_str = "significant (p < 0.05, ~2σ)"
        else:
            sig_str = "not significant (p ≥ 0.05, <2σ)"
        
        lines.append(f"\n1. STATISTICAL SIGNIFICANCE")
        lines.append(f"   - Detection significance: {det_sig:.2f} σ")
        lines.append(f"   - Chi-squared p-value: {p_val:.4f}")
        lines.append(f"   - Result: {sig_str}")
        
        # Amplitude
        if xi_mean > 0:
            excess_str = "EXCESS (clustering)"
        else:
            excess_str = "DEFICIT (anticlustering)"
        
        lines.append(f"\n2. CORRELATION AMPLITUDE")
        lines.append(f"   - Mean ξ(θ): {xi_mean:.4f} ± {significance_dict['xi_overall_error']:.4f}")
        lines.append(f"   - Integrated correlation: {xi_int:.4f}")
        lines.append(f"   - Type: {excess_str}")
        
        # Interpretation
        lines.append(f"\n3. INTERPRETATION")
        
        if p_val < 0.05 and xi_mean > 0:
            lines.append("   ✓ POSITIVE CORRELATION DETECTED")
            lines.append("   FRBs show CLUSTERING around galaxies.")
            lines.append("   This suggests FRBs may be associated with")
            lines.append("   dense regions of galaxy matter.")
        elif p_val < 0.05 and xi_mean < 0:
            lines.append("   ✗ NEGATIVE CORRELATION DETECTED")
            lines.append("   FRBs show ANTI-CLUSTERING around galaxies.")
            lines.append("   FRBs avoid regions of high galaxy density.")
        else:
            lines.append("   ~ NO SIGNIFICANT CORRELATION")
            lines.append("   FRBs and galaxies show random spatial distribution.")
            lines.append("   No evidence for environmental association.")
        
        lines.append(f"\n4. PHYSICAL IMPLICATIONS")
        if p_val < 0.05:
            if xi_mean > 0:
                lines.append("   - FRBs may originate from stellar systems")
                lines.append("   - Association with galaxy environments")
                lines.append("   - Possible connection to star formation")
            else:
                lines.append("   - FRBs avoid high-density environments")
                lines.append("   - Possible origin in isolated systems")
                lines.append("   - Intergalactic or galactic halo origin?")
        else:
            lines.append("   - No strong environmental dependence observed")
            lines.append("   - FRB origins likely independent of galaxy distribution")
            lines.append("   - Requires higher sensitivity to detect associations")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
    
    @staticmethod
    def print_summary(result_dict, significance_dict):
        """Print summary of analysis."""
        summary_lines = []
        summary_lines.append("\nANALYSIS SUMMARY")
        summary_lines.append("-" * 50)
        summary_lines.append(f"Number of bins: {len(result_dict['bin_centers'])}")
        summary_lines.append(f"Total real pairs: {np.sum(result_dict['counts_real']):.0f}")
        summary_lines.append(f"Total random pairs: {np.sum(result_dict['counts_random']):.0f}")
        summary_lines.append(f"Mean correlation: {result_dict['correlation'].mean():.4f}")
        summary_lines.append(f"Max correlation: {result_dict['correlation'].max():.4f}")
        summary_lines.append(f"Min correlation: {result_dict['correlation'].min():.4f}")
        
        return "\n".join(summary_lines)
