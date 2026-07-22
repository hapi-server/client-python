# Test using tox (See also README.md for additional instructions):
#   tox
#
# Beta versions (not released to pypi.org).
# 	1. tox
# 	2. Update bX in version in CHANGES.txt.
# 	3. Run `make version-update` if version changed in CHANGES.txt.
# 	4. Commit and push
#
# Releases
# 	Tag the repo, create a GitHub release, and upload package to pypi.org
#  	1. Remove the "b" in the version in CHANGES.txt
#  	2. make release
#  	3. Wait ~5 minutes and execute
#        make pypi-release-test
#      or
#        make pypi-release-test-all
#  	4. Create new version number in CHANGES.txt ending with b0 and then:
#        make version-update
#        git commit -a -m "Update version for next release"
#      This will update the version information in the repository to indicate it
#      is now in a pre-release state.

URL=https://upload.pypi.org/
REP=pypi

# Default to the first Python environment configured in tox.ini.
PYTHON=$(shell tox list --no-desc | sed -n 's/^py3\([0-9][0-9]*\)$$/python3.\1/p' | sed -n '1p')
PYTHON_VER=$(subst python,,$(PYTHON))

# VERSION is updated in "make version-update" step and derived
# from CHANGES.txt. Do not edit.
VERSION=0.3.3b0
SHELL:= /bin/bash

################################################################################
.PHONY: install test

test:
	tox

install:
	python -m pip install --editable .
################################################################################

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
# Packaging
.PHONY: package package-test package-test-all package-smoke-test

package:
	make clean
	make version-update
	python -m pip install --upgrade build twine
	python -m build
	python -m twine check dist/*

package-test-all:
	make package
	@tmpdir=$$(mktemp -d); \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	tox run \
		--installpkg dist/hapiclient-$(VERSION)-py3-none-any.whl \
		--override "testenv.changedir=$$tmpdir" \
		-- $(CURDIR)/test/test_datetime2hapitime.py
	make package-smoke-test

package-test:
	make package
	make package-smoke-test

package-smoke-test:
	@tmpdir=$$(mktemp -d); \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	python -m venv "$$tmpdir/venv"; \
	venv_python="$$tmpdir/venv/bin/python"; \
	"$$venv_python" -m pip install "$(CURDIR)/dist/hapiclient-$(VERSION)-py3-none-any.whl"; \
	cd "$$tmpdir"; "$$venv_python" "$(CURDIR)/misc/smoke.py" "$(VERSION)" --exclude-path "$(CURDIR)"; \
	"$$venv_python" -m pip install --force-reinstall --no-deps "$(CURDIR)/dist/hapiclient-$(VERSION).tar.gz"; \
	"$$venv_python" "$(CURDIR)/misc/smoke.py" "$(VERSION)" --exclude-path "$(CURDIR)"
################################################################################

################################################################################
# Release a package to pypi.org
release:
	make package-test
	make version-tag
	make gh-release
	make pypi-release

gh-release:
	gh release create $(VERSION) --target master --notes "Release $(VERSION)" --title "Release $(VERSION)"

pypi-release:
	pip install twine
	twine upload \
		-r $(REP) dist/hapiclient-$(VERSION).tar.gz -u __token__ \
		&& echo Uploaded to $(subst upload.,,$(URL))/project/hapiclient/

pypi-release-test-all:
	@set -e; \
	tox list --no-desc | sed -n 's/^py3\([0-9][0-9]*\)$$/\1/p' | while read minor; do \
		make pypi-release-test PYTHON=python3.$$minor; \
	done

pypi-release-test:
	@set -e; \
	tmpdir=$$(mktemp -d); \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	uv venv --python $(PYTHON_VER) "$$tmpdir/venv"; \
	venv_python="$$tmpdir/venv/bin/python"; \
	uv pip install --python "$$venv_python" 'hapiclient==$(VERSION)'; \
	cd "$$tmpdir"; \
	"$$venv_python" "$(CURDIR)/misc/smoke.py" "$(VERSION)" --exclude-path "$(CURDIR)"
################################################################################

clean:
	- @find . -type d -name __pycache__ -exec rm -rf {} +
	- @find . -type f -name '*.pyc' -exec rm -f {} +
	- @find . -type f -name '*.DS_Store' -exec rm -f {} +
	- @rm -f *~
	- @rm -f \#*\#
	- @rm -rf env
	- @rm -rf dist
	- @rm -f MANIFEST
	- @rm -rf .pytest_cache/
	- @rm -rf hapiclient.egg-info/
