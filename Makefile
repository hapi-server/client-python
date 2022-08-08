# Test hapi() data read functions using repository code:
#   make repository-test python=PYTHON # Test using PYTHON (e.g, python3.6)
#   make repository-test-all           # Test on all versions in $(PYTHONVERS) var below
#
# Beta releases:
# 1. Run make repository-test-all
# 2. For non-doc/formatting changes, update version in CHANGES.txt.
# 3. run `make version-update` if version changed in CHANGES.txt.
# 4. Commit and push
#
# Making a local package:
#  1. Update CHANGES.txt to have a new version line
#  2. make package
#  3. make package-test-all
#
# Upload package to pypi.org
#  0. Remove the "b" in the version in CHANGES.txt
#  1. make release
#  2. Wait ~5 minutes and execute
#  3. make release-test-all
#     (Will fail until new version is available at pypi.org for pip install.
#      Sometimes takes ~5 minutes even though web page is immediately
#      updated.)
#  4. After package is finalized, create new version number in CHANGES.txt ending
#     with "b0" in setup.py and then run
#       make version-update
#       git commit -a -m "Update version for next release"
#     This will update the version information in the repository to indicate it
#     is now in a pre-release state.
#  5. Manually create a relase at https://github.com/hapi-server/client-python/releases 
#     (could do this automatically using https://stackoverflow.com/questions/21214562/how-to-release-versions-on-github-through-the-command-line)
#  Notes:
#   1. make repository-test tests with Anaconda virtual environment
#      make package-test and release-test tests with native Python virtual
#      environment.
#   2. Switch to using tox and conda-tox
#   3. 'pip install --editable . does not install develop dependencies, so
#      'python setup.py develop' is used. Won't need figure out when 2. is finished.

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
VERSION=0.2.6b
SHELL:= /bin/bash
#SHELL:= /c/Windows/system32/cmd

LONG_TESTS=false

CONDA=$(PWD)/anaconda3

ifeq ($(OS),Windows_NT)
	CONDA=C:/Users/weigel/git/client-python/anaconda3
	TMP=tmp/
endif
CONDA_ACTIVATE=source $(CONDA)/etc/profile.d/conda.sh; conda activate

################################################################################
install: $(CONDA)/envs/$(PYTHON)
	$(CONDA_ACTIVATE) $(PYTHON); pip install --editable .
	@printf "\n--------------------------------------------------------------------------------\n"
	@printf "To use created Anaconda environment, execute\n  $(CONDA_ACTIVATE) $(PYTHON)"
	@printf "\n--------------------------------------------------------------------------------\n"

test:
	make repository-test-all

####################################################################
# Tox notes
#
# Ideally local tests would use same commands as .tox.ini and .travis.yml.
#
# To use tox -e short-test, it seems we need to install and activate
# each version of python. So using tox locally does not seem to make
# things much simpler than `make repository-test`, which installs
# interpreter and runs tests.
#
# However, Travis tests use tox-anaconda and it seems creation of 
# virtual environment is done automatically.
#
#repository-test-all-tox:
#	tox -e short-test
#repository-test-tox: 
# # Does not work
#	tox -e py$(subst .,,$(PYTHON_VER)) short-test
####################################################################

# Test contents in repository using different Python versions
repository-test-all:
	@make clean
	#rm -rf $(CONDA)
	@ for version in $(PYTHONVERS) ; do \
		make repository-test PYTHON=$$version ; \
	done

repository-test:
	@make clean
ifeq ($(OS),Windows_NT)
	-@type NUL >> filename # Not tested
else
	-@touch $(CONDA) # If dir exists but Makefile was edited, this prevents re-install.
endif
	make condaenv PYTHON=$(PYTHON)
	$(CONDA_ACTIVATE) $(PYTHON); pip install pytest deepdiff; pip install .

ifeq (LONG_TESTS,true)
	$(CONDA_ACTIVATE) $(PYTHON); python -m pytest --tb=short -v -m 'long' hapiclient/test/test_hapi.py
else
	$(CONDA_ACTIVATE) $(PYTHON); python -m pytest --tb=short -v -m 'short' hapiclient/test/test_hapi.py
endif

	$(CONDA_ACTIVATE) $(PYTHON); python -m pytest -v hapiclient/test/test_chunking.py
	$(CONDA_ACTIVATE) $(PYTHON); python -m pytest -v hapiclient/test/test_hapitime2datetime.py
	$(CONDA_ACTIVATE) $(PYTHON); python -m pytest -v hapiclient/test/test_datetime2hapitime.py
	$(CONDA_ACTIVATE) $(PYTHON); python -m pytest -v hapiclient/test/test_hapitime_reformat.py
################################################################################

################################################################################
# Anaconda install
CONDA_PKG=Miniconda3-latest-Linux-x86_64.sh
CONDA_PKG_PATH=/tmp/$(CONDA_PKG)
ifeq ($(shell uname -s),Darwin)
	CONDA_PKG=Miniconda3-latest-MacOSX-x86_64.sh
	CONDA_PKG_PATH=/tmp/$(CONDA_PKG)
endif
ifeq ($(OS),Windows_NT)
	CONDA_PKG=Miniconda3-latest-Windows-x86_64.exe
	CONDA_PKG_PATH=C:/tmp/$(CONDA_PKG)
endif

activate:
	@echo "On command line enter:"
	@echo "$(CONDA_ACTIVATE) $(PYTHON)"

condaenv: $(CONDA)/envs/$(PYTHON)
	make $(CONDA)/envs/$(PYTHON)

$(CONDA)/envs/$(PYTHON): $(CONDA)
ifeq ($(OS),Windows_NT)
	$(CONDA_ACTIVATE); \
		$(CONDA)/Scripts/conda \
			create -y --name $(PYTHON) python=$(PYTHON_VER)
else
$(CONDA_ACTIVATE); \
        $(CONDA)/bin/conda \
        	create -y --name $(PYTHON) python=$(PYTHON_VER)
endif

$(CONDA): $(CONDA_PKG_PATH)
ifeq ($(OS),Windows_NT)
	# Not working; path is not set
	#start "$(CONDA_PKG_PATH)" /S /D=$(CONDA)
	echo "!!! Install miniconda3 into $(CONDA) manually by executing 'start $(PWD)/anaconda3'. Then re-execute make command."
	exit 1
else	
	bash $(CONDA_PKG_PATH) -b -p $(CONDA)
endif

$(CONDA_PKG_PATH):
	curl https://repo.anaconda.com/miniconda/$(CONDA_PKG) > $(CONDA_PKG_PATH)
################################################################################

################################################################################
# Packaging
package:
	make clean
	make version-update
	python setup.py sdist

package-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test PYTHON=$$version ; \
	done

env-$(PYTHON):
	rm -rf env-$(PYTHON)
	$(CONDA_ACTIVATE) $(PYTHON); \
		conda install -y virtualenv; \
		$(PYTHON) -m virtualenv env-$(PYTHON)

package-test:
	make package
	make env-$(PYTHON)
	make package-venv-test PACKAGE='dist/hapiclient-$(VERSION).tar.gz'

package-venv-test:
	cp hapi_demo.py /tmp # TODO: Explain why needed.
	cp hapi_demo.py /tmp
	source env-$(PYTHON)/bin/activate && \
		pip install pytest deepdiff ipython && \
		pip uninstall -y hapiplot && \
		pip install --pre hapiplot && \
		pip uninstall -y hapiclient && \
		pip install --pre '$(PACKAGE)' \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env-$(PYTHON)/bin/pytest -v -m 'short' hapiclient/test/test_hapi.py
		env-$(PYTHON)/bin/ipython /tmp/hapi_demo.py

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
	make env-$(PYTHON)
	make release-venv-test PYTHON=$(PYTHON)

release-venv-test:
	cp hapi_demo.py /tmp # TODO: Explain why needed.
	cp hapi_demo.py /tmp
	source env-$(PYTHON)/bin/activate && \
		pip install pytest deepdiff ipython && \
		pip uninstall -y hapiplot && \
		pip install --pre hapiplot && \
		pip uninstall -y hapiclient && \
		pip install hapiclient && \
		env-$(PYTHON)/bin/pytest -v -m 'short' hapiclient/test/test_hapi.py && \
		env-$(PYTHON)/bin/ipython /tmp/hapi_demo.py

################################################################################
# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py

version-tag:
	- git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags
################################################################################

################################################################################
# Install package in local directory (symlinks made to local dir)
install-pip:
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
