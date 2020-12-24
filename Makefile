# Test hapi() data read functions using repository code:
#   make repository-test     # Test using $(PYTHON)
#   make repository-test-all # Test on all versions in $(PYTHONVERS)
#
# Making a local package:
#  1. Update CHANGES.txt to have a new version line
#  2. make package
#  3. make package-test-all
#
# Upload package to pypi.org
#  1. make release
#  2. Wait ~5 minutes and execute
#  3. make release-test-all
#     (Will fail until new version is available at pypi.org for pip install.
#      Sometimes takes ~5 minutes even though web page is immediately
#      updated.)
#  4. After package is finalized, create new version number in CHANGES.txt ending
#     with "b0" in setup.py and then run
#       make version-update
# 	  git commit -a -m "Update version for next release"
#     This will update the version information in the repository to indicate it
#     is now in a pre-release state.
#
#  Notes:
#   1. make repository-test tests with Anaconda virtual environment
#      make package-test and release-test tests with native Python virtual
#      environment.

URL=https://upload.pypi.org/
REP=pypi

# Default Python version to use for tests
PYTHON=python3.8
PYTHON_VER=$(subst python,,$(PYTHON))

# Python versions to test
# TODO: Use tox.
PYTHONVERS=python3.8 python3.7 python3.6 python3.5 python2.7    

# VERSION is updated in "make version-update" step and derived
# from CHANGES.txt. Do not edit.
VERSION=0.1.9b0
SHELL:= /bin/bash

LONG_TESTS=false

# Select this to have anaconda installed for you.
CONDA=./anaconda3
# Use existing anaconda
# CONDA=/opt/anaconda3
# CONDA=~/anaconda3

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
  # CONDA=/c/tools/anaconda3
	CONDA=/c/tools/miniconda3
endif

CONDA_ACTIVATE=source $(CONDA)/etc/profile.d/conda.sh; conda activate

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	CONDA_ACTIVATE=source $(CONDA)/Scripts/activate; conda activate
endif

################################################################################
test:
	make repository-test-all

# Test contents in repository using different python versions
repository-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test PYTHON=$$version ; \
	done

repository-test:
	@make clean

	make condaenv PYTHON=$(PYTHON)

	# https://stackoverflow.com/questions/30306099/pip-install-editable-vs-python-setup-py-develop
	$(CONDA_ACTIVATE) $(PYTHON); \
		pip install pytest deepdiff; pip install --editable .
	# Previously used:
	# $(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) setup.py develop | grep "Best"

ifeq (LONG_TESTS,true)
	$(CONDA_ACTIVATE) $(PYTHON); $(python) -m pytest -v -m 'long' hapiclient/test/test_hapi.py
else
	$(CONDA_ACTIVATE) $(PYTHON); $(python) -m pytest -v -m 'short' hapiclient/test/test_hapi.py	
endif

	$(CONDA_ACTIVATE) $(PYTHON); $(python) -m pytest -v hapiclient/test/test_chunking.py
	$(CONDA_ACTIVATE) $(PYTHON); $(python) -m pytest -v hapiclient/test/test_hapitime2datetime.py
	$(CONDA_ACTIVATE) $(PYTHON); $(python) -m pytest -v hapiclient/test/test_hapitime_reformat.py
################################################################################

################################################################################
# Anaconda install
CONDA_PKG=Miniconda3-latest-Linux-x86_64.sh
ifeq ($(shell uname -s),Darwin)
	CONDA_PKG=Miniconda3-latest-MacOSX-x86_64.sh
endif

condaenv:
# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	cp $(CONDA)/Library/bin/libcrypto-1_1-x64.* $(CONDA)/DLLs/
	cp $(CONDA)/Library/bin/libssl-1_1-x64.* $(CONDA)/DLLs/

	# $(CONDA)/Scripts/conda config --set ssl_verify no
	$(CONDA)/Scripts/conda create -y --name $(PYTHON) python=$(PYTHON_VER)
