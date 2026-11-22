PYTHON ?= python3
export PYTHONPATH := $(CURDIR)/src

.PHONY: all test check examples build install clean

all: test

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m unittest discover -s tests -v

check:
	./hydrogenc check examples/hello.hy

examples: build
	./hydrogenc build examples/hello.hy -o build/hello
	./hydrogenc build examples/types.hy -o build/types
	./hydrogenc build examples/arithmetic.hy -o build/arithmetic
	./hydrogenc build examples/control_flow.hy -o build/control_flow
	./hydrogenc build examples/loops.hy -o build/loops
	./hydrogenc build examples/functions.hy -o build/functions
	./hydrogenc build examples/structs.hy -o build/structs
	./hydrogenc build examples/fizzbuzz.hy -o build/fizzbuzz

build:
	mkdir -p build

clean:
	rm -rf build
