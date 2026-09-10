LATEXMK := latexmk
OUTDIR := out
FLAGS := -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all proposal user-manual dev-manual clean distclean

all: proposal user-manual dev-manual

$(OUTDIR):
	mkdir -p $(OUTDIR)

proposal: | $(OUTDIR)
	cd docs && $(LATEXMK) $(FLAGS) -output-directory=../$(OUTDIR) proposal.tex

user-manual: | $(OUTDIR)
	cd docs/user-manual && $(LATEXMK) $(FLAGS) -output-directory=../../$(OUTDIR) user-manual.tex

dev-manual: | $(OUTDIR)
	cd docs/dev-manual && $(LATEXMK) $(FLAGS) -output-directory=../../$(OUTDIR) dev-manual.tex

clean:
	rm -f $(OUTDIR)/*.aux $(OUTDIR)/*.log $(OUTDIR)/*.fdb_latexmk \
	      $(OUTDIR)/*.fls $(OUTDIR)/*.out $(OUTDIR)/*.toc $(OUTDIR)/*.synctex.gz

distclean:
	rm -rf $(OUTDIR)
