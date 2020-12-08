# Default Python version to use for tests
PYTHON=python3.6
PYTHON_VER=$(subst python,,$(PYTHON))

# Python versions to test
# TODO: Use tox.
PYTHONVERS=python2.7 python3.5 python3.6 python3.7 python3.8

# VERSION is updated in "make version-update" step and derived
# from CHANGES.txt. Do not edit.
VERSION=0.1.5b4
SHELL:= /bin/bash

# Select this to have anaconda installed for you.
CONDA=./anaconda3
# CONDA=/opt/anaconda3
# CONDA=~/anaconda3

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
# 	CONDA=/c/tools/anaconda3
	CONDA=/c/tools/miniconda3
endif


CONDA_ACTIVATE=source $(CONDA)/etc/profile.d/conda.sh; conda activate

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	CONDA_ACTIVATE=source $(CONDA)/Scripts/activate; conda activate
endif

# Development:
# Test hapi() data read functions using repository code:
#   make repository-test-data     # Test using $(PYTHON)
#   make repository-test-data-all # Test on all versions in $(PYTHONVERS)
#
# Test hapiplot() functions using repository code:
#   make repository-test-plots     # Test using $(PYTHON)
#   make repository-test-plots-all # Test on all versions in $(PYTHONVERS)
#
# Making a local package:
# 1. Update CHANGES.txt to have a new version line
# 2. make package
# 3. make package-test-all
#
# Upload package to pypi.org test starting with uploaded package:
# 1. make release
# 2. Wait ~5 minutes and execute
# 3. make release-test-all
#    (Will fail until new version is available at pypi.org for pip install.
#     Sometimes takes ~5 minutes even though web page is immediately
#     updated.)
# 4. After package is finalized, create new version number in CHANGES.txt ending
#    with "b0" in setup.py and then run
#       make version-update
# 	git commit -a -m "Update version for next release"
#    This will update the version information in the repository to indicate it
#    is now in a pre-release state.

URL=https://upload.pypi.org/
REP=pypi

test:
	make repository-test-data-all
	make repository-test-plots-all

##########################################################################
# Test contents in repository using different python versions
repository-test-data-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test-data PYTHON=$$version ; \
	done

repository-test-plots-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test-plots PYTHON=$$version ; \
	done

CONDA_PKG=Miniconda3-latest-Linux-x86_64.sh
ifeq ($(shell uname -s),Darwin)
	CONDA_PKG=Miniconda3-latest-MacOSX-x86_64.sh
endif


condaenv:
# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	cp $(CONDA)/Library/bin/libcrypto-1_1-x64.* $(CONDA)/DLLs/
	cp $(CONDA)/Library/bin/libssl-1_1-x64.* $(CONDA)/DLLs/

# 	$(CONDA)/Scripts/conda config --set ssl_verify no
	$(CONDA)/Scripts/conda create -y --name $(PYTHON) python=$(PYTHON_VER)
else
	make $(CONDA)/envs/$(PYTHON) PYTHON=$(PYTHON)
endif

$(CONDA)/envs/$(PYTHON): /tmp/$(CONDA_PKG)
	$(CONDA_ACTIVATE); \
		$(CONDA)/bin/conda create -y --name $(PYTHON) python=$(PYTHON_VER)

/tmp/$(CONDA_PKG):
	curl https://repo.anaconda.com/miniconda/$(CONDA_PKG) > /tmp/$(CONDA_PKG) 
	bash /tmp/$(CONDA_PKG) -b -p $(CONDA)

pythonw=$(PYTHON)

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	pythonw=python
endif

ifeq ($(UNAME_S),Darwin)
#	Use pythonw instead of python. On OS-X, this prevents "need to install python as a framework" error.
#	The following finds the path to the binary of $(PYTHON) and replaces it with pythonw, e.g.,
#	/opt/anaconda3/envs/python3.6/bin/python3.6 -> /opt/anaconda3/envs/python3.6/bin/pythonw
	a=$(shell source activate $(PYTHON); which $(PYTHON))
	pythonw=$(subst bin/$(PYTHON),bin/pythonw,$(a))
endif

repository-test-data:
	@make clean

	make condaenv PYTHON=$(PYTHON)

	# https://stackoverflow.com/questions/30306099/pip-install-editable-vs-python-setup-py-develop
	$(CONDA_ACTIVATE) $(PYTHON); pip install pytest deepdiff; pip install --editable .
	# 'python setup.py develop' creates symlinks in system package directory.
	# $(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) setup.py develop | grep "Best"

	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) -m pytest -v -m 'not long' hapiclient/test/test_hapi.py
	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) -m pytest -v -m 'long' hapiclient/test/test_hapi.py
	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) -m pytest -v hapiclient/test/test_hapitime2datetime.py
	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) -m pytest -v hapiclient/test/test_hapitime2datetime.py
	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) -m pytest -v hapiclient/test/test_hapitime_reformat.py
	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) -m pytest -v hapiclient/test/test_chunking.py

# These require visual inspection.
repository-test-plots:
	@make clean
	make condaenv PYTHON=$(PYTHON)
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) setup.py develop | grep "Best"
	# Run using pythonw instead of python only so plot windows always work
	# for programs called from command line. This is needed for 
	# OS-X, Python 3.5, and matplotlib instaled from pip.
	$(CONDA_ACTIVATE) $(PYTHON); $(pythonw) hapi_demo.py

repository-test-plots-other:
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) hapiclient/hapiplot_test.py
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) hapiclient/plot/timeseries_test.py
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) hapiclient/plot/heatmap_test.py
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) hapiclient/gallery/gallery_test.py
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) hapiclient/autoplot/autoplot_test.py
	jupyter-notebook ../client-python-notebooks/hapi_demo.ipynb
##########################################################################

##########################################################################
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
		env-$(PYTHON)/bin/python /tmp/hapi_demo.py #&& \
		#env/bin/pytest -v hapiclient/test/test_hapi.py
##########################################################################

##########################################################################
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
##########################################################################

# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags

# Install package in local directory (symlinks made to local dir)
install-local:
#	python setup.py -e .
	source ~/.bashrc; $(CONDA_ACTIVATE) $(PYTHON); pip install --editable .

install:
	pip install 'hapiclient==$(VERSION)' --index-url $(URL)/simple
	conda list | grep hapiclient
	pip list | grep hapiclient

# Run pytest twice because first run creates test files that
# subsequent tests use for comparison.
test-clean:
	rm -f hapiclient/test/data/*
	pytest -v hapiclient/test/test_hapi.py
	pytest -v hapiclient/test/test_hapi.py

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
	- @rm -rf /c/tools/Anaconda3/envs/python3.6/Scripts/wheel.exe*
	- @rm -rf /c/tools/Anaconda3/envs/python3.6/vcruntime140.dll.*

