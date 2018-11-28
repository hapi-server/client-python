import datetime   
import warnings 
import numpy as np

from hapiclient.plot.datetick import datetick

def timeseries(t, y, **kwargs):

    # https://matplotlib.org/users/customizing.html
    
    opts = {
                'figsize': (7, 3),
                'dpi': 144,
                'xlabel': '',
                'ylabel': '',
                'legendlabels': [],
                'title': '',
                'logx': '',
                'logy': '',
                'rc': {},
                'figure.facealpha': 1,
                'axes.facealpha': 1,
                'returnimage': False,
                'logging': False,
                'style': 'fast'
            }
    
    # Override defaults
    for key, value in kwargs.items():
        if key in opts:
            opts[key] = value
        else:
            warnings.warn('Warning: Ignoring invalid keyword option "%s".' % key)

    # To allow to run from command line, find a back-end that works
    import matplotlib
    if not opts['returnimage']:
        gui_env = ['Qt5Agg', 'QT4Agg', 'GTKAgg', 'TKAgg', 'WXAgg']
        if opts['logging']: print("Looking for first Matplotlib back-end available in list " +  str(gui_env))
        for gui in gui_env:
            try:
                matplotlib.use(gui, warn=False, force=True)
                from matplotlib import pyplot as plt
                break
            except:
                continue
        if opts['logging']: print("Using Matplotlib back-end " + gui)
    else:
        # When returnimage=True, the Matplotlib OO API is used b/c it is thread safe.
        # Otherwise, the pyplot API is used. Ideally would always use the OO API,
        # but this has problems with notebooks and showing figure when executing
        # a script from the command line. See also
        # https://www.saltycrane.com/blog/2007/01/how-to-use-pylab-api-vs-matplotlib-api_3134/        
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    #print(matplotlib.style.available)
    # matplotlib.style.us may cause a problem in server mode because this changes
    # global settings. Would need to use, e.g., 

    if False:
        style = kwargs['style'] if 'style' in kwargs else ''
        if style:
            if style in matplotlib.style.available:
                matplotlib.style.use(style)
            else:
                warnings.warn('style "' + style + '" is not in list of known styles: ' + str(matplotlib.style.available))

    if y.shape[0] < 11:
        props = {'linestyle': 'none', 'marker': '.', 'markersize': 16}
    elif y.shape[0] < 101:
        props = {'lineStyle': '-', 'linewidth': 2, 'marker': '.', 'markersize': 8}
    else:
        props = {}

    ylabels = []
    
    if issubclass(y.dtype.type, np.flexible):
        # See https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.scalars.html
        # for diagram of subclasses.
        # Find unique strings and give each an integer value.
        # Modify tick labels to correspond to unique strings
        yu = np.unique(y)
        if len(yu) > 20:
            # Too many labels in this case. One option is to find
            # number of unique first characters and change labels to
            # "first character" and then warn. If number of unique first
            # characters < 21, try number of unique second characters, etc.
            raise ValueError('Can only plot strings if number of unique strins < 21')
        yi = np.zeros((y.shape))
        for i in range(0, len(yu)):
            yi[y == yu[i]] = i
        ylabels = yu
        y = yi

    rclib =  matplotlib.style.library
    rc = dict(rclib[opts['style']]) # default rc parameters for style.

    # Override defaults with given rc parameters
    for key in opts['rc']:
        rc[key] = opts['rc'][key]
    
    with matplotlib.rc_context(rc=rc):
        # Setting stylesheet method: https://stackoverflow.com/a/22794651/1491619
        if opts['returnimage']:
            # See note above about OO API for explanation for why this is
            # done differently if returnimage=True
            plt = None
            fig = Figure(figsize=opts['figsize'])
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.plot(t, y, **props)
            ax.set(ylabel=opts['ylabel'], xlabel=opts['xlabel'], title=opts['title'])
        else:
            plt.figure(figsize=opts['figsize'], dpi=opts['dpi'])
            plt.clf()
            plt.plot(t, y, **props)
            plt.gcf().canvas.set_window_title(opts['title'])
            plt.ylabel(opts['ylabel'])
            plt.xlabel(opts['xlabel'])
            plt.title(opts['title'])
            fig, canvas, ax = (plt.gcf(), plt.gcf().canvas, plt.gca())

    if len(ylabels) > 0:
        ax.set_yticks(np.unique(y))
        ax.set_yticklabels(ylabels)
    ax.grid()
    if isinstance(t.take(0), datetime.datetime):
        datetick('x', axes=ax)
    if isinstance(y.take(0), datetime.datetime):
        datetick('y', axes=ax)

    fig.patch.set_alpha(opts['figure.facealpha'])
    ax.patch.set_alpha(opts['axes.facealpha'])

    if not opts['returnimage']:
        plt.show()

    return plt, fig, canvas, ax
