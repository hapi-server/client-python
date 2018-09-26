# Test repository contents using system packages:
#   make repository-test
#
# Make and test a candidate release package in virtual environment:
# 1. Update CHANGES.txt to have a new version line
# 2. make package
#
# Make release package, upload to pypi.org, and test package
# 1. make release
# 2. Wait 10 minutes and execute
# 3. make release-test
#    (Will fail unti new version is available at pypi.org for pip install. 
#     Usually takes 5-10 minutes even though web page is immediately
#     updated.)

# For using the pypi test repository, use
#URL=https://test.pypi.org/
#REP=pypitest

URL=https://upload.pypi.org/
REP=pypi

# VERSION below is updated in make version-update step.
VERSION=0.0.5
SHELL:= /bin/bash

release:
	make version-tag
	make release-upload

release-upload: 
	twine upload \
		-r $(REP) dist/hapiclient-$(VERSION).tar.gz \
		--config-file misc/.pypirc \
		&& \
	echo Uploaded to $(subst upload.,,$(URL))project/hapiclient/

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
	make README.txt
	make repository-test
	python setup.py sdist
	make package-test

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
		env/bin/python3 /tmp/hapi_demo.py

# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py
	mv setup.py.tmp setup.py
	mv hapiclient/hapi.py.tmp hapiclient/hapi.py
	mv hapiclient/hapiplot.py.tmp hapiclient/hapi.py
	mv Makefile.tmp Makefile

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags

README.txt: README.md
	pandoc --from=markdown --to=rst --output=README.txt README.md

# Use package in ./hapiclient instead of that installed by pip.
# This seems to not work in Spyder.
install-local:
	python setup.py develop

# Test contents in repository using system install of python.
# 'python setup.py develop' creates symlinks in system package directory.
repository-test:
	make README.txt	
	python setup.py develop
	pytest -v hapiclient/test/test_hapi.py
	python3 hapi_demo.py
	python setup.py develop --uninstall

install:
	pip install 'hapiclient==$(VERSION)' --index-url $(URL)/simple
	conda list | grep hapiclient
	pip list | grep hapiclient

test:
	pytest -v hapiclient/test/test_hapi.py

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

clean:
	- find . -name __pycache__ | xargs rm -rf {}
	- find . -name *.pyc | xargs rm -rf {}
	- find . -name *.DS_Store | xargs rm -rf {}
	- rm -rf __pycache__
	- rm -f *.pyc
	- rm -rf hapi-data	
	- rm -f *~
	- rm -f \#*\#
	- rm -f README.txt
	- rm -rf env
	- rm -rf dist
	- rm -f MANIFEST
	- rm -rf .pytest_cache/
	- rm -rf hapiclient.egg-info/





