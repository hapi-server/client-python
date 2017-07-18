import matplotlib.pyplot as plt 
import pandas
import time
import matplotlib
import warnings
#import matplotlib.dates as mdates

def hapiplot(data,meta):

    fignums = plt.get_fignums()
    if len(fignums) == 0:
        fignums = [0]
    lastfn = fignums[-1]
    
    Time = pandas.to_datetime(data['Time'],infer_datetime_format=True)
    
    for i in xrange(1,len(meta["parameters"])):
        if meta["parameters"][i]["type"] != "double" and meta["parameters"][i]["type"] != "integer":
            warnings.warn("Plots for types double and integer only implemented.")
            continue

        name = meta["parameters"][i]["name"]

        plt.figure(lastfn + i)
        plt.clf()
        plt.plot(Time,data[name])
        plt.gcf().canvas.set_window_title(meta["x_server"] + " | " + meta["x_dataset"] + " | " + name)

        yl = meta["parameters"][i]["name"] + " [" + meta["parameters"][i]["units"] + "]"
        plt.ylabel(yl)
        plt.title(meta["x_server"] + "/info?id=" + meta["x_dataset"] + "&parameters=" + name, fontsize=10)

        plt.grid()
        plt.show()