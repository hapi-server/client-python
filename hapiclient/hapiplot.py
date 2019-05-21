import os
import re
import hashlib
import json

import numpy as np
from matplotlib import rc_context

from hapiclient.hapi import hapitime2datetime
from hapiclient.hapi import request2path
from hapiclient.hapi import cachedir
from hapiclient.util import log, warning
from hapiclient.plot.timeseries import timeseries
from hapiclient.plot.heatmap import heatmap
from hapiclient.plot.util import setopts


def imagepath(meta, i, cachedir, opts):

    optsmd5 = hashlib.md5(json.dumps(opts, sort_keys=True).encode('utf8')).hexdigest()

    fname = request2path(meta['x_server'],
                         meta['x_dataset'],
                         meta['parameters'][i]['name'],
                         meta['x_time.min'],
                         meta['x_time.max'],
                         cachedir)

    return fname + "-" + optsmd5 + "." + opts['savefig.format']


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
    # in file must match double(fill string in metadata).
    y[y == np.float32(yfill)] = np.nan

    return y


def hapiplot(*args, **kwargs):
    """Plot response from HAPI server.

    Demos
    -----
    <https://github.com/hapi-server/client-python/blob/master/hapiclient/plot/hapiplot_test.py>


    Usage
    -----
            data, meta = hapiplot(server, dataset, params, start, stop, **kwargs)
        or    
            meta = hapiplot(data, meta, **kwargs)
        where data and meta are return values from `hapi()`.

        All parameters are plotted. If a parameter has a bins attribute,
        it is plotted using `heatmap()`. Otherwise, it is plotted using
        `timeseries()`.

    Returns
    -------
        `data` is the same as that returned from `hapi()`.
        `meta` is the same as that returned from `hapi()` with the additon of

        meta['parameters'][i]['hapiplot']['figure'] is a reference to the
            figure (e.g., plt.gcf()). Usage example:

            >>> fig = meta['parameters'][i]['hapiplot']['figure']
            >>> fig.set_facecolor('blue')
            >>> fig.axes[0].set_ylabel('new y-label')
            >>> fig.axes[0].set_title('new title\\nsubtitle\\nsubtitle')
            >>> fig.tight_layout()

        meta['parameters'][i]['hapiplot']['colorbar'] is a reference to the
            colorbar on the figure (if parameter plotted as a heatmap)

        meta['parameters'][i]['hapiplot']['image'] is PNG, PDF, or SVG data
            and is included only if `returnimage=True`. Usage example:

            >>> img = meta['parameters'][i]['hapiplot']['image']
            >>> Image.open(io.BytesIO(img)).show()
            >>> # or
            >>> f = open('/tmp/a.png', 'wb')
            >>> f.write(img)
            >>> f.close()

    See Also
    ---------
        hapi: Get data from a HAPI server
        timeseries: Used by `hapiplot()` to HAPI parameters with no `bins`
        heatmap: Used by `hapiplot()` to HAPI parameters with `bins`

        <https://github.com/hapi-server/client-python-notebooks>

    kwargs
    ------
        * logging: [False] Display console messages
        * usecache: [True] Use cached data
        * tsopts: {} kwargs for the `timeseries()` function
        * hmopts: {} kwargs for the `heatmap()` function

    Other kwargs
    ------------
        * returnimage: [False] If True, `hapiplot()` returns binary image data
        * returnformat: [png], svg, or pdf
        * cachedir: Directory to store images. Default is hapiclient.hapi.cachedir()
        * useimagecache: [True] Used cached image (when returnimage=True)
        * saveimage: [False] Save image to `cachedir`
        * saveformat: [png], svg, or pdf

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
        >>>
        >>> from hapiclient import hapi, hapiplot
        >>> data, meta = hapi(server, dataset, params, start, stop, **opts)
        >>> hapiplot(data, meta, **opts)

    Version: 0.1.0
    """

    __version__ = '0.1.0' # This is modified by misc/setversion.py. See Makefile.

    if len(args) == 5:
        # For consistency with gallery and autoplot functions, allow useage of
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
        meta = hapiplot(data, meta, **kwargs)
        return data, meta
    else:
        data = args[0]
        meta = args[1]

    # Default options
    opts = {
                'logging': False,
                'saveimage': False,
                'returnimage': False,
                'usecache': True,
                'useimagecache': True,
                'cachedir': cachedir(),
                'backend': 'default',
                'style': 'fast',

                'title': '',
                'ztitle': '',
                'xlabel': '',
                'ylabel': '',
                'zlabel': '',
                'logx': False,
                'logy': False,
                'logz': False,

                'tsopts': {},
                'hmopts': {},

                'backend': 'default',
                'returnimage': False,

                'rcParams':
                    {
                        'savefig.dpi': 144,
                        'savefig.format': 'png',
                        'savefig.bbox': 'standard',
                        'savefig.transparent': True,
                        'figure.max_open_warning': 50,
                        'figure.figsize': (7, 3),
                        'figure.dpi': 144,
                        'axes.titlesize': 10
                    },
                '_rcParams': {
                        'figure.bbox': 'standard'
                }
            }

    # Will use given rc style parameters and style name to generate file name.
    # Assumes rc parameters of style never change.
    styleParams = opts['rcParams']

    # Override defaults
    opts = setopts(opts, kwargs)

    # _rcParams are not actually rcParams:
    #'figure.bbox': 'standard', # Set to 'tight' to have fig.tight_layout() called before figure shown.

    if opts["saveimage"]:
        # Create cache directory
        dir = cachedir(opts['cachedir'], meta['x_server'])
        if not os.path.exists(dir): os.makedirs(dir)

    # Convert from NumPy array of byte literals to NumPy array of
    # datetime objects.
    timename = meta['parameters'][0]['name']
    Time = hapitime2datetime(data[timename])

    if len(meta["parameters"]) == 1:
        a = 0 # Time is only parameter
    else:
        a = 1 # Time plus another parameter

    for i in range(a, len(meta["parameters"])):

        meta["parameters"][i]['hapiplot'] = {}

        name = meta["parameters"][i]["name"]

        # Return cached image (case where we are returning binary image data)
        # imagepath() options. Only need filename under these conditions.
        if opts['saveimage'] or (opts['returnimage'] and opts['useimagecache']):
            fnameimg = imagepath(meta, i, opts['cachedir'], styleParams)

        if opts['useimagecache'] and opts['returnimage'] and os.path.isfile(fnameimg):
            log('Returning cached binary image data in ' + fnameimg, opts)

            meta["parameters"][i]['hapiplot']['imagefile'] = fnameimg
            with open(fnameimg, "rb") as f:
                meta["parameters"][i]['hapiplot']['image'] = f.read()
            continue

        name = meta["parameters"][i]["name"]
        log("Plotting parameter '%s'" % name, opts)

        if len(data[name].shape) > 3:
            # TODO: Implement more than 2 dimensions?
            warning('Parameter ' + name + ' has size with more than 2 dimensions. Plotting first two only.')
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
                metar = hapiplot(datar, metar, **opts)
                meta["parameters"][i]['hapiplot'] = metar["parameters"][i]['hapiplot']
            return meta

        title = meta["x_server"] + "\n" + meta["x_dataset"] + " | " + name

        if 'bins' in meta['parameters'][i]:
            # Plot as heatmap

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
                #warning('Time values are not uniformly spaced. Bin width for '
                #        'time will be based on time separation of consecutive time values.')
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


            if opts['xlabel'] != '' or 'xlabel' in kwargs:
                opts['hmopts']['xlabel'] = opts['xlabel']

            opts['hmopts']['ylabel'] = ylabel
            if opts['ylabel'] != '' or 'ylabel' in kwargs:
                opts['hmopts']['ylabel'] = opts['ylabel']

            opts['hmopts']['title'] = title
            if opts['title'] != '' or 'title' in kwargs:
                opts['hmopts']['title'] = opts['title']

            opts['hmopts']['zlabel'] = zlabel
            if opts['ztitle'] != '' or 'zlabel' in kwargs:
                opts['hmopts']['xlabel'] = opts['zlabel']

            if opts['logx'] is not False:
                opts['hmopts']['logx'] = True
            if opts['logy'] is not False:
                opts['hmopts']['logy'] = True
            if opts['logz'] is not False:
                opts['hmopts']['logz'] = True

            hmopts = {
                        'returnimage': opts['returnimage'],
                        'transparent': opts['rcParams']['savefig.transparent']
                    }

            for key, value in opts['hmopts'].items():
                hmopts[key] = value

            with rc_context(rc=opts['rcParams']):
                fig, cb = heatmap(Time, bins, np.transpose(z), **hmopts)
            meta["parameters"][i]['hapiplot']['figure'] = fig
            meta["parameters"][i]['hapiplot']['colorbar'] = cb

        else:
            # Plot as time series.

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
                        warning('Parameter ' + name + ' is of type ' + ptype + ' and has '
                                + str(Nremoved) + ' fill value(s). Masking is not implemented, '
                                'so removing fill elements before plotting.')
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
                nl = "\n" # TODO: Automatically figure out when this is needed.

            if ptype == 'string':
                ylabel = name
            else:
                ylabel = name + nl + " [" + units + "]"

            if not 'legendlabels' in opts['tsopts']:
                legendlabels = []
                if 'size' in meta['parameters'][i]:
                    for l in range(0,meta['parameters'][i]['size'][0]):
                        legendlabels.append('col %d' % l)
                    opts['tsopts']['legendlabels'] = legendlabels


            if opts['xlabel'] != '' or 'xlabel' in kwargs:
                opts['tsopts']['xlabel'] = opts['xlabel']

            opts['tsopts']['ylabel'] = ylabel
            if opts['ylabel'] != '' or 'ylabel' in kwargs:
                opts['tsopts']['ylabel'] = opts['ylabel']

            opts['tsopts']['title'] = title
            if opts['title'] != '' or 'title' in kwargs:
                opts['tsopts']['title'] = opts['title']

            if opts['logx'] is not False:
                opts['tsopts']['logx'] = True
            if opts['logy'] is not False:
                opts['tsopts']['logy'] = True

            tsopts = {
                        'logging': opts['logging'],
                        'returnimage': opts['returnimage'],
                        'transparent': opts['rcParams']['savefig.transparent']
                    }

            # Apply tsopts
            for key, value in opts['tsopts'].items():
                tsopts[key] = value

            with rc_context(rc=opts['rcParams']):
                fig = timeseries(Time, y, **tsopts)
            meta["parameters"][i]['hapiplot']['figure'] = fig


        if opts['saveimage']:
            log('Writing %s' % fnameimg, opts)
            meta["parameters"][i]['hapiplot']['imagefile'] = fnameimg
        else:
            from io import BytesIO
            fnameimg = BytesIO()

        if opts['returnimage']:
            with rc_context(rc=opts['rcParams']):
                fig.canvas.print_figure(fnameimg)

            if opts['saveimage']:
                with open(fnameimg, mode='rb') as f:
                    meta["parameters"][i]['hapiplot']['image'] = f.read()
            else:
                meta["parameters"][i]['hapiplot']['image'] = fnameimg.getvalue()
        else:
            with rc_context(rc=opts['rcParams']):
                fig.savefig(fnameimg)

            # Two calls to fig.tight_layout() may be needed b/c of bug in PyQt:
            # https://github.com/matplotlib/matplotlib/issues/10361
            if opts['_rcParams']['figure.bbox'] is 'tight':
                fig.tight_layout()

    return meta



