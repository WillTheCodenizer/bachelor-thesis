all: build/thesis.pdf

# Engine, output directory and biber are configured once in ./latexmkrc.
# Do not repeat --lualatex/--output-directory here, otherwise two different
# build configurations fight over the same aux/bcf files.

build/thesis.pdf: FORCE
	latexmk thesis.tex

preview: FORCE
	# continuous preview (open external viewer and auto-update on changes)
	latexmk -pvc thesis.tex

# Show the real biber error when the bibliography stays empty:
# with --debug biber does not swallow the libbtparse message on stderr.
bib-debug: build/thesis.bcf
	biber --debug --validate-datamodel build/thesis

# biber is a PAR-packed binary that unpacks its Perl libs into $TMPDIR.
# macOS prunes /var/folders/... periodically and leaves a half-empty cache
# behind, after which biber dies with "Unicode::UCD: failed to find
# unicore/version" and writes a 0-byte .bbl. This forces a clean re-extract.
bib-cache-reset:
	rm -rf "$${TMPDIR:-/tmp}"/par-*
	biber --version

build/thesis.bcf:
	latexmk thesis.tex

FORCE:

clean:
	latexmk -C
