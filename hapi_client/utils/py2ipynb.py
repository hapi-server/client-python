# https://stackoverflow.com/questions/23292242/converting-to-not-from-ipython-notebook-format/35720002#35720002
from IPython.nbformat import v3, v4

file = 'hapi_demo'
with open(file+'.py') as fpin:
    text = fpin.read()

nbook = v3.reads_py(text)
nbook = v4.upgrade(nbook)  # Upgrade v3 to v4

jsonform = v4.writes(nbook) + "\n"
with open(file+".ipynb", "w") as fpout:
    fpout.write(jsonform)
    
text += """
# <markdowncell>

# If you can read this, reads_py() is no longer broken! 
"""    