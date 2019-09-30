#---------------------------------------------------------------------------------------#
#                                                                                       #
#	 - Makefile, version 1.8.1                                                          #
#	 - PROJECT:  xlines                                                                 #
# 	 - copyright, Blake Huber.  All rights reserved.                                    #
#                                                                                       #
#---------------------------------------------------------------------------------------#


PROJECT := xlines
CUR_DIR = $(shell pwd)
PYTHON_VERSION := python3
PYTHON3_PATH := $(shell which $(PYTHON_VERSION))
GIT := $(shell which git)
VENV_DIR := $(CUR_DIR)/p3_venv
PIP_CALL := $(VENV_DIR)/bin/pip
PANDOC_CALL := $(shell which pandoc)
ACTIVATE = $(shell . $(VENV_DIR)/bin/activate)
MAKE = $(shell which make)
MODULE_PATH := $(CUR_DIR)/$(PROJECT)
SCRIPT_DIR := $(CUR_DIR)/scripts
DOC_PATH := $(CUR_DIR)/docs
REQUIREMENT = $(CUR_DIR)/requirements.txt
VERSION_FILE = $(CUR_DIR)/$(PROJECT)/_version.py

# os package creation
AML_REQUIRES = 'python3,python3-pip,python3-setuptools,bash-completion,which'
PRE_SCRIPT = $(SCRIPT_DIR)/rpm_preinstall.py
_POSTINSTALL = $(CUR_DIR)/packaging/rpm/amzn2_postinstall.sh
YUM_CALL = sudo $(shell which yum)
PIP3_CALL = $(shell which pip3)


# --- rollup targets  ------------------------------------------------------------------------------


.PHONY: fresh-install fresh-test-install deploy-test deploy-prod

zero-source-install: clean source-install   ## Install (source: local). Zero prebuild artifacts

zero-test-install: clean setup-venv test-install  ## Install (source: testpypi). Zero prebuild artifacts

deploy-test: clean testpypi  ## Deploy (testpypi), generate all prebuild artifacts

deploy-prod: clean pypi   ## Deploy (pypi), generate all prebuild artifacts


# --- targets -------------------------------------------------------------------------------------


.PHONY: pre-build
pre-build:    ## Remove residual build artifacts
	rm -rf $(CUR_DIR)/dist
	mkdir $(CUR_DIR)/dist


setup-venv: $(VENV_DIR)

$(VENV_DIR): pre-build  ## Create and activiate python virtual package environment
	$(PYTHON3_PATH) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && $(PIP_CALL) install -U setuptools pip && \
	$(PIP_CALL) install -r $(REQUIREMENT)


.PHONY: artifacts
artifacts: setup-venv  ## Generate documentation build artifacts (*.rst)
	. $(VENV_DIR)/bin/activate  &&  $(PIP_CALL) install pandoc && \
	$(PANDOC_CALL) --from=markdown --to=rst README.md --output=README.rst


.PHONY: test
test: setup-venv  ## Run pytest unittests. Optional Param: PDB, MODULE
	if [ $(MODULE) ]; then \
	bash $(CUR_DIR)/scripts/make-test.sh --package-path $(MODULE_PATH) --module $(MODULE); \
	else bash $(CUR_DIR)/scripts/make-test.sh  --package-path $(MODULE_PATH); fi


.PHONY: test-coverage
test-coverage:  setup-venv  ## Run pytest unittests; generate coverage report
	bash $(CUR_DIR)/scripts/make-test.sh  --package-path $(MODULE_PATH) --coverage


.PHONY: test-complexity
test-complexity:  setup-venv  ## Run pytest unittests; generate McCabe Complexity Report
	bash $(CUR_DIR)/scripts/make-test.sh  --package-path $(MODULE_PATH) --complexity


.PHONY: test-pdb
test-pdb:  setup-venv  ## Run pytest unittests with debugging output on
	bash $(CUR_DIR)/scripts/make-test.sh  --package-path $(MODULE_PATH) --pdb


.PHONY: test-help
test-help:   ## Print runtime options for running pytest unittests
	bash $(CUR_DIR)/scripts/make-test.sh  --help


docs: clean setup-venv    ## Generate sphinx documentation
	. $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install -r $(DOC_PATH)/requirements.txt
	cd $(CUR_DIR) && $(MAKE) clean-docs
	cd $(DOC_PATH) && . $(VENV_DIR)/bin/activate && $(MAKE) html


.PHONY: build
build: artifacts  ## Build dist artifact and increment version
	if [ $(VERSION) ]; then . $(VENV_DIR)/bin/activate && \
	$(PYTHON3_PATH) $(SCRIPT_DIR)/version_update.py $(VERSION); \
	else . $(VENV_DIR)/bin/activate && \
	$(PYTHON3_PATH) $(SCRIPT_DIR)/version_update.py; fi && . $(VENV_DIR)/bin/activate && \
	cd $(CUR_DIR) && $(PYTHON3_PATH) setup.py sdist


.PHONY: builddeb
builddeb: setup-venv clean-version ## Build Debian distribution (.deb) os package
	@echo "Building Debian package format of $(PROJECT)";
	@echo "Building RPM package format of $(PROJECT)";
	if [ $(VERSION) ]; then . $(VENV_DIR)/bin/activate && \
	$(PYTHON3_PATH) $(SCRIPT_DIR)/builddeb.py --build --set-version $(VERSION); \
	else cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && $(PYTHON3_PATH) $(SCRIPT_DIR)/builddeb.py --build; fi


