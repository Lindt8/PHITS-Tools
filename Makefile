# Common Python project Makefile tasks
.PHONY: test test-cov test-all test-unit clean-cov install clean docs build publish lint upload-unit upload-full

# Just run the tests without coverage reporting
test:
	pytest tests/

# Testing with coverage report
test-cov:
	pytest tests/ --cov=PHITS_tools --cov-report=html:htmlcov-unit --cov-report=xml:coverage-unit.xml --cov-report=term-missing

# Test everything, including integration tests in test/
test-all:
	pytest tests/ test/ --cov=PHITS_tools --cov-report=html:htmlcov-full --cov-report=xml:coverage-full.xml --cov-report=term-missing

# Just unit tests
test-unit:
	pytest tests/ -m "not integration"

# Clean coverage files
clean-cov:
	rm -rf htmlcov/ htmlcov-unit/ htmlcov-full/ .coverage*

install:
	git submodule update --init --recursive
	pip install -e .

install-dev:
	git submodule update --init --recursive
	pip install -e ".[develop]"

clean:
	rm -rf htmlcov/ htmlcov-unit/ htmlcov-full/ .coverage .pytest_cache/ __pycache__/
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +

docs:
	python build_docs.py

build:
	hatch build

publish:
	python -m twine upload dist/*
	
# Code quality checks (critical errors only)
lint:
	@echo "Checking for critical syntax errors..."
	flake8 PHITS_tools/ tests/ --select=E9,F63,F7,F82,F83 --show-source --statistics
	@echo "No critical errors found"

upload-unit:
	codecovcli upload-coverage --coverage-files-search-direct-file ./coverage-unit.xml --flag ci-unittests --name codecov-unit --slug Lindt8/PHITS-Tools -t %CODECOV_TOKEN% --disable-search


upload-full:
	codecovcli upload-coverage --coverage-files-search-direct-file ./coverage-full.xml --flag full-suite --name codecov-full --slug Lindt8/PHITS-Tools -t %CODECOV_TOKEN% --disable-search
