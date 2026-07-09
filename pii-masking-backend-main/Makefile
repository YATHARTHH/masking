#* Variables
SHELL := /usr/bin/env bash
PYTHON := python3.11
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := python_project
VERSION := latest

#* Poetry
.PHONY: poetry-download
poetry-download:
	@echo "Installing Poetry..."
ifeq ($(OS),Windows_NT)
	@powershell -Command "(New-Object System.Net.WebClient).DownloadString('https://install.python-poetry.org') | python -"
else
	@curl -sSL https://install.python-poetry.org | $(PYTHON) -
endif
	@echo "Poetry installation completed!"


.PHONY: poetry-remove

poetry-remove:
ifeq ($(OS),Windows_NT)
	PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = 'Tls12'; irm https://install.python-poetry.org | python - --uninstall}"
else
	curl -sSL https://install.python-poetry.org | $(PYTHON) - --uninstall
endif


#* Installation
.PHONY: install
install:
ifeq ($(OS),Windows_NT)
	@echo "Installing Poetry Export Plugin..."
	@poetry self add poetry-plugin-export || true
	@poetry lock -n
	@poetry export --without-hashes > requirements.txt
	@poetry install -n
	@poetry run mypy --install-types --non-interactive ./
else
	@echo "Installing Poetry Export Plugin..."
	@poetry self add poetry-plugin-export@latest || true
	@poetry lock -n
	@poetry export --without-hashes > requirements.txt
	@poetry install -n
# @poetry run mypy --install-types --non-interactive ./

endif


.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py39-plus $(wildcard **/*.py)
	poetry run isort --settings-path pyproject.toml --python-version 311  ./
	poetry run black --config pyproject.toml  ./

.PHONY: formatting
formatting: codestyle

.PHONY: test
test:
	set PYTHONPATH=. && poetry run pytest -c pyproject.toml --cov-report=html --cov=src test/
	poetry run python -c "import os; os.makedirs('assets/images', exist_ok=True)"
	poetry run coverage-badge -o assets/images/coverage.svg -f



.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run darglint --verbosity 2 src/ test/

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	poetry check
	poetry run bandit -ll --recursive src/ test/
	poetry run safety check --full-report

#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache


# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Include '__pycache__', '*.pyc', '*.pyo' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
endif

# cleaning macOS releated files
.PHONY: dsstore-remove
dsstore-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Filter '.DS_Store' -Recurse | Remove-Item -Force"
else
	find . | grep -E ".DS_Store" | xargs rm -rf
endif

.PHONY: mypycache-remove
mypycache-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Filter '.mypy_cache' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E ".mypy_cache" | xargs rm -rf
endif

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Filter '.ipynb_checkpoints' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
endif

.PHONY: pytestcache-remove
pytestcache-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Filter '.pytest_cache' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E ".pytest_cache" | xargs rm -rf
endif
