#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
#	 - Makefile, version 1.7.3                                                                    #
#	 - PROJECT:  keyup                                                                            #
# 	 - copyright, Blake Huber.  All rights reserved.                                              #
#                                                                                                 #
#-------------------------------------------------------------------------------------------------#


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
SCRIPTS := $(CUR_DIR)/scripts
DOC_PATH := $(CUR_DIR)/docs
REQUIREMENT = $(CUR_DIR)/requirements.txt
VERSION_FILE = $(CUR_DIR)/$(PROJECT)/_version.py

# os package creation
RHEL_REQUIRES = 'python36,python36-pip,python36-setuptools,python36-pygments,bash-completion'
AML_REQUIRES = 'python3,python3-pip,python3-setuptools,bash-completion'
PRE_SCRIPT = $(SCRIPTS)/rpm_preinstall_py3.py
POST_SCRIPT = $(SCRIPTS)/rpm_postinstall.py
YUM_CALL = sudo $(shell which yum)
ALIEN_CALL = sudo $(shell which alien)
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


.PHONY: setup-venv
setup-venv:    ## Create and activiate python venv
	$(PYTHON3_PATH) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && $(PIP_CALL) install -U setuptools pip && \
	$(PIP_CALL) install -r $(REQUIREMENT)


.PHONY: artifacts
artifacts:	  ## Generate documentation build artifacts (*.rst)
	$(PANDOC_CALL) --from=markdown --to=rst README.md --output=README.rst


.PHONY: test
test:     ## Run pytest unittests
	if [ $(PDB) ]; then PDB = "true"; \
	bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH) $(PDB); \
	elif [ $(MODULE) ]; then PDB = "false"; \
	bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH) $(PDB) $(MODULE); \
	elif [ $(COMPLEXITY) ]; then COMPLEXITY = "run"; \
	bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH) $(COMPLEXITY) $(MODULE); \
	else bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH); fi


docs: clean setup-venv    ## Generate sphinx documentation
	. $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install -r $(DOC_PATH)/requirements.txt
	cd $(CUR_DIR) && $(MAKE) clean-docs
	cd $(DOC_PATH) && . $(VENV_DIR)/bin/activate && $(MAKE) html


.PHONY: build
build: pre-build setup-venv artifacts   ## Build dist, increment version || force version (VERSION=X.Y)
	if [ $(VERSION) ]; then bash $(SCRIPTS)/version_update.sh $(VERSION); \
	else bash $(SCRIPTS)/version_update.sh; fi && . $(VENV_DIR)/bin/activate && \
	cd $(CUR_DIR) && $(PYTHON3_PATH) setup.py sdist


.PHONY: builddeb
builddeb:     ## Build Debian distribution (.deb) os package
	@echo "Building Debian package format of $(PROJECT)"; \
	$(YUM_CALL) install -y epel-release
	$(YUM_CALL) install -y alien
	$(ALIEN_CALL) --to-deb dist/xlines-*.noarch.rpm


.PHONY: buildrpm-rhel
buildrpm-rhel:  artifacts   ## Build Redhat distribution (.rpm) os package
	$(YUM_CALL) -y install epel-release which
	$(YUM_CALL) -y install python36 python36-pip python36-setuptools python36-devel
	sudo -H $(PIP3_CALL) install -U pip setuptools
	sudo cp -r /usr/local/lib/python3.*/site-packages/setuptools* /usr/lib/python3.*/site-packages/
	sudo cp -r /usr/local/lib/python3.*/site-packages/pkg_resources* /usr/lib/python3.*/site-packages/
	$(PYTHON3_PATH) setup_rpm.py bdist_rpm --requires=$(RHEL_REQUIRES) --python='/usr/bin/python3' --pre-install=$(PRE_SCRIPT)


.PHONY: buildrpm-aml
buildrpm-aml:  artifacts  ## Build Amazon Linux 2 distribution (.rpm) os package
	$(YUM_CALL) -y install python3 python3-pip python3-setuptools which sudo rpm-build
	$(PIP3_CALL) install -U pip setuptools pygments
	sudo cp -r /usr/local/lib/python3.*/site-packages/setuptools* /usr/lib/python3.*/site-packages/
	sudo cp -r /usr/local/lib/python3.*/site-packages/pkg_resources* /usr/lib/python3.*/site-packages/
	cp -r /usr/local/lib64/python3.*/site-packages/pygments .
	$(PYTHON3_PATH) setup_rpm.py bdist_rpm --requires=$(AML_REQUIRES) --python='/usr/bin/python3'


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
rebuild-docs:   ##  Regenerate sphinx documentation
	cd $(CUR_DIR)/docs && . $(VENV_DIR)/bin/activate && $(MAKE) html && cd $(CUR_DIR);


.PHONY: upload-images
upload-images:   ## Upload README images to Amazon S3
	bash $(CUR_DIR)/scripts/upload-s3-artifacts.sh


.PHONY: help
help:   ## Print help index
	@printf "\n\033[0m %-15s\033[0m %-13s\u001b[37;1m%-15s\u001b[0m\n\n" " " "make targets: " $(PROJECT)
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[0m%-2s\033[36m%-20s\033[33m %-8s\033[0m%-5s\n\n"," ", $$1, "-->", $$2}' $(MAKEFILE_LIST)
	@printf "\u001b[37;0m%-2s\u001b[37;0m%-2s\n\n" " " "___________________________________________________________________"
	@printf "\u001b[37;1m%-3s\u001b[37;1m%-3s\033[0m %-6s\u001b[44;1m%-9s\u001b[37;0m%-15s\n\n" " " "  make" "deploy-[test|prod] " "VERSION=X" " to deploy specific version"


.PHONY: clean-docs
clean-docs:    ## Remove build artifacts for documentation only
	@echo "Clean docs build directory"
	if [ -e $(VENV_DIR) ]; then . $(VENV_DIR)/bin/activate && \
	cd $(DOC_PATH) && $(MAKE) clean || true; fi


.PHONY: clean
clean:  clean-docs  ## Remove all build artifacts generated by make
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
