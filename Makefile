SKILL_NAME := quote-forensics
DIST       := dist
BUNDLE     := $(DIST)/$(SKILL_NAME).skill
PY         := python3

# Files that go into the distributable bundle. Generated artefacts and repo
# scaffolding (CI, Makefile, requirements) are deliberately excluded.
BUNDLE_PATHS := SKILL.md README.md LICENSE .gitignore \
                references schemas scripts examples

.PHONY: all bundle test clean install-deps

all: bundle

install-deps:
	$(PY) -m pip install -r requirements.txt

## Rebuild the .skill archive from the working tree. The tree is the source of
## truth; the bundle is a build artefact and is never edited by hand.
bundle: clean-bundle
	@mkdir -p $(DIST)/$(SKILL_NAME)
	@for p in $(BUNDLE_PATHS); do cp -R $$p $(DIST)/$(SKILL_NAME)/; done
	@find $(DIST)/$(SKILL_NAME) -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@find $(DIST)/$(SKILL_NAME) -name '*.pyc' -delete 2>/dev/null || true
	@cd $(DIST) && zip -qr $(SKILL_NAME).skill $(SKILL_NAME)
	@rm -rf $(DIST)/$(SKILL_NAME)
	@echo "built $(BUNDLE)"
	@unzip -l $(BUNDLE) | tail -3

## End-to-end run of the four-stage pipeline against the worked example.
test:
	$(PY) scripts/normalize.py  examples/sample_quotes.json        -o examples/normalized.json
	$(PY) scripts/variance.py   examples/normalized.json           -o examples/variance.json
	$(PY) scripts/build_xlsx.py examples/normalized.json examples/variance.json -o examples/comparison.xlsx
	$(PY) scripts/build_pdf.py  examples/normalized.json examples/variance.json \
	      --verdict examples/verdict.json -o examples/comparison.pdf
	@echo "pipeline OK"

clean-bundle:
	@rm -rf $(DIST)

clean: clean-bundle
	@rm -f examples/normalized.json examples/variance.json
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