else
	make $(CONDA)/envs/$(PYTHON) PYTHON=$(PYTHON)
endif

$(CONDA)/envs/$(PYTHON): ./anaconda3
	$(CONDA_ACTIVATE); \
		$(CONDA)/bin/conda create -y --name $(PYTHON) python=$(PYTHON_VER)

./anaconda3: /tmp/$(CONDA_PKG)
	bash /tmp/$(CONDA_PKG) -b -p $(CONDA)

/tmp/$(CONDA_PKG):
	curl https://repo.anaconda.com/miniconda/$(CONDA_PKG) > /tmp/$(CONDA_PKG)
################################################################################

################################################################################
# Packaging
package:
	make clean
	make version-update
	python setup.py sdist

package-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test-plots PYTHON=$$version ; \
	done

env-$(PYTHON):
	$(CONDA_ACTIVATE) $(PYTHON); \
		conda install -y virtualenv; \
		$(PYTHON) -m virtualenv env-$(PYTHON)

package-test:
	make package
	make env-$(PYTHON)
	cp hapi_demo.py /tmp
	source env-$(PYTHON)/bin/activate && \
		pip install pytest && \
		pip install deepdiff && \
		pip uninstall -y hapiclient && \
		pip install dist/hapiclient-$(VERSION).tar.gz \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env-$(PYTHON)/bin/python /tmp/hapi_demo.py && \
		env-$(PYTHON)/bin/pytest -v -m 'short' hapiclient/test/test_hapi.py
################################################################################

################################################################################
# Release a package to pypi.org
release:
	make package
	make version-tag
	make release-upload

release-upload:
	pip install twine
	echo "rweigel, t1p"
	twine upload \
		-r $(REP) dist/hapiclient-$(VERSION).tar.gz \
		&& echo Uploaded to $(subst upload.,,$(URL))/project/hapiclient/

release-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make release-test PYTHON=$$version ; \
	done

release-test:
	rm -rf env
	source activate $(PYTHON); pip install virtualenv; $(PYTHON) -m virtualenv env
	cp hapi_demo.py /tmp
	source env/bin/activate && \
		pip install pytest && \
		pip install deepdiff && \
		pip install 'hapiclient==$(VERSION)' \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env/bin/pytest -v hapiclient/test/test_hapi.py && \
		env/bin/python /tmp/hapi_demo.py
################################################################################

################################################################################
# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags
################################################################################

################################################################################
# Install package in local directory (symlinks made to local dir)
install-local:
	$(CONDA_ACTIVATE) $(PYTHON); pip install --editable .

install:
	pip install 'hapiclient==$(VERSION)' --index-url $(URL)/simple
	conda list | grep hapiclient
	pip list | grep hapiclient
################################################################################

################################################################################
# Recreate reference response files. Use this if server response changes
# Run pytest twice because first run creates test files that
# subsequent tests use for comparison.
test-clean:
	rm -f hapiclient/test/data/*
	pytest -v hapiclient/test/test_hapi.py
	pytest -v hapiclient/test/test_hapi.py
################################################################################

clean:
	- @find . -name __pycache__ | xargs rm -rf {}
	- @find . -name *.pyc | xargs rm -rf {}
	- @find . -name *.DS_Store | xargs rm -rf {}
	- @find . -type d -name __pycache__ | xargs rm -rf {}
	- @find . -name *.pyc | xargs rm -rf {}
	- @rm -f *~
	- @rm -f \#*\#
	- @rm -rf env
	- @rm -rf dist
	- @rm -f MANIFEST
	- @rm -rf .pytest_cache/
	- @rm -rf hapiclient.egg-info/
	- @rm -rf /c/tools/miniconda3/envs/python3.6/Scripts/wheel.exe*
	- @rm -rf /c/tools/miniconda3/envs/python3.6/vcruntime140.dll.*
