import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetick import datetick

# Plots two points separated by varying time ranges.
# For testing date/time tick labeling code datetick.py.
    
#for i in (15,31,59,182,366,400,731):
#    d1 = datetime(1900, 1, 2)
#    d2 = datetime.fromordinal(datetime.toordinal(d1) + i)

# Test 1-second cadence labels
test = 'sec'
tmpdir = "./tmp/"+test
if not os.path.exists(tmpdir): os.makedirs(tmpdir)
for j in range(1,2): # Seconds after 2000-01-01 for first point
    for i in range(1,2): # Time separation between points
        d1 = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=j)
        d2 = d1 + datetime.timedelta(seconds=i)
        
        x = np.array([d1,d2], dtype=object)
        #y = [0.0,1e-5/i]
        y = [0.0,0.0]
    
        ######################################################################
        #%% Default plot
        figstr = tmpdir + "/dateplot_%s_def_%02d_%04d.png" % (test,j,i)
        print("Writing %s" % figstr)
        plt.figure("Default")
        #plt.gcf().set_size_inches(5,1) # Aspect ratio of figure is 10
        plt.clf()
        plt.subplot(2,1,1)
        #plt.subplots_adjust(hspace=5,top=1)
        plt.plot(x, y, '*')
        plt.title('Default (top) and New (bottom)')
        plt.gcf().autofmt_xdate()
        #plt.gca().set_aspect(0.00001*i) # Remove vertical whitespace
        #plt.axes().set_aspect(0.000002) # Remove vertical whitespace
        #plt.gca().get_yaxis().set_visible(False) # Remove y-labels
        plt.gca().set_yticks([0]) # Label only y=0
        #plt.ylabel('y ',rotation=0,ha='right',va='center')
        plt.ylabel('y') # Show label
        #plt.show()
        #plt.savefig(figstr,bbox_inches='tight')
        ######################################################################
    
        ######################################################################
        #%% New plot
        figstr = tmpdir + "/dateplot_%s_new_%02d_%04d.png" % (test,j,i)
        print("Writing %s" % figstr)
        #plt.figure("New")
        #plt.clf()
        plt.subplot(2,1,2)
        plt.plot(x, y, '*')
        datetick('x') # Instead of autofmt_xdate()
        #plt.gca().set_aspect(0.00001*i) # Remove vertical whitespace
        #plt.axes().set_aspect(0.000002) 
        #plt.gca().get_yaxis().set_visible(False) # Remove y-labels
        plt.gca().set_yticks([0]) # Label only y=0
        #plt.ylabel('y ',rotation=0,ha='right',va='center')
        plt.ylabel('y') # Show label
        plt.tight_layout()
        #plt.show()
        plt.savefig(figstr,bbox_inches='tight')
        ######################################################################