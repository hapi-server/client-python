import warnings
import re
import sys
import numpy as np

# To allow to run from command line, find a back-end that works
import matplotlib
gui_env = ['Qt5Agg', 'QT4Agg', 'GTKAgg', 'TKAgg', 'WXAgg']
for gui in gui_env:
    try:
        #print("Trying MatPlotLib back-end ", gui)
        matplotlib.use(gui, warn=False, force=True)
        from matplotlib import pyplot as plt
        break
    except:
        continue

from hapiclient.util.datetick import datetick
from hapiclient.hapi import hapitime2datetime

def printf(format, *args): sys.stdout.write(format % args)

def hapiplot(data, meta, **kwargs):
    """Plot response from HAPI server.

    Version: 0.0.6

    See also https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb

    Example
    --------
        >>> from hapiclient.hapi import hapi
        >>> server = 'http://hapi-server.org/servers/SSCWeb/hapi'
        >>> dataset = 'ace'
        >>> start, stop = '2001-01-01T05:00:00', '2001-01-01T06:00:00'
        >>> parameters = 'X_GSE,Y_GSE,Z_GSE'
        >>> opts = {'logging': True, 'use_cache': True}
        >>> data, meta = hapi(server, dataset, parameters, start, stop, **opts)
        >>> hapiplot(data,meta)

    """

    __version__ = '0.0.6' # This is modified by misc/setversion.py. See Makefile.

    # TODO: Allow back-end to be specified as keyword, e.g.,
    #   hapiplot(data,meta,backend='Qt5Agg') ->
    #      matplotlib.use(backend, warn=False, force=True)

    # Default options
    DOPTS = {}
    DOPTS.update({'logging': False})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            warnings.warn('Warning: Keyword option "%s" is not valid.' % key)

    fignums = plt.get_fignums()
    if not fignums:
        fignums = [0]
    lastfn = fignums[-1]

    # Convert from NumPy array of byte literals to NumPy array of
    # datetime objects.
    Time = hapitime2datetime(data['Time'])

    # In the following, the x parameter is a datetime object.
    # If the x parameter is a number, would need to use plt.plot_date()
    # and much of the code for datetick.py would need to be modified.
    for i in range(1, len(meta["parameters"])):
        if meta["parameters"][i]["type"] != "double" and meta["parameters"][i]["type"] != "integer":
            warnings.warn("Plots for types double and integer only implemented.")
            continue

        name = meta["parameters"][i]["name"]
        y = np.asarray(data[name])

        if meta["parameters"][i]["fill"]:
            if meta["parameters"][i]["fill"] == 'nan':
                yfill = np.nan
            else:
                yfill = float(meta["parameters"][i]["fill"])
                #if isnan(yfill),yfill = 'null';,end
        else:
            yfill = 'null'

        if yfill != 'null':
            # Replace fills with NaN for plotting
            # (so gaps shown in lines for time series)
            y[y == yfill] = np.nan;

        if y.shape[0] < 11:
            props = {'linestyle': 'none', 'marker': '.', 'markersize': 16}
        elif y.shape[0] < 101:
            props = {'lineStyle': '-', 'linewidth': 2, 'marker': '.', 'markersize': 8}
        else:
            props = {}
        plt.figure(lastfn + i)
        plt.clf()
        plt.plot(Time, y, **props)
        plt.gcf().canvas.set_window_title(meta["x_server"] + " | " + meta["x_dataset"] + " | " + name)

        yl = meta["parameters"][i]["name"] + " [" + meta["parameters"][i]["units"] + "]"
        plt.ylabel(yl)
        plt.title(meta["x_server"] + "/info?id=" + meta["x_dataset"] + "&parameters=" + name + "\n", fontsize=10)
        plt.grid()
        datetick('x')

        fnamepng = re.sub(r'\.csv|\.bin', '.png', meta['x_dataFile'])
        if DOPTS['logging']: printf('Writing %s ... ', fnamepng)
        plt.figure(lastfn + i).savefig(fnamepng, dpi=300)
        if DOPTS['logging']: printf('Done.\n')

        # Important: This must go after savefig or else the png is blank.
        plt.show()