.PHONY: buildrpm-rhel
buildrpm-rhel:  setup-venv   ## Build Redhat distribution (.rpm) os package
	if [ $(VERSION) ]; then cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && \
	$(PYTHON3_PATH) $(SCRIPT_DIR)/buildrpm.py --build --set-version $(VERSION); elif [ $(RETAIN) ]; then \
	. $(VENV_DIR)/bin/activate && $(PYTHON3_PATH) $(SCRIPT_DIR)/buildrpm.py --build --container; else \
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && $(PYTHON3_PATH) $(SCRIPT_DIR)/buildrpm.py --build; fi


.PHONY: buildrpm-amzn
buildrpm-amzn: clean  ## Build Amazon Linux 2 distribution (.rpm) os package
	bash $(SCRIPT_DIR)/buildrpm-amzn2.sh


.PHONY: testpypi
testpypi: build     ## Deploy to testpypi without regenerating prebuild artifacts
	@echo "Deploy $(PROJECT) to test.pypi.org"
	. $(VENV_DIR)/bin/activate && twine upload --repository testpypi dist/*


.PHONY: pypi
pypi: clean build    ## Deploy to pypi without regenerating prebuild artifacts
	@echo "Deploy $(PROJECT) to pypi.org"
	. $(VENV_DIR)/bin/activate && twine upload --repository pypi dist/*
	rm -f $(CUR_DIR)/README.rst


.PHONY: install
install:    ## Install (source: pypi). Build artifacts exist
	if [ ! -e $(VENV_DIR) ]; then $(MAKE) setup-venv; fi; \
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install -U $(PROJECT)


.PHONY: test-install
test-install:  ## Install (source: testpypi). Build artifacts exist
	if [ ! -e $(VENV_DIR) ]; then $(MAKE) setup-venv; fi; \
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install -U $(PROJECT) --extra-index-url https://test.pypi.org/simple/


.PHONY: source-install
source-install:  clean  setup-venv  ## Install (source: local source). Build artifacts exist
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && 	$(PIP_CALL) install .


.PHONY: update-src-install
update-src-install:    ## Update Install (source: local source).
	if [ -e $(VENV_DIR) ]; then \
	cp -rv $(MODULE_PATH) $(VENV_DIR)/lib/python3*/site-packages/; fi


.PHONY: rebuild-docs
rebuild-docs:   ## Regenerate sphinx documentation
	cd $(CUR_DIR)/docs && . $(VENV_DIR)/bin/activate && $(MAKE) html && cd $(CUR_DIR);


.PHONY: upload-images
upload-images:   ## Upload README images to Amazon S3
	bash $(CUR_DIR)/scripts/s3upload.sh


.PHONY: help
help:   ## Print help index
	@printf "\n\033[0m %-15s\033[0m %-13s\u001b[37;1m%-15s\u001b[0m\n\n" " " "make targets: " $(PROJECT)
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[0m%-2s\033[36m%-20s\033[33m %-8s\033[0m%-5s\n\n"," ", $$1, "-->", $$2}' $(MAKEFILE_LIST)
	@printf "\u001b[37;0m%-2s\u001b[37;0m%-2s\n\n" " " "$(shell printf "%0.s_" {1..85})"
	@printf "\u001b[37;1m%-7s\u001b[37;1m%-3s\033[0m %-6s\u001b[44;1m%-9s\u001b[37;0m%-15s\n\n" " " "  make" "deploy-[test|prod] " "VERSION=x.y" " to deploy specific version"


.PHONY: clean-docs
clean-docs:    ## Remove build artifacts for documentation only
	@echo "Clean docs build directory"
	cd $(DOC_PATH) && $(VENV_DIR)/bin/activate && $(MAKE) clean || true


.PHONY: clean-version
clean-version:    ## Reset version back to committed version number
	@echo "RESET version to committed version number"; \
	$(GIT) checkout $(VERSION_FILE);


.PHONY: clean-pkgbuild
clean-pkgbuild: clean-version   ## Remove os packaging build artifacts
	@echo "Clean post build package assempbly artifacts"
	sudo rm -rf $(CUR_DIR)/.pybuild || true
	sudo rm -rf $(CUR_DIR)/*.egg* || true
	sudo rm -fr debian/.debhelper debian/files debian/xlines.postinst.debhelper
	sudo rm -fr debian/xlines.prerm.debhelper debian/xlines.substvars debian/xlines


.PHONY: clean
clean: clean-docs clean-version ## Remove generic build artifacts
	@echo "Clean project directories"
	rm -rf $(VENV_DIR) || true
	rm -rf $(CUR_DIR)/dist || true
	rm -rf $(CUR_DIR)/*.egg* || true
	rm -f $(CUR_DIR)/README.rst || true
	rm -rf $(CUR_DIR)/$(PROJECT)/__pycache__ || true
	rm -rf $(CUR_DIR)/tests/__pycache__ || true
	rm -rf $(CUR_DIR)/docs/__pycache__ || true
	rm -rf $(CUR_DIR)/.pytest_cache || true
	rm -rf $(CUR_DIR)/build || true
