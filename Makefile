PYTHON = python3.10

.PHONY: help
help:
	@echo "  install     install all dev and production dependencies (virtualenv is created as venv)"
	@echo "  clean       remove unwanted stuff"
	@echo "  test        run tests"

.PHONY: install
install:
	$(PYTHON) -m venv venv; . venv/bin/activate; python -m pip install -r requirements.txt

.PHONY: clean
clean:
	rm -fr test
	rm -fr venv

.PHONY: test
test:
	. venv/bin/activate; python -m unittest discover

.PHONY: all
all: clean install test
