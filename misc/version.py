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

fnames = ["Makefile", "setup.py", "hapiclient/hapi.py", "hapiclient/__init__.py"]
regexes = ["VERSION=(.*)", "version=(.*)", "Version: (.*)", "__version__ = (.*)"]
replaces = ["VERSION=" + version, "version='" + version + "',", "Version: " + version, "__version__ = '" + version + "'"]
for i in range(len(fnames)):
	updated = False
	is_up_to_date = False

	lines = ''
	fin = open(fnames[i])
	print("Scanning " + fnames[i])
	for lineo in fin:
		line1 = re.sub(regexes[i], replaces[i], lineo)
		if re.search(regexes[i], lineo):
			is_up_to_date = True
		if lineo != line1:
			print("Original: " + lineo.rstrip())
			print("Modified: " + line1.rstrip())
			updated = True
		lines = lines + line1
	fin.close()
	if is_up_to_date:
		print("  Version in file was already up-to-date.")
	errstr = "Problem updating line with %s in %s." % (regexes[i], fnames[i])
	assert updated is True or is_up_to_date is True, errstr
	with open(fnames[i] + ".tmp", "w") as fout:
		fout.write(lines)
	print("Wrote " + fnames[i] + ".tmp")
	if overwrite:
		os.rename(fnames[i] + ".tmp", fnames[i])
		print("  Renamed " + fnames[i] + ".tmp" + " to " + fnames[i])
