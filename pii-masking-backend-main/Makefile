#* Variables
PYTHON := python
PYTHONPATH := .

#* Docker variables
IMAGE := pii-masking-backend
VERSION := latest

#* Installation
.PHONY: install
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

.PHONY: pre-commit-install
pre-commit-install:
	pre-commit install

#* Formatters & Linters
.PHONY: codestyle
codestyle:
	ruff check --fix ./
	isort --settings-path pyproject.toml ./
	black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

.PHONY: test
test:
	pytest -c pyproject.toml --cov-report=html --cov=src tests/

.PHONY: check-codestyle
check-codestyle:
	ruff check ./
	isort --diff --check-only --settings-path pyproject.toml ./
	black --diff --check --config pyproject.toml ./

.PHONY: mypy
mypy:
	mypy --config-file pyproject.toml src/

.PHONY: check-safety
check-safety:
	bandit -ll --recursive src/
	pip-audit

#* Docker
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build -t $(IMAGE):$(VERSION) -f ./docker/Dockerfile .

.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

#* Cleaning
.PHONY: clean
clean: pycache-remove mypycache-remove pytestcache-remove

.PHONY: pycache-remove
pycache-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Include '__pycache__', '*.pyc', '*.pyo' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
endif

.PHONY: mypycache-remove
mypycache-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Filter '.mypy_cache' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E ".mypy_cache" | xargs rm -rf
endif

.PHONY: pytestcache-remove
pytestcache-remove:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Filter '.pytest_cache' -Recurse | Remove-Item -Force -Recurse"
else
	find . | grep -E ".pytest_cache" | xargs rm -rf
endif
