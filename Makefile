# Make package, upload to pypi.org, and test package
# 1. Update CHANGES.txt to have a new version line
# 2. Execute "make all"
# 3. Execute "make test-package" (May fail if new version takes time to be
#    available at pypi.org. Usually takes a few minutes.)

# To test a repository contents, use
# make test-local

# For using the pypi test repository, use
#URL=https://test.pypi.org/
#REP=pypitest

URL=https://upload.pypi.org/
REP=pypi

# VERSION is updated in make updateversion step.
VERSION=0.0.1
SHELL:= /bin/bash

all:
	make test
	make package
	make upload
	make package-test

# Update version based on content of CHANGES.txt
updateversion:
	python misc/version.py
	mv setup.py.tmp setup.py
	mv hapiclient/hapi.py.tmp hapiclient/hapi.py
	mv hapiclient/hapiplot.py.tmp hapiclient/hapi.py
	mv Makefile.tmp Makefile

commitversion:
	git commit -a -m "Update version before tagging"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)

package:
	make updateversion
	make commitversion
	make README.txt
	python setup.py sdist

upload: 
	twine upload \
		-r $(REP) dist/hapiclient-$(VERSION).tar.gz \
		--config-file misc/.pypirc \
		&& \
	echo Uploaded to $(subst upload.,,$(URL))project/hapiclient/

README.txt: README.md
	pandoc --from=markdown --to=rst --output=README.txt README.md

# Use package in ./hapiclient instead of that installed by pip.
install-local:
	python setup.py develop

# Test contents in repository using local install of python.
test-local:
	make install-local
	pytest -v hapiclient/test/test_hapi.py
	python3 hapi_demo.py
	python setup.py develop --uninstall

# Test package in a virtual environment
# Enter "deactivate" to exit virtual environment
# On OS-X (at least), I need to close windows for next plot to be shown 
# (virutal environment has different windows manager than system)
# Note: pytest uses script in local directory. Need to figure out how to
# use version in installed package.
test-package:
	pip install --user pipenv
	python3 -m virtualenv env
	cp hapi_demo.py /tmp
	source env/bin/activate && \
		pip install 'hapiclient==$(VERSION)' \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		pytest -v hapiclient/test/test_hapi.py && \
		env/bin/python3 /tmp/hapi_demo.py

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


