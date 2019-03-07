import datetime
import warnings
import numpy as np

import matplotlib
from matplotlib.patches import Patch
from matplotlib.colors import LogNorm

from hapiclient.plot.datetick import datetick


def heatmap(x, y, z, **kwargs):
    """Plot a heatmap using pcolormesh and do typical configuration.

    plt, fig, canvas, ax, im, cb = heatmap(x, y, z, **kwargs)

    x and y are bin centers, edges, or ranges; x is associated with the
    columns of z and y is associated with the rows of z.

    If len(x) == z.shape[1], x is assumed to correspond to the center of the
    rectangle and the labels are placed at the center of the bin. The bin
    widths are x[i+1]-x[i]. If the spacing of x values is not uniform,
    the bin width of x[-1] is assumed to be equal to that of x[-2].

    The same logic is applied to y if len(y) == z.shape[0].

    If len(x) == z.shape[1] + 1, x is assumed to correspond to edges of the
    rectangle and the labels are placed at x[i] and the bin widths are x[i+1]-x[i].

    The same logic is applied to y if len(y) == z.shape[0] + 1.

    If x.shape = (z.shape[1], 2), each row gives the range of the rectangle
    associated with the columns of z and a "No data" color is used for
    ranges that do not have data.

    The same logic is applied to y if y.shape = (z.shape[0], 2).

    kwargs:

        Colorbar
        ------
        * zlabel
        * cbtitle
        * clim - Ignore if ...
        * cmap
        * cmap.name (ignored if cmap given)
        * cmap.numcolors (ignored if cmap given)
        * cmap.clim

        Logarithm
        ---------
        * logx - All x values must be either >= 0 or <= 0.
        * logy - All y values must be either >= 0 or <= 0.
        * logz - All z values must be either >= 0 or <= 0. The zero values rectangles are colored using logz0color.
        * logz0.legend
        * log.auto^

        Tile edges, gaps, and NaN
        -------------------------
        * edgecolor - Edge color of tile border

        * logz0.color
        * logz0.alpha
        * logz0.hatch
        * logz0.legend - Show legend entry for logz0

        * gap.color
        * gap.alpha
        * gap.hatch
        * gap.hatch.color
        * gap.legend - Show legend entry for gaps (True by default and if gaps)

        * nan.color
        * nan.alpha
        * nan.hatch
        * nan.hatch.color
        * nan.legend - Show legend entry for nans (True by default and if NaNs)



    """

    ###########################################################################
    def warning(message):
        print("\x1b[31mheatmap() warning: \x1b[0m" + message)

    def calcEdges(y, coord):
        """Caclulate bin ranges given bin centers."""

        # TODO: Set bin width to 1 if y is not datetime.
        # TODO: If datetime, guess cadence by inspecting and warn?

        if len(y) == 1:
            # Put tick at center of bin; make bin have width = 1.
            y = np.array([y[0]-0.5,y[0]+0.5])
        else:
            # y are bin centers
            dy = np.diff(y)
            dyu = np.unique(dy)
            if len(dyu) > 1:
                if coord == 'y':
                    warning('Only bin centers given for y and bin separation distance is not constant.')
                    warning('Bin width assumed based on separation distance and data pickers will not work properly.')
                else:
                    warning('Only bin centers given for x and bin separation distance is not constant.')
                    warning('Bin width assumed based on separation distance and data pickers will not work properly.')
                y = np.append(y, y[-1] + dy[-1])
            else:
                y = np.append(y, y[-1] + dy[0])
                y = y-dyu[0]/2

        return y

    def calcGaps(y, z, coord):

        if coord == 'x':
            z = np.transpose(z)

        havegaps = False
        ynew = []
        for k in range(0, len(y)-1):
            ynew.append(y[k][0])
            if y[k][1] != y[k+1][0]:
                havegaps = True
                break
        if len(y) == 1:
            ynew.append(y[0][0])
            ynew.append(y[0][1])
            y = ynew
        elif not havegaps:
            # Set top-most two bin edges.
            ynew.append(y[k+1][0])
            ynew.append(y[k+1][1])
            y = ynew
        else:
            # Insert NaN rows where gaps
            znew = z[0,:]
            nanrow = np.nan*z[0,:]

            Igaps = []
            ynew = []
            ynew.append(y[0][0])
            if y[0][1] != y[1][0]: # Gap between bins
                ynew.append(y[0][1])
                znew = np.vstack((znew, nanrow))
                Igaps.append(1)

            for k in range(1, len(y)-1):
                ynew.append(y[k][0])
                znew = np.vstack((znew, z[k,:]))
                if y[k][1] != y[k+1][0]: # Gap between bins
                    ynew.append(y[k][1])
                    #print('inserting nan row or column')
                    znew = np.vstack((znew, nanrow))
                    Igaps.append(znew.shape[0]-1)

            # Set top-most two bin edges
            ynew.append(y[k+1][0])
            ynew.append(y[k+1][1])
            znew = np.vstack((znew, z[k+1,:]))

            z = znew

        Igaps = np.asarray(Igaps, dtype=np.int32)
        y = np.array(ynew)

        if coord == 'x':
            z = np.transpose(z)

        return y, z, Igaps

    def adjustCenters(y, yc):
        # Adjusts centers and their labels if nonuniform diff(y)
        dy = np.diff(y)
        dyu = np.unique(dy)
        if len(dyu) > 1:
            # If centers not uniform, they were used as lower edges.
            # Need to adjust center location for ticks and labels.
            ycl = np.copy(y) # y center labels
            yc = np.copy(y[0:-1])
            for i in range(0, y.shape[0]-1):
                yc[i] = y[i] + (y[i+1]-y[i])/2
        else:
            # No adjustment needed. Indicate this with empty ycl.
            ycl = np.array([])

        return yc, ycl

    def array2cmap(X):

        N = X.shape[0]

        # https://stackoverflow.com/questions/48387847/overlaying-two-plots-using-pcolor
        from matplotlib import colors
        r = np.linspace(0., 1., N+1)
        r = np.sort(np.concatenate((r, r)))[1:-1]
        rd = np.concatenate([[X[i, 0], X[i, 0]] for i in range(N)])
        gr = np.concatenate([[X[i, 1], X[i, 1]] for i in range(N)])
        bl = np.concatenate([[X[i, 2], X[i, 2]] for i in range(N)])

        rd = tuple([(r[i], rd[i], rd[i]) for i in range(2 * N)])
        gr = tuple([(r[i], gr[i], gr[i]) for i in range(2 * N)])
        bl = tuple([(r[i], bl[i], bl[i]) for i in range(2 * N)])

        cdict = {'red': rd, 'green': gr, 'blue': bl}
        return colors.LinearSegmentedColormap('my_colormap', cdict, N)
    ###########################################################################

    opts = {
                'logging': False,
                'title': '',
                'xlabel': '',
                'ylabel': '',
                'logx': False,
                'logy': False,
                'backend': 'default',
                'returnimage': False,
                'transparent': False,

                'ztitle': '',
                'zlabel': '',
                'logz': False,

                'edgecolor': None,
                'cmap': None,
                'cmap.numcolors': 32,
                'cmap.name': 'viridis',
                'cmap.clim': None,
                'nan.color': [0.95,0.95,0.95],
                'nan.alpha': 1,
                'nan.hatch': '',
                'nan.hatch.color': [0.1,0.1,0.1] ,
                'nan.legend': True,
                'gap.color': [0,0,0],
                'gap.alpha': 1,
                'gap.hatch': '',
                'gap.hatch.color': [0.95,0.95,0.95],
                'gap.legend': True,
                'logz0.color': [1,1,1],
                'logz0.alpha': 1,
                'logz0.hatch': '',
                'logz0.hatch.color': [0.95,0.95,0.95],
                'logz0.legend': True
            }

    for key, value in kwargs.items():
        if key in opts:
            opts[key] = value
        else:
            warnings.warn('Warning: Ignoring invalid keyword option "%s".' % key, SyntaxWarning)

    if opts['returnimage']:
        # When returnimage=True, the Matplotlib OO API is used b/c it is thread safe.
        # Otherwise, the pyplot API is used. Ideally would always use the OO API,
        # but this has problems with notebooks and showing figure when executing
        # a script from the command line.
        # TODO: Document issues.
        #
        # API differences description:
        # https://www.saltycrane.com/blog/2007/01/how-to-use-pylab-api-vs-matplotlib-api_3134/
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    else:
        from matplotlib import pyplot as plt
        if opts['logging']: print("Using Matplotlib back-end " + matplotlib.get_backend())

    if not opts['cmap.name'] in matplotlib.pyplot.colormaps():
        warning('colormap name "'
                + opts['cmap.name']
                + '" is not in list of known names: '
                + str(matplotlib.pyplot.colormaps())
                + ". Using 'viridis'.")
        opts['cmap.name'] = 'viridis'

    if not opts['cmap']:
        opts['cmap'] = matplotlib.pyplot.get_cmap(opts['cmap.name'], opts['cmap.numcolors'])

    if opts['returnimage']:
        fig = Figure()
        FigureCanvas(fig) # Not used directly, but calling attaches canvas to fig which is used later.
        ax = fig.add_subplot(111)
    else:
        plt.figure()
        fig = plt.gcf()
        ax = plt.gca()

    # Number of x values (columns)
    Nx = z.shape[1] if len(z.shape) == 2 else 1
    # Number of y values (rows)
    Ny = z.shape[0] if len(z.shape) == 2 else 1

    # If y is a matrix, assume it has two columns.
    # First column is lower edge, second is upper edge.
    # If given a two-row matrix, transpose.
    if len(y.shape) > 1: # Bin edges given
        if y.shape[1] != 2 and y.shape[0] == 2:
            warning('If y is a matrix, it should have two columns. Two rows found. Transposing.')
            y = np.transpose(y)
        if y.shape[0] !=2 and y.shape[1] != 2:
            raise ValueError('If y is a matrix, it must have two columns or two rows.')

    if len(x.shape) > 1: # Bin edges given
        if x.shape[1] != 2 and x.shape[0] == 2:
            warning('If x is a matrix, it should have two columns. Two rows found. Transposing.')
            x = np.transpose(x)
        if x.shape[0] !=2 and x.shape[1] != 2:
            raise ValueError('If x is a matrix, it must have two columns or two rows.')

    if not (len(x) == Nx or len(x) == Nx+1):
        raise ValueError('Required: len(x) == z.shape[1] or len(x) == z.shape[1] + 1.')
    if not (len(y) == Ny or len(y) == Ny+1):
        raise ValueError('Required: len(y) == z.shape[0] or len(y) == z.shape[0] + 1.')

    if len(x.shape) == 1 and len(x) == Nx:
        # Centers given. Calculate edges.
        xedges = False
        xc = x
        x = calcEdges(x, 'x')
        xc, xcl = adjustCenters(x, xc)
    else:
        xc = np.array([])
        xedges = True

    if len(y.shape) == 1 and len(y) == Ny:
        # Centers given. Calculate edges.
        yedges = False
        yc = y
        y = calcEdges(y, 'y')
        yc, ycl = adjustCenters(y, yc)
    else:
        yc = np.array([])
        yedges = True

    inan = np.where(np.isnan(z))
    havenans = False
    if np.any(inan) > 0:
        havenans = True

    xgaps = np.array([], dtype=np.int32)
    ygaps = np.array([], dtype=np.int32)
    if len(x.shape) == 2: # x is an matrix
        x, z, xgaps = calcGaps(x, z, 'x')
    if len(y.shape) == 2: # y is an matrix
        y, z, ygaps = calcGaps(y, z, 'y')

    legendh = []
    havegaps = False
    if len(xgaps) > 0 or len(ygaps) > 0:
        # TODO: Add alpha to nancolor and change array2cmap to accept alpha.
        havegaps = True
        cmapg = array2cmap(np.array([opts['gap.color']]))
        zg = np.nan*np.copy(z)
        if len(xgaps) > 0:
            zg[:,xgaps] = 1
        if len(ygaps) > 0:
            zg[ygaps,:] = 1
        if opts['gap.hatch'] == '':
            ax.pcolormesh(x, y, zg, cmap=cmapg)
        else:
            # pcolormesh does not support hatch
            ax.pcolor(x, y, zg, cmap=cmapg, hatch=opts['gap.hatch'],
                      edgecolor=opts['gap.hatch.color'])
        if opts['gap.legend']:
            legendh.append(Patch(facecolor=opts['gap.color'],
                        hatch=opts['gap.hatch']+opts['gap.hatch'],
                        edgecolor=opts['edgecolor'], label='No data'))

    if havenans:
        # TODO: Add alpha to nancolor and change array2cmap to accept alpha.
        cmapn = array2cmap(np.array([opts['nan.color']]))
        zn = np.nan*np.copy(z)
        if havegaps:
            inan = np.where(np.logical_and(np.isnan(z),zg != 1))
        zn[inan] = 1
        if opts['nan.hatch'] == '':
            ax.pcolormesh(x, y, zn, cmap=cmapn)
        else:
            # pcolormesh does not support hatch
            ax.pcolor(x, y, zn, cmap=cmapn, hatch=opts['nan.hatch'],
                      edgecolor=opts['nan.hatch.color'])
        if opts['nan.legend']:
            legendh.append(Patch(facecolor=opts['nan.color'],
                        hatch=opts['nan.hatch']+opts['nan.hatch'],
                        edgecolor=opts['edgecolor'], label='NaN'))

    zc = np.array([])
    categorical = False
    if not 'cmap' in kwargs:
        Ig = ~np.isnan(z)
        if np.all(np.equal(z[Ig], np.int32(z[Ig]))):
            # All z values are integer. Colorbar will label integer categories.
            categorical = True
            zc = np.unique(z[Ig])
            nc = zc[-1]-zc[0] + 1
            cmap = matplotlib.pyplot.get_cmap(opts['cmap.name'], nc)
            # TODO: Warn that cmap_numcolors will be over-ridden if
            # nc != default?

    zmin = np.nanmin(z)
    zmax = np.nanmax(z)
    if zmin < 0 and zmax > 0:
        warning('Colorbar cannot have log scale when all values do not have the same sign.')

    havelogz0 = False
    if opts['logz']:
        # Log scale emits warning if data have NaNs.
        warnings.filterwarnings(action='ignore',
                            message='invalid value encountered in less_equal')
        flipsign = False
        if zmin < 0 and zmax <= 0 and opts['logz']:
            z = -z;
            flipsign = True
        if zmin == 0:
            #warning('Log scale for z requested but min(z) = 0.')
            havelogz0 = True
            logz0idx = np.where(z==0)
            z[z == 0] = np.nan
            havelogz0 = True
            zmin = np.nanmin(z)
        norm = LogNorm(vmin=zmin, vmax=zmax)
        im = ax.pcolormesh(x, y, z, cmap=opts['cmap'], norm=norm,
                           edgecolor=opts['edgecolor'])
        if havelogz0:
            cmapz = array2cmap(np.array([opts['logz0.color']]))
            z = np.nan*z
            z[logz0idx] = 1
            ax.pcolormesh(x, y, z, cmap=cmapz)
            if opts['logz0.legend']:
                legendh.append(Patch(facecolor=opts['logz0.color'],
                                     edgecolor='k', label='0.0'))
    else:
        im = ax.pcolormesh(x, y, z, cmap=opts['cmap'], edgecolor=opts['edgecolor'])

    # TODO: Handle case where > 10.
    # Label every Nth, etc. as needed
    if xedges and x.size <= 10:
        ax.set_xticks(x)
    if xc.size > 0 and xc.size <= 10:
        ax.set_xticks(xc)
        if len(xcl) > 0:
            # Relabel x-ticks b/c nonuniform center spacing.
            ax.set_xticklabels(xcl)

    #for spine in ax.spines.values(): spine.set_edgecolor(None)

    if yedges and y.size <= 10:
        ax.set_yticks(y)
    if yc.size > 0 and yc.size <= 10:
        ax.set_yticks(yc)
        if len(ycl) > 0:
            # Relabel y-ticks b/c nonuniform center spacing.
            ax.set_yticklabels(ycl)

    ax.set_ylim(y[0], y[-1])
    if opts['xlabel']:
        ax.set_xlabel(opts['xlabel'])
    if opts['logx']:
        # TODO: Flip sign if needed.
        ax.set_xscale('log')
    if opts['ylabel']:
        ax.set_ylabel(opts['ylabel'])
    if opts['logy']:
        # TODO: Flip sign if needed.
        ax.set_yscale('log')
    if opts['title']:
        ax.set_title(opts['title'], fontsize=10)

    cb = fig.colorbar(im, ax=ax, pad=0.01)

    if categorical and zc.size <= 10:
        # If number of unique zc values is <= 10, put
        # tick label at center of color patch.
        # If zc > 10, won't be able to tell that ticks don't line
        # up with center of patch, so use default tick positions.
        cb.set_ticks(np.arange(zc[0],zc[-1]+1,1))
        if not opts['cmap.clim']:
            im.set_clim(zc[0]-0.5, zc[-1]+0.5)
        #cb.ax.set_yticklabels(['%d' % x for x in np.arange(zc[0],zc[-1],1)])
    if opts['cmap.clim']:
        im.set_clim(opts['cmap.clim'])

    zt = cb.get_ticks()

    # How to label zmin and zmax without overlap of default labels?
    # Extend clim to next interval? But then one may think actual values in
    # extended range. For now, just warn.
    if zt[0] != zmin:
        #warnings.warn('Lower z limit not labeled.')
        zt = np.concatenate(([zmin],zt))
        #cb.set_ticks(zt)
    if zt[-1] != zmax:
        #warnings.warn('Upper z limit not labeled.')
        zt = np.concatenate((zt,[zmax]))
        #cb.set_ticks(zt)

    cb.set_label(opts['zlabel'], fontsize=10) # On side
    cb.ax.set_title(opts['ztitle'], fontsize=10) # On top

    if opts['logz'] and flipsign:
        # Put negative sign in front of numbers on colorbar
        zlabels = cb.ax.get_yticklabels()
        for i in range(0, len(zlabels)):
            text = zlabels[i].get_text()
            if text != '':
                zlabels[i].set_text('-'+text)
        cb.ax.set_yticklabels(zlabels)

    if isinstance(x[0], datetime.datetime):
        datetick('x', axes=ax)
    if isinstance(y[0], datetime.datetime):
        datetick('y', axes=ax)

    # Set positions of axes and colorbar
    ax.set_position([0.1,0.14,0.8,0.73])
    cb.ax.set_position([0.905,0.14,0.10,0.73])

    # NaN, logz0, and gap legend
    if len(legendh) > 0:
        fig.legend(frameon=False, borderaxespad=0.25, borderpad=0.15,
                   handles=legendh, loc='upper right',
                   fontsize='x-small', ncol=len(legendh))

    if opts['transparent']:
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

    if not opts['returnimage']:
        plt.show()

    return fig, cb
