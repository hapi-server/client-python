# Make package, upload to pypi.org, and test package
# 1. Edit VERSION variable below
# 2. Edit version variable in setup.py and then execute "make all"

# For testing, change all occurences of
# pypi.org to test.pypi.org 
# and 
# -r pypi to -r pypitest 

VERSION=0.0.34
SHELL:= /bin/bash

all:
	make package
	make upload
	make package-test

package:
	make README.txt
	python setup.py sdist
# The following results in package being named hapiclient-0.0.0 when installed.	
#	python setup.py sdist --version $(VERSION)

# Enter "deactivate" to exit virtual environment
# On OS-X (at least), I need to close windows for next plot to be shown
package-test:
	pip install --user pipenv
	python3 -m virtualenv env
	source env/bin/activate && \
		pip install hapiclient \
		--index-url https://test.pypi.org/simple  \
		--extra-index-url https://pypi.org/simple
	env/bin/python3 hapi_demo.py

upload: 
	twine upload \
		-r pypitest dist/hapiclient-$(VERSION).tar.gz \
		--config-file misc/.pypirc \
		&& \
		echo "Uploaded to https://test.pypi.org/project/hapiclient/"

README.txt: README.md
	pandoc --from=markdown --to=rst --output=README.txt README.md

# Use package in ./hapiclient
install-local:
	python setup.py develop

install:
	python setup.py develop --uninstall; pip install 'hapiclient==$(VERSION)' --index-url https://test.pypi.org/simple
	conda list | grep hapiclient
	pip list | grep hapiclient

# First run creates test files that subsequent tests use for comparison
test-clean:
	rm -f hapiclient/test/data/*
	pytest -v hapiclient/test/test_hapi.py
	pytest -v hapiclient/test/test_hapi.py

test:
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