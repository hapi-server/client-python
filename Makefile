# Development: Test repository contents:
#   make repository-test
#
# Make and test a candidate release package in virtual environment:
# 1. Update CHANGES.txt to have a new version line
# 2. make package
#
# Make release package, upload to pypi.org, and test package
# 1. make release
# 2. Wait ~5 minutes and execute
# 3. make release-test
#    (Will fail unti new version is available at pypi.org for pip install. 
#     Usually takes ~5 minutes even though web page is immediately
#     updated.)

# For using the pypi test repository, use
#URL=https://test.pypi.org/
#REP=pypitest

PYTHON=python3.6

URL=https://upload.pypi.org/
REP=pypi

# VERSION below is updated in "make version-update" step.
VERSION=0.0.8
SHELL:= /bin/bash

test:
	make repository-test

# Test contents in repository using system install of python.
# 'python setup.py develop' creates symlinks in system package directory.
repository-test:
	make repository-test-data PYTHON=python3.6
	make repository-test-data PYTHON=python2.7
	make repository-test-plots PYTHON=python3.6
	make repository-test-plots PYTHON=python2.7

repository-test-data:
	make clean
	$(PYTHON) setup.py develop
	$(PYTHON) -m pytest -v -m 'not long' hapiclient/test/test_hapi.py
	$(PYTHON) -m pytest -v -m 'long' hapiclient/test/test_hapi.py
	$(PYTHON) -m pytest -v hapiclient/test/test_hapitime2datetime.py
	#python setup.py develop --uninstall

# These require visual inspection.
repository-test-plots:
	make clean
	$(PYTHON) setup.py develop
	$(PYTHON) hapi_demo.py
	$(PYTHON) hapiclient/hapiplot_test.py
	$(PYTHON) hapiclient/plot/timeseries_test.py
	$(PYTHON) hapiclient/gallery/gallery_test.py
	$(PYTHON) hapiclient/autoplot/autoplot_test.py
	jupyter-notebook hapi_demo.ipynb

repository-test-server:
	$(PYTHON) hapiclient/plotserver/hapiplotserver_test.py
	read -p "Press enter to continue tests."
	cd hapiclient/plotserver/; \
		gunicorn -w 4 -b 127.0.0.1:5000 'hapiplotserver:gunicorn(loglevel="debug",use_cache=False)' &
	read -p "Press enter to continue tests."
	echo("Open and check http://127.0.0.1:5000/")

release:
	make version-tag
	make release-upload

release-upload: 
	twine upload \
		-r $(REP) dist/hapiclient-$(VERSION).tar.gz \
		--config-file misc/.pypirc \
		&& \
	echo Uploaded to $(subst upload.,,$(URL))/project/hapiclient/

# See comments above package-test
release-test:
	rm -rf env
	python3 -m virtualenv env
	cp hapi_demo.py /tmp
	source env/bin/activate && \
		pip install pytest && \
		pip install deepdiff && \
		pip install 'hapiclient==$(VERSION)' \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env/bin/pytest -v hapiclient/test/test_hapi.py && \
		env/bin/python3 /tmp/hapi_demo.py

package:
	make clean
	make version-update
	#make repository-test
	python setup.py sdist
	#make package-test

# Test package in a virtual environment
# Enter "deactivate" to exit virtual environment
# On OS-X (at least), I need to close windows for next plot to be shown 
# (virutal environment has different windows manager than system)
# Note: pytest uses script in local directory. Need to figure out how to
# use version in installed package.
package-test:
	rm -rf env
	python3 -m virtualenv env
	cp hapi_demo.py /tmp
	source env/bin/activate && \
		pip install pytest && \
		pip install deepdiff && \
		pip install dist/hapiclient-$(VERSION).tar.gz \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env/bin/pytest -v hapiclient/test/test_hapi.py && \
		env/bin/pytest -v hapiclient/test/test_hapitime2datetime.py && \
		env/bin/python3 /tmp/hapi_demo.py

# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py
	mv setup.py.tmp setup.py
	mv hapiclient/hapi.py.tmp hapiclient/hapi.py
	mv hapiclient/hapiplot.py.tmp hapiclient/hapiplot.py
	mv Makefile.tmp Makefile

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags

# Use package in ./hapiclient instead of that installed by pip.
# This seems to not work in Spyder.
install-local:
	python setup.py

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

clean:
	- python setup.py --uninstall
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





