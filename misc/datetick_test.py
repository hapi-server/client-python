import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from datetick import datetick

#for i in (15,31,59,182,366,400,731):
for i in (400,):
    d1 = dt.datetime(1900, 1, 2)
    #d2 = dt.datetime(1900+i,1,1)
    d2 = datetime.fromordinal(datetime.toordinal(d1) + i)
    
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.1]
    plt.clf()
    plt.plot(x, y)
    plt.axes().set_aspect(0.01)
    plt.gca().get_yaxis().set_visible(False)
    plt.show()
    #print plt.gca().get_xticks()
    if 1:
        datetick('x')
        fname = "dateplot_%03d.png" % i
        print fname
        plt.savefig(fname,bbox_inches='tight')
