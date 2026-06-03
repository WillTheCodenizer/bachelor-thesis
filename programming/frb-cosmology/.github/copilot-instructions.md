## Copilot Instructions for FRB Cosmology Project

### Language

- All code, comments, variable names, function names, and documentation must be in English.
- English should be at a level appropriate for a non-native speaker writing a scientific thesis:
  clear, correct, and professional — but not overly formal or stiff.

### Code Style

- Every function must have a docstring explaining what it does, its parameters, and what it returns.
- Every non-obvious line or block of code must have an inline comment.
- Use descriptive variable names (no single letters except for standard physics notation like z, k, ell).
- Keep functions short and focused — one function does one thing.
- Avoid magic numbers: define constants at the top of each file or in a dedicated config file.

### Plots

All plots must follow scientific publication standards used in physics:

- Axis labels with units (e.g., "Wavenumber k [h/Mpc]")
- Legends where multiple lines are shown
- Log-log or log-linear axes where physically appropriate
- Clean layout using `tight_layout()` or `constrained_layout`
- Save plots as `.pdf` and `.png` to the `plots/` directory
- Use a consistent matplotlib style (e.g., a custom style file in `config/`)

### Project Structure

- Source code goes in `src/`
- Notebooks (if any) go in `notebooks/`
- Plots go in `plots/`
- Config/parameter files go in `config/`
- Tests (if any) go in `tests/`

### Dependencies

- Use Python with astropy, numpy, scipy, matplotlib, and hmf.
- Always import at the top of the file, grouped: standard library, then third-party.

### Units

- Always be explicit about units when using astropy quantities.
- When computing distances or power spectra, pay attention to h/Mpc vs 1/Mpc conventions.
- When using hmf, be aware that k is in units of h/Mpc and divide by h where needed.
