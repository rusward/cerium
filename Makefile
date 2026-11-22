PYTHON ?= python3
export PYTHONPATH := $(CURDIR)/src

DOCS_VENV ?= website/.venv
DOCS_PYTHON := $(CURDIR)/$(DOCS_VENV)/bin/python
DOCS_MKDOCS := .venv/bin/mkdocs

.PHONY: all test check examples build install docs-install docs-serve docs-build clean

all: test

install:
	$(PYTHON) -m pip install -e .

docs-install:
	$(PYTHON) -m venv $(DOCS_VENV)
	$(DOCS_PYTHON) -m pip install -r website/requirements.txt

docs-serve:
	cp SPEC.md website/docs/spec.md
	cp CHANGELOG.md website/docs/changelog.md
	cd website && $(DOCS_MKDOCS) serve

docs-build:
	cp SPEC.md website/docs/spec.md
	cp CHANGELOG.md website/docs/changelog.md
	cd website && $(DOCS_MKDOCS) build --strict

test:
	$(PYTHON) -m unittest discover -s tests -v

check:
	./ceriumc check examples/hello.ce

examples: build
	./ceriumc build examples/hello.ce -o build/hello
	./ceriumc build examples/types.ce -o build/types
	./ceriumc build examples/arithmetic.ce -o build/arithmetic
	./ceriumc build examples/control_flow.ce -o build/control_flow
	./ceriumc build examples/loops.ce -o build/loops
	./ceriumc build examples/functions.ce -o build/functions
	./ceriumc build examples/structs.ce -o build/structs
	./ceriumc build examples/input.ce -o build/input
	./ceriumc build examples/conversions.ce -o build/conversions
	./ceriumc build examples/fizzbuzz.ce -o build/fizzbuzz

build:
	mkdir -p build

clean:
	rm -rf build
