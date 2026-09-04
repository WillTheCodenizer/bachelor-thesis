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

build/thesis.bcf:
	latexmk thesis.tex

FORCE:

clean:
	latexmk -C
