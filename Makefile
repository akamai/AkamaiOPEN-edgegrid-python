PYTHON = python3

.PHONY: help
help:
	@echo "  install     install all dev and production dependencies (virtualenv is created as venv)"
	@echo "  clean       remove unwanted stuff"
	@echo "  test        run tests"

.PHONY: install
install:
	$(PYTHON) -m venv venv; . venv/bin/activate; python -m pip install -r dev-requirements.txt

.PHONY: clean
clean:
	rm -fr test
	rm -fr venv

.PHONY: test
test:
	@. venv/bin/activate; pytest --junitxml $(CURDIR)/test/tests.xml --cov-report xml:$(CURDIR)/test/coverage/cobertura-coverage.xml --cov=akamai

.PHONY: test-docker
test-docker:
	sh ci/test_with_docker.sh

.PHONY: lint
lint:
	@. venv/bin/activate; pylint ./akamai

.PHONY: all
all: clean install test lint
