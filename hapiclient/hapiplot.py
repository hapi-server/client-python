import os
import re

import numpy as np

from hapiclient.hapi import hapitime2datetime
from hapiclient.util import log, warning, setopts
from hapiclient.plot.timeseries import timeseries
from hapiclient.plot.heatmap import heatmap

from hapiclient.hapi import request2path
from hapiclient.hapi import cachedir

def imagepath(server, dataset, parameters, start, stop, **kwargs):

    # Default options
    opts = {'cachedir': cachedir(), 'format': 'png', 'figsize': (7,3), 'dpi': 144, 'transparent': True}
    # Override defaults
    opts = setopts(opts, kwargs)

    fname = request2path(server, dataset, parameters, start, stop, opts['cachedir'])
    fname = fname \
            + "_figsize-" + str(opts['figsize'][0]) + "x" + str(opts['figsize'][1]) + "_" \
            + "dpi-" + str(opts['dpi']) \
            + "_transparent-" + str(opts['transparent']) \
            + "." + opts['format']

    return fname

def fill2mask(y, fill):
    """Create a masked array for a non-numeric fill value."""

    # TODO: Write. Needed for ISOTime parameters with a fill value.
    pass
    
def fill2nan(y, fill):

    if fill.lower() == 'nan':
        yfill = np.nan
    else:
        yfill = float(fill)

    # Replace fills with NaN for plotting
    # (so gaps shown in lines for time series an empty tiles for spectra)
    y[y == yfill] = np.nan
    # Catch case values in binary where, e.g., metadata says fill='-1E-31'
    # but file has -9.999999848243207e+30. This happens when CDF data
    # values stored as floats is converted to binary using double(value)
    # because double(float('-1E31')) = -9.999999848243207e+30. Technically
    # the server is not producing valid results b/c spec says fill values
    # in file must match double(fill in metadata).
    y[y == np.float32(yfill)] = np.nan

    return y

def tex(s):
    """Convert string with certain character patterns to a TeX string"""

    if not re.match('\$', s):
        s = re.sub(r"(.*)(\^[0-9].*)$",r'\1$^{\2}$', s)
        s = re.sub(r"(.*)(\^[0-9].*)/(.*)$",r'\1$^{\2}$/\3', s)
        s = re.sub(r"(.*)(_\w.*)$",r'\1$_{\2}$', s)
        s = re.sub(r"(.*)(_\w.*)/(.*)$",r'\1$_{\2}$/\3', s)

    return s

