all: build/thesis.pdf


TeXOptions = --lualatex \
             --interaction=nonstopmode \
             --halt-on-error \
             --output-directory=build

build/thesis.pdf: FORCE | build
	latexmk $(TeXOptions) thesis.tex
	
preview: FORCE | build
	# continuous preview (open external viewer and auto-update on changes)
	TEXINPUTS=..: \
	BIBINPUTS=..: \
	max_print_line=1048576 \
	latexmk \
	  -pvc \
	  --lualatex \
	  --output-directory=build \
	  --interaction=nonstopmode \
	  --halt-on-error \
	thesis.tex

FORCE:

build:
	mkdir -p build/

clean:
	rm -rf build
