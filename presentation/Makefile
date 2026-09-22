all: build/thesis_presentation.pdf

texoptions = \
	     --lualatex \
	     --interaction=nonstopmode \
	     --halt-on-error \
	     --output-directory=build

build/thesis_presentation.pdf: FORCE | build
	latexmk $(texoptions) thesis_presentation.tex

preview: FORCE | build
	latexmk $(texoptions) thesis_presentation.tex
	open -a Preview build/thesis_presentation.pdf
	latexmk $(texoptions) -pvc -view=none thesis_presentation.tex

FORCE:

build:
	mkdir -p build

clean:
	rm -rf build
