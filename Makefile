# Default Python version to use for tests
PYTHON=python3.6

# Python versions to test
# TODO: Use tox.
PYTHONVERS=python2.7 python3.5 python3.6 python3.7

# VERSION is updated in "make version-update" step. Do not edit.
VERSION=0.1.3b
SHELL:= /bin/bash

# First-time use, need to create the following virtual environments for testing:
# conda create -n python2.7 python=2.7; conda install jupyter; conda install spyder
# conda create -n python3.5 python=3.5; conda install jupyter; conda install spyder
# conda create -n python3.6 python=3.6; conda install jupyter; conda install spyder
# conda create -n python3.7 python=3.7; conda install jupyter; conda install spyder
#
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

# 'python setup.py develop' creates symlinks in system package directory.
repository-test-data:
	make clean
	source activate $(PYTHON); $(PYTHON) setup.py develop
	source activate $(PYTHON); $(PYTHON) -m pytest -v -m 'not long' hapiclient/test/test_hapi.py
	source activate $(PYTHON); $(PYTHON) -m pytest -v -m 'long' hapiclient/test/test_hapi.py
	source activate $(PYTHON); $(PYTHON) -m pytest -v hapiclient/test/test_hapitime2datetime.py

# These require visual inspection.
repository-test-plots:
	make clean
	source activate $(PYTHON); $(PYTHON) setup.py develop
	source activate $(PYTHON); $(PYTHON) hapi_demo.py

repository-test-plots-other:
	source activate $(PYTHON); $(PYTHON) hapiclient/hapiplot_test.py
	source activate $(PYTHON); $(PYTHON) hapiclient/plot/timeseries_test.py
	source activate $(PYTHON); $(PYTHON) hapiclient/plot/heatmap_test.py
	source activate $(PYTHON); $(PYTHON) hapiclient/gallery/gallery_test.py
	source activate $(PYTHON); $(PYTHON) hapiclient/autoplot/autoplot_test.py
	jupyter-notebook ../client-python-notebooks/hapi_demo.ipynb
##########################################################################

##########################################################################
package:
	make clean
	make version-update
	python setup.py sdist

package-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test-plots PYTHON=$$version ; \
	done

package-test:
	rm -rf env
	source activate $(PYTHON); pip install virtualenv; $(PYTHON) -m virtualenv env
	cp hapi_demo.py /tmp
	source env/bin/activate && \
		pip install pytest && \
		pip install deepdiff && \
		pip install dist/hapiclient-$(VERSION).tar.gz \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env/bin/pytest -v hapiclient/test/test_hapi.py && \
		env/bin/pytest -v hapiclient/test/test_hapitime2datetime.py && \
		env/bin/python /tmp/hapi_demo.py
##########################################################################

##########################################################################
release:
	make package
	make version-tag
	make release-upload

release-upload:
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
	python setup.py -e .

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
	- find . -name __pycache__ | xargs rm -rf {}
	- find . -name *.pyc | xargs rm -rf {}
	- find . -name *.DS_Store | xargs rm -rf {}
	- find . -type d -name __pycache__ | xargs rm -rf {}
	- find . -name *.pyc | xargs rm -rf {}
	- rm -f *~
	- rm -f \#*\#
	- rm -rf env
	- rm -rf dist
	- rm -f MANIFEST
	- rm -rf .pytest_cache/
	- rm -rf hapiclient.egg-info/

##########################################################################
# Not used
requirements:
	pip install pipreqs
	pipreqs hapiclient/

pngquant: bin/pngquant
	git clone https://github.com/pornel/pngquant.git
	make bin/pngquant

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
bin/pngquant:
	echo $(UNAME_S)
	echo "--- Attempting to compile pngquant."
	echo "--- If this fails, you may need to install libpng12 headers."
	cd pngquant; ./configure CFLAGS="-I../libpng12/" && make;
endif

ifeq ($(UNAME_S),Darwin)
bin/pngquant:
	echo "--- Attempting to compile pngquant."
	brew install libpng
	cd pngquant; ./configure && make
endif
