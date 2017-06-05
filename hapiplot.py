import matplotlib.pyplot as plt 
from datetime import datetime

# TODO: Figure out equivalent of MATLAB's datetick() function.

def hapiplot(meta,data, titlestr):
    fignums = plt.get_fignums()
    if len(fignums) == 0:
        fignums = [0]
    lastfn = fignums[-1]
    
    for i in xrange(1,len(meta["parameters"])):
        plt.figure(lastfn + i)
        plt.clf()
        name = meta["parameters"][i]["name"]
        # TODO: Need to account for fraction of day in data['Time'][0]
        t = 24*60*(data['Time'] - data['Time'][0])
        plt.plot(t,data[name])
        start = datetime.fromordinal(int(data['Time'][0])).isoformat()
        plt.xlabel("Minutes since " + start[0:9])
        yl = meta["parameters"][i]["name"] + " [" + meta["parameters"][i]["units"] + "]"
        plt.ylabel(yl)
        plt.title(titlestr + ": Parameter from dataset w/id = " + meta["x_dataset"] + " from " + meta["x_server"], fontsize=10)
        plt.grid()
        plt.show()