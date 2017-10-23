import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetick import datetick

# Plots two points separated by varying time ranges.
# For testing date/time tick labeling code datetick.py.
# Files written to ./tmp for comparison.
tmpdir = "./tmp"
if not os.path.exists(tmpdir): os.makedirs(tmpdir)
    
#for i in (15,31,59,182,366,400,731):
#    d1 = datetime(1900, 1, 2)
#    d2 = datetime.fromordinal(datetime.toordinal(d1) + i)

# Test 1-second cadence labels
for i in xrange(1,3600):
#for i in xrange(1,2):
    d1 = datetime.datetime(1901, 1, 1) + datetime.timedelta(seconds=0)
    d2 = d1 + datetime.timedelta(seconds=i)
    
    x = np.array([d1,d2], dtype=object)
    y = [0.0,1e-5/i]

    ######################################################################
    # Default plot
    figstr = tmpdir + "/dateplot_minutes_orig_%03d.png"
    print "Writing %s" % figstr
    plt.figure("Original")
    plt.clf()
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    plt.axes().set_aspect(0.0001) # Remove vertical whitespace
    plt.gca().get_yaxis().set_visible(False) # Remove y-labels
    plt.show()
    plt.savefig(figstr % i,bbox_inches='tight')
    ######################################################################

    ######################################################################
    # New plot
    figstr = tmpdir + "/dateplot_minutes_new_%03d.png"
    print "Writing %s" % figstr
    plt.figure("New")
    plt.clf()
    plt.plot(x, y)
    datetick('x') # Instead of autofmt_xdate()
    plt.axes().set_aspect(0.0001) # Remove vertical whitespace
    plt.gca().get_yaxis().set_visible(False) # Remove y-labels
    plt.show()
    plt.savefig(figstr % i,bbox_inches='tight')
    ######################################################################