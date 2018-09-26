import re
import sys

# TODO: Find better way to manage this.

# Get last version in CHANGES.txt
print("Finding version information from CHANGES.txt")
fin = open("CHANGES.txt")
version = '0.0.0'
for line in fin:
	(repl,n) = re.subn(r"^v(.*):.*", r"\1", line)
	if n > 0:
		version = repl
fin.close()
version = version.rstrip()
print("Using version = " + version)

lines = ''
fin = open("Makefile")
for lineo in fin:
	line = re.sub(r"VERSION=(.*)", r"VERSION=" + version, lineo)
	updated = lineo != line
	lines = lines + line
fin.close()
assert updated is False, "Problem updating version in Makefile."
with open("Makefile.tmp", "w") as fout:
    fout.write(lines + "\n")
fout.close()    
print("Wrote Makefile.tmp")

lines = ''
fin = open("setup.py")
for lineo in fin:
	line = re.sub(r"version=(.*),", r"version='" + version + "',", lineo)
	updated = lineo != line
	lines = lines + line
fin.close()
assert updated is False, "Problem updating version in setup.py."
with open("setup.py.tmp", "w") as fout:
    fout.write(lines + "\n")
fout.close()    
print("Wrote setup.py.tmp")

for fname in ("hapiclient/hapi.py","hapiclient/hapiplot.py"):
	lines = ''
	fin = open(fname)
	#sys.stdout.write("Updating version in " + fname + ".")
	for lineo in fin:
		line1 = re.sub(r"__version__ = '(.*)'", r"__version__ = '" + version + "'", lineo)
		updated1 = lineo != line1
		line2 = re.sub(r"Version: (.*)", r"Version: "+version, line1)
		updated2 = lineo != line2
		lines = lines + line2
	fin.close()
	assert updated1 == False or updated2 is False, "Problem updating version in " + fname + "."
	with open(fname + ".tmp", "w") as fout:
	    fout.write(lines + "\n")
	fout.close()    
	print("Wrote " + fname + ".tmp")
