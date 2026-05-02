"""
Reads CHANGES.txt and finds last version. Updates version strings in Makefile,
setup.py, hapi.py, and hapiclient.py to match this version.

TODO: Find better way to manage this.
TODO: Update copyright year in LICENSE.txt
"""

import os
import re

overwrite = True

# Get last version in CHANGES.txt
print("Finding version information from CHANGES.txt")
fin = open("CHANGES.txt")
version = '0.0.0'
for line in fin:
	(repl, n) = re.subn(r"^v(.*):.*", r"\1", line)
	if n > 0:
		version = repl
fin.close()
version = version.rstrip()
print("Using version = " + version)

fnames = {
	"Makefile": r"^(VERSION=)(.*)$",
	"setup.py": r"^(\s*version=')(.*)(',\s*)$",
	"hapiclient/hapi.py": r"^(\s*Version: )(.*)$",
	"hapiclient/__init__.py": r"^(__version__ = ')(.*)('$)",
	".zenodo.json": r'^(\s*"version": ")(.*)(",?\s*)$'
}

def replace_version(match):
	prefix = match.group(1)
	suffix = match.group(3) if match.lastindex == 3 else ''
	return prefix + version + suffix


for fname, regex in fnames.items():
	updated = False
	lines = ''
	fin = open(fname)
	print("Scanning " + fname)
	for lineo in fin:
		line1 = re.sub(regex, replace_version, lineo)
		if lineo != line1:
			print("Original: " + lineo.rstrip())
			print("Modified: " + line1.rstrip())
			updated = True
		lines = lines + line1
	fin.close()

	if not updated:
		print("  Version in file was already up-to-date.")
		continue

	with open(fname + ".tmp", "w") as fout:
		fout.write(lines)
	print("Wrote " + fname + ".tmp")

	if overwrite:
		os.rename(fname + ".tmp", fname)
		print("  Renamed " + fname + ".tmp" + " to " + fname)