def hapiplot(*args, **kwargs):
    """Plot response from HAPI server.
    
    Usage
    -----
        hapiplot(server, dataset, params, start, stop, **kwargs)
        
        hapiplot(data, meta, **kwargs) where data and meta are return values
        from `hapi()`.
        
        All parameters in the dataset `dataset` are plotted. If a parameter
        has a bins attribute, it is plotted using `heatmap()`. Otherwise, it
        is plotted using `timeseries()`.

    Returns
    -------
    None, unless `returnimage`=True in which case raw image data is returned.

    See Also
    ---------
        hapiplot_test: Demonstrates kwarg options
        hapi: Get data from a HAPI server
        timeseries: Used by `hapiplot()` to HAPI parameters with no `bins`
        heatmap: Used by `hapiplot()` to HAPI parameters with `bins`
        
        <https://github.com/hapi-server/client-python/blob/master/hapi_demo.ipynb>
    
    kwargs
    ------
        * logging: [False]
        * saveimage: [False] Save image to `cachedir`. Ignored if 
            `pngquant`=True.
        * saveformat: [png], svg, or pdf
        * usecache: [True] Use cached data (and cached image if 
            `returnimage`=True)
        * cachedir: [cachedir()] The directory returned by 
            `from hapiclient.hapi import cachedir; print(cachedir())`
        * transparent: [False] Figure and axis box background are transparent
        * tskwargs: {} kwargs for the `timeseries()` function
        * hmkwargs: {} kwargs for the `heatmap()` function

        * returnimage: [False] If True, `hapiplot()` returns binary image data
        * returnformat: [png], svg, or pdf
            * pngquant: [False] Reduce png size using PNGQuant. Applies
                 if returnformat='png'.
            * pngquantbinary: [cachedir() + '/pngquant/pngquant'] Location of
                  pngquant executable.

    Example
    --------    
        >>> server  = 'http://hapi-server.org/servers/TestData/hapi'
        >>> dataset = 'dataset1'
        >>> start   = '1970-01-01T00:00:00'
        >>> stop    = '1970-01-02T00:00:00'
        >>> params  = 'scalar,vector'
        >>> opts    = {'logging': True}
        >>>
        >>> from hapiclient import hapiplot
        >>> hapiplot(server, dataset, params, start, stop, **opts)
        >>>
        >>> # or
        >>> from hapiclient import hapi, hapiplot
        >>> data, meta = hapi(server, dataset, params, start, stop, **opts)
        >>> hapiplot(data, meta, **opts)

    Version: 0.0.8
    """

    __version__ = '0.0.8' # This is modified by misc/setversion.py. See Makefile.

    if len(args) == 5:
        # For consistency with gallery and autoplot functions, allow usage of
        # hapiplot(server, dataset, parameters, start, stop, **kwargs)
        from hapiclient.hapi import hapiopts
        from hapiclient.hapi import hapi
        kwargs_allowed = hapiopts()
        kwargs_reduced = {}
        # Extract hapi() options from kwargs
        for key, value in kwargs.items():
            if key in kwargs_allowed:
                kwargs_reduced[key] = value
        data, meta = hapi(args[0], args[1], args[2], args[3], args[4], **kwargs_reduced)
        hapiplot(data, meta, **kwargs)
        return
    else:
        data = args[0]
        meta = args[1]
            
    # Default options
    opts = {
                'logging': False,
                'saveimage': False,
                'saveformat': 'png',
                'returnimage': False,
                'returnformat': 'png',
                'usecache': True,
                'cachedir': cachedir(),
                'transparent': False,
                'figsize': (7, 3),
                'dpi': 144,
                'format': 'png',
                'pngquant': False,
                'pngquantbinary': '/tmp/pngquant/pngquant',
                'tskwargs': {},
                'hmkwargs': {}
            }

    # Override defaults
    opts = setopts(opts, kwargs)

    if opts["returnimage"]:
        # Create cache directory
        dir = cachedir(opts['cachedir'], meta['x_server'])
        if not os.path.exists(dir): os.makedirs(dir)

    # Return cached image (case where we are returning binary image data)
    # imagepath() options
    iopts = {
                'cachedir': opts['cachedir'],
                'figsize': opts['figsize'],
                'dpi': opts['dpi'],
                'transparent': opts['transparent']
             }

    fnameimg = imagepath(meta['x_server'], meta['x_dataset'], meta['x_parameters'], meta['x_time.min'], meta['x_time.max'], **iopts)
    if opts['usecache'] and opts['returnimage'] and os.path.isfile(fnameimg):
            log('Returning cached binary image data in ' + fnameimg, opts)
            with open(fnameimg, "rb") as f:
                return f.read()

    # Convert from NumPy array of byte literals to NumPy array of
    # datetime objects.
    timename = meta['parameters'][0]['name']
    Time = hapitime2datetime(data[timename])

    # In the following, the x parameter is a datetime object.
    # If the x parameter is a number, would need to use plt.plot_date()
    # and much of the code for datetick.py would need to be modified.
    if len(meta["parameters"]) == 1:
        a = 0 # Time is only parameter
    else:
        a = 1 # Time plus another parameter

    for i in range(a, len(meta["parameters"])):

        name = meta["parameters"][i]["name"]
        log("Plotting parameter '%s'" % name, opts)

        #import pdb;pdb.set_trace()

        if len(data[name].shape) > 3:
            # TODO: Implement more than 3 dimensions?
            warning('Parameter ' + name + ' has more than 3 dimensions. Plotting not implemented for this many dimensions.')
            continue
        
        # If parameter has a size with two elements, e.g., [N1, N2]
        # create N2 plots.
        if len(data[name].shape) == 3: # (Time, N1, N2)
            for j in range(0, data[name].shape[1]):
                timename = meta['parameters'][0]['name']
                name_new = name + "[:," + str(j) + "]" # Give name to indicate what is plotted
                # Reduced data NDArray
                datar = np.ndarray(shape=(data[name].shape[0]), 
                                   dtype=[
                                           (timename, data.dtype[timename]),
                                           (name_new, data[name].dtype.str, data.dtype[name].shape[1])
                                           ])
                #import pdb;pdb.set_trace()

                #import pdb;pdb.set_trace()
                datar[timename] = data[timename]
                datar[name_new] = data[name][:,j]
                # Copy metadata to create a reduced metadata object
                metar = meta.copy() # Shallow copy
                metar["parameters"] = []
                # Create parameters array with elements of Time parameter ...
                metar["parameters"].append(meta["parameters"][0])
                # .... and this parameter
                metar["parameters"].append(meta["parameters"][i].copy())
                # Give new name to indicate it is a subset of full parameter
                metar["parameters"][1]['name'] = name_new
                # New size is N1
                metar["parameters"][1]['size'] = [metar["parameters"][1]['size'][0]]
                # Extract bins corresponding to jth column of data[name]

                if 'bins' in metar["parameters"][1]:
                    metar["parameters"][1]['bins'] = []
                    #print(j)
                    metar["parameters"][1]['bins'].append(meta["parameters"][i]['bins'][j])
                hapiplot(datar, metar, **opts)       
            return
                        
        title = meta["x_server"] + "\n" + meta["x_dataset"] + " | " + name

        if 'bins' in meta['parameters'][i]:

            if meta["parameters"][i]["type"] == "string":
                warning("Plots for only types double, integer, and isotime implemented. Not plotting %s." % meta["parameters"][i]["name"])
                continue

            z = np.asarray(data[name])

            if 'fill' in meta["parameters"][i]:
                if meta["parameters"][i]["type"] == 'integer':
                    z = z.astype('<f8', copy=False)
                z = fill2nan(z, meta["parameters"][i]['fill'])

            ylabel = meta["parameters"][i]['bins'][0]["name"] + " [" + meta["parameters"][i]['bins'][0]["units"] + "]"

            units = meta["parameters"][i]["units"]
            nl = ""
            if len(name) > 10 or len(units) > 10:
                nl = "\n"

            zlabel = name + nl + " [" + units + "]"

            if 'ranges' in meta["parameters"][i]['bins'][0]:
                bins = np.array(meta["parameters"][i]['bins'][0]["ranges"])
            else:
                bins = np.array(meta["parameters"][i]['bins'][0]["centers"])

            dt = np.diff(Time)
            dtu = np.unique(dt)
            if len(dtu) > 1:
                warning('Time values are not uniformly spaced. Bin width for time will be based on time separation of consecutive time values.')
                if False and 'cadence' in meta:

                    # Cadence != time bin width in general, so don't do this.
                    # See https://github.com/hapi-server/data-specification/issues/75
                    # Kept for future reference when Parameter.bin.window or
                    # Parameter.bin.windowWidth is added to spec.
                    import isodate
                    dt = isodate.parse_duration(meta['cadence'])
                    if 'timeStampLocation' in meta:
                        if meta['timeStampLocation'].lower() == "begin":
                            Time = np.vstack((Time,Time+dt))
                        if meta['timeStampLocation'].lower() == "end":
                            Time = np.vstack((Time-dt,Time))
                        if meta['timeStampLocation'].lower() == "center":
                            Time = np.vstack((Time-dt/2,Time+dt/2))
                    else:
                        # Default is center
                        Time = np.vstack((Time-dt/2,Time+dt/2))

                    Time = np.transpose(Time)
            elif 'timeStampLocation' in meta:
                if meta['timeStampLocation'].lower() == "begin":
                    Time = np.append(Time, Time[-1] + dtu[0])
                if meta['timeStampLocation'].lower() == "end":
                    Time = Time - dtu[0]
                    Time = np.append(Time, Time[-1] + dtu[0])


            hmopts = {
                        'figsize': opts['figsize'],
                        'dpi': opts['dpi'],
                        'title': title,
                        'ylabel': ylabel,
                        'zlabel': zlabel,
                        'returnimage': opts['returnimage']
                    }

            if opts['transparent']:
                hmopts['figure.facealpha'] = 0
                hmopts['axes.facealpha'] = 0

            # Override above options with those given
            if 'hmkwargs' in kwargs:
                for key in kwargs['hmkwargs']:
                    hmopts[key] = kwargs['hmkwargs'][key]
                
            plt, fig, canvas, ax, im, cb = heatmap(Time, bins, np.transpose(z), **hmopts)
        else:
                
            ptype = meta["parameters"][i]["type"]
            if ptype == "isotime":
                y = hapitime2datetime(data[name])
            elif ptype == 'string':
                y = data[name].astype('U')
            else:
                y = np.asarray(data[name])

            if 'fill' in meta["parameters"][i] and meta["parameters"][i]['fill']:
                if  ptype == 'isotime' or ptype == 'string':
                    Igood = y != meta["parameters"][i]['fill']
                    # Note that json reader returns fill to U not b.
                    Nremoved = data[name].size - Igood.size
                    #import pdb;pdb.set_trace()
                    if Nremoved > 0:
                        # TODO: Implement masking so connected line plots will
                        # show gaps as they do for NaN values.
                        warning('Parameter ' + name + ' is of type ' + ptype + ' and has ' + str(Nremoved) + ' fill value(s). Masking is not implemented, so removing fill elements before plotting.')
                        Time = Time[Igood]
                        y = y[Igood]
                if ptype == 'integer':
                    y = y.astype('<f8', copy=False)
                if ptype == 'integer' or ptype == 'double':
                    y = fill2nan(y, meta["parameters"][i]['fill'])

            units = ''
            if 'units' in meta["parameters"][i] and meta["parameters"][i]['units']:
                units = meta["parameters"][i]["units"]

            nl = ""
            if len(name) > 10 or len(units) > 10:
                nl = "\n"

            if ptype == 'string':
                ylabel = name
            else:
                ylabel = name + nl + " [" + units + "]"

            tsopts = {
                        'figsize': opts['figsize'],
                        'dpi': opts['dpi'],
                        'title': title,
                        'ylabel': ylabel,
                        'returnimage': opts['returnimage']
                    }

            # Override above options with those given
            if 'tskwargs' in kwargs:
                for key in kwargs['tskwargs']:
                    tsopts[key] = kwargs['tskwargs'][key]

            if opts['transparent']:
                tsopts['figure.facealpha'] = 0
                tsopts['axes.facealpha'] = 0
                
            plt, fig, canvas, ax = timeseries(Time, y, **tsopts)

        pngquant = False
        if opts['pngquant'] and not opts['saveformat'] == 'png':
            warning("pngquant = True requires saveformat = 'png'")

        if opts['pngquant'] and opts['saveformat'] == 'png':
            if os.path.exists(opts["pngquantbinary"]):
                pngquant = True
                
        if opts['saveimage'] or pngquant:
            log('Writing %s' % fnameimg, opts)
        else:
            from io import BytesIO
            fnameimg = BytesIO()

        # bbox_inches='tight' for file has same effect as fig.tight_layout()
        # for plot show in plot window.
        if opts['returnimage']:
            canvas.print_figure(fnameimg, format=opts['saveformat'], bbox_inches='tight', transparent=opts['transparent'], dpi=opts['dpi'])
        else:
            fig.savefig(fnameimg, format=opts['saveformat'], bbox_inches='tight', transparent=opts['transparent'], dpi=opts['dpi'])

        if opts['pngquant']:
            # 66% reduction in filesize using pngquant
            # Only get ~4% reduction in filesize using
            #  from PIL import Image
            #  image = Image.open(fnamepng)
            #  image.save(fnamepng,quality=2,optimize=True)
            if os.path.exists(opts["pngquantbinary"]):
                from hapiclient.util import system
                fnameimg_quant = fnameimg.replace(".png", ".quant.png")
                cmd = opts["pngquantbinary"] + ' --quality 20 ' + fnameimg + ' --output ' + fnameimg_quant
                system(cmd)
                if opts['logging']:
                    so = os.stat(fnameimg).st_size
                    sf = os.stat(fnameimg_quant).st_size
                    log('PNGQuant reduced file size by %.1fx' % (float(so)/float(sf)), opts)
                                        
                fnameimg = fnameimg_quant
            else:
                print('Did not find pngquant binary at ' + opts["pngquantdir"])

        if opts['returnimage']:
            if opts['saveimage'] or pngquant:
                log('Reading and returning %s.' % fnameimg, opts)
                with open(fnameimg, "rb") as f:
                    return f.read()
            else:
                return fnameimg.getvalue()
        else:
            # Two calls to fig.tight_layout() needed b/c of bug in PyQt:
            # https://github.com/matplotlib/matplotlib/issues/10361
            fig.tight_layout()
            fig.tight_layout() 
            # plt.tight_layout() 
            # Important: plt.show() must go after plt.savefig() (or png blank).
            plt.show()






