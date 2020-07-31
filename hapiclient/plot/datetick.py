import warnings
from datetime import datetime
import numpy as np

import matplotlib.dates as mpld
import matplotlib
if matplotlib.get_backend() == 'MacOSX':
    # With MacOSX backend, draw() does not update the ticks 
    # See warning at
    # https://matplotlib.org/3.3.0/tutorials/advanced/blitting.html#sphx-glr-tutorials-advanced-blitting-py
    import sys
    if sys.version_info[0:2] < (3, 6):
        #warnings.filterwarnings("ignore", '.*backend.*', category=UserWarning)
        #the above should work and is better because more specific.
        warnings.simplefilter("ignore", category=UserWarning)
    gui_env = ['Qt5Agg','QT4Agg','GTKAgg','TKAgg','WXAgg']
    for gui in gui_env:
        try:
            #print('Trying ' + gui)
            matplotlib.use(gui, force=True)
            import matplotlib.pyplot as plt
            #print('Success with ' + gui)
            break
        except:
            #print('Failure with ' + gui)
            continue
else:
    try:
        import matplotlib.pyplot as plt
    except:
        #print('Failed: import matplotlib.pyplot as plt')
        gui_env = ['Qt5Agg','QT4Agg','GTKAgg','TKAgg','WXAgg']
        for gui in gui_env:
            try:
                matplotlib.use(gui, force=True)
                import matplotlib.pyplot as plt
                break
            except:
                continue
                
def datetick(dir, **kwargs):
    '''
    datetick('x') or datetick('y') formats the major and minor tick labels
    of the current figure.
    
    datetick('x', axes=ax) or datetick('y', axes=ax) formats the given
    axes `ax`.

    Example:
    --------
        import datetime as dt
        import numpy as np
        import matplotlib.pyplot as plt
        from hapiclient.plot.datetick import datetick
        d1 = dt.datetime(1900, 1, 2)
        d2 = dt.datetime.fromordinal(10 + dt.datetime.toordinal(d1))
        x = np.array([d1, d2], dtype=object)
        y = [0.0,1.0]
        plt.clf()
        plt.plot(x, y)
        datetick('x')
    '''

    # Based on spacepy/plot/utils.py on 07/10/2017, but many additions.
    
    # TODO: Account for leap years instead of using 367, 366, etc.
    # TODO: Use numsize() to determine if figure width and height
    #       will cause overlap when default number major tick labels is used.
    # TODO: If time[0].day > 28, need to make first tick at time[0].day = 28
    #       as needed.
    # TODO: If first data point has fractional seconds, the plot won't have
    #       a major x-label right below it. This is due to the fact that
    #       MicrosecondLocator() does not take a keyword argument of
    #       "bymicroseconds".
    # TODO: Adjust lower and upper limits as in 366*8 span

    def millis(x, pos):
        x = matplotlib.dates.num2date(x)
        label = x.strftime('.%f')
        label = label[0:3]
        #label = label.rstrip(".")
        return label
    

    DOPTS = {}
    DOPTS.update({'debug': False})
    DOPTS.update({'set_cb': True})
    DOPTS.update({'axes': None})

    # Override defaults
    for key, value in kwargs.items():
        if key in DOPTS:
            DOPTS[key] = value
        else:
            print('Warning: Keyword option "%s" is not valid.' % key)

    if 'axes' in kwargs:
        axes = kwargs['axes']
        fig = axes.figure
    else:
        axes = plt.gca()
        fig = plt.gcf()
    
    debug = DOPTS['debug']

    def on_xlims_change(ax): datetick('x', axes=ax, set_cb=False)
    def on_ylims_change(ax): datetick('y', axes=ax, set_cb=False)
    def draw(fig): fig.canvas.draw()

    bbox = axes.dataLim

    if dir == 'x':        
        datamin = bbox.x0
        datamax = bbox.x1
        lim = axes.get_xlim()
    else:
        datamin = bbox.y0
        datamax = bbox.y1    
        lim = axes.get_ylim()

    try:
        mpld.num2date(lim[0])
    except:
        raise ValueError('timeseries(): Lower axis limit of %f is not a valid Matplotlib datenum' % lim[0])
    try:
        mpld.num2date(lim[1])
    except:
        raise ValueError('timeseries(): Upper axis limit of %f is not a valid Matplotlib datenum' % lim[1])
    try:
        mpld.num2date(datamin)
    except:
        raise ValueError('timeseries(): Minimum data value of %f is not a valid Matplotlib datenum' % datamin)
    try:
        mpld.num2date(datamax)
    except:
        raise ValueError('timeseries(): Maximum data value of %f is not a valid Matplotlib datenum' % datamax)

    tmin = np.max((lim[0], datamin))
    tmax = np.min((lim[1], datamax))
            
    time = mpld.num2date((tmin,tmax))

    if debug == True:
        print('Data min time: %f' % datamin)
        print('Data max time: %f' % datamax)
    
    deltaT = time[-1] - time[0]
    nDays  = deltaT.days
    nHours = deltaT.days * 24.0 + deltaT.seconds/3600.0
    nSecs  = deltaT.total_seconds()
    if debug == True:
        print("Total seconds: %s" % deltaT.total_seconds())

    # fmt is format of the tick labels
    # fmt2 contains additional information that is used for the first tick label
    # or when there is a majore change. For example, if
    # fmt = %M:%S and fmt2 = %H, the labels will have only minute and hour and
    # the first tick will have a label of %M:%S\n%H. If there is a change
    # in hour somewhere on the axis, that label will include the new hour.
    
    # Note that interval=... is specified even when it would seem to be
    # redundant. It is needed to workaround the bug discussed at
    # https://stackoverflow.com/questions/31072589/matplotlib-date-ticker-exceeds-locator-maxticks-error-for-no-apparent-reason
    if deltaT.total_seconds() < 0.1:
        # < 0.1 second
        # At this level of zoom, would need original datetime data
        # which has not been converted by date2num and then re-plot
        # using integer number of milliseconds. E.g., call
        # plotd(dtobj,y)
        # where
        # t = dtobj converted to milliseconds since first array value
        # plotd() calls
        # plot(t,y)
        # and then makes first label indicate %Y-%m-%dT%H:%M:%S
        warnings.warn("Warning: Cannot create accurate time labels with this time resolution.")
        # This does not locate microseconds.
        Mtick = mpld.MicrosecondLocator(interval=10000)
        mtick = mpld.MicrosecondLocator(interval=2000)
        from matplotlib.ticker import FuncFormatter
        fmt = FuncFormatter(millis)
        fmt2  = '%H:%M:%S\n%Y-%m-%d'
    if deltaT.total_seconds() < 0.5:
        # < 0.5 seconds
        # Locators don't locate at this resolution. 
        # Need to do this manually. See comment above.
        warnings.warn("Warning: Cannot create accurate time labels with this time resolution.")
        Mtick = mpld.MicrosecondLocator(interval=50000)
        mtick = mpld.MicrosecondLocator(interval=10000)
        from matplotlib.ticker import FuncFormatter
        fmt = FuncFormatter(millis)
        fmt2  = '%H:%M:%S\n%Y-%m-%d'
    if deltaT.total_seconds() < 1:
        # < 1 second
        # https://matplotlib.org/api/dates_api.html#matplotlib.dates.MicrosecondLocator
        # MircosecondLocator() does not have a "bymicrosecond" option. If
        # First point is not at zero microseconds, it won't be labeled.
        Mtick = mpld.MicrosecondLocator(interval=100000)
        mtick = mpld.MicrosecondLocator(interval=20000)
        from matplotlib.ticker import FuncFormatter
        fmt = FuncFormatter(millis)
        #fmt   = mpld.DateFormatter('%M:%S.%f')
        fmt2  = '%H:%M:%S\n%Y-%m-%d'
    elif deltaT.total_seconds() < 5:
        # < 5 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 1)) )
        mtick = mpld.MicrosecondLocator(interval=200000)
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 10:
        # < 10 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 1)) )
        mtick = mpld.MicrosecondLocator(interval=500000)
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 20:
        # < 20 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 2)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 1)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 30:
        # < 30 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 5)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 1)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60:
        # < 1 minute
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 10)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 2)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*2:
        # < 2 minutes
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 20)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 5)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*3:
        # < 3 minutes
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 20)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 5)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*5:
        # < 5 minutes
        Mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 30)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 10)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*10:
        # < 10 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 1)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 15)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*20:
        # < 20 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 2)) )
        mtick = mpld.SecondLocator(bysecond=list(range(0, 60, 30)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*30:
        # < 30 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 5)) )
        mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 1)) )
        fmt   = mpld.DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif deltaT.total_seconds() < 60*60:
        # < 60 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 10)) )
        mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 2)) )
        fmt   = mpld.DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 2:
        Mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 15)) )
        mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 5)) )
        fmt   = mpld.DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 4:
        Mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 20)) )
        mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 5)) )
        fmt   = mpld.DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 6:
        Mtick = mpld.HourLocator(byhour=list(range(0,24,1)) )
        mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 10)) )
        fmt   = mpld.DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 12:
        Mtick = mpld.HourLocator(byhour=list(range(0,24,2)) )
        mtick = mpld.MinuteLocator(byminute=list(range(0, 60, 30)) )
        fmt   = mpld.DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 24:
        # < 1 day
        Mtick = mpld.HourLocator(byhour=list(range(0, 24, 3)) )
        mtick = mpld.HourLocator(byhour=list(range(0, 24, 1)) )
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 48:
        # < 2 days
        Mtick = mpld.HourLocator(byhour=list(range(0, 24, 4)) )
        mtick = mpld.HourLocator(byhour=list(range(0, 24, 2)) )
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 72:
        # < 3 days
        Mtick = mpld.HourLocator(byhour = list(range(0, 24, 6)))
        mtick = mpld.HourLocator(byhour = list(range(0, 24, 3)))
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 96:
        # < 4 days
        Mtick = mpld.HourLocator(byhour = list(range(0, 24, 12)))
        mtick = mpld.HourLocator(byhour = list(range(0, 24, 3)))
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif deltaT.days < 8:
        Mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 1)))
        mtick = mpld.HourLocator(byhour=list(range(0, 24, 4)))
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 16:
        Mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 1)))
        mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 1)))
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 32:
        Mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 4)))
        mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 1)))
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 60:
        Mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 7)))
        mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 1)))
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 183:
        Mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 1)))
        mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 7)))
        fmt   = mpld.DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 367:
        Mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 1)))
        mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 1)))
        fmt   = mpld.DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 366*2:
        Mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 2)))
        mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 1)))
        fmt   = mpld.DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 366*8:
        Mtick = mpld.YearLocator(1)
        mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 4)))
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*15:
        to = axes.lines[0].get_xdata()[0]
        tf = axes.lines[0].get_xdata()[-1]
        print(to)
        print(tf)
        # Ideally would set byyear=list(range(to.year, tf.year,2)) but
        # byyear is not a kwarg. Would need to something like
        # https://stackoverflow.com/questions/48428729/matplotlib-dates-yearlocator-with-odd-intervals
        Mtick = mpld.YearLocator(1) 
        mtick = mpld.YearLocator(1)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
        if False:
            xl = axes.get_xlim()
            a = mpld.num2date(xl[0])
            print(a)
            import pdb;pdb.set_trace()
            a = mpld.date2num(a.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
            b = mpld.num2date(xl[1])
            b = mpld.date2num(b.replace(year=(b.year+1), month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
            axes.set_xlim([a, b])

    elif deltaT.days < 366*40:
        Mtick = mpld.YearLocator(5)
        mtick = mpld.YearLocator(1)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*100:
        Mtick = mpld.YearLocator(10)
        mtick = mpld.YearLocator(2)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*200:
        Mtick = mpld.YearLocator(20)
        mtick = mpld.YearLocator(5)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
    else:
        Mtick = mpld.YearLocator(50)
        mtick = mpld.YearLocator(10)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''

    xt = axes.get_xticks()
    xl = axes.get_xlim()

    if debug:
        print("Default xlim[0]:    %s" % mpld.num2date(xl[0]))
        print("Default xlim[1]:    %s" % mpld.num2date(xl[1]))
        print("Default xticks[0]:  %s" % mpld.num2date(xt[0]))
        print("Default xticks[-1]: %s" % mpld.num2date(xt[-1]))
    
    if debug:
        print("Start: %s" % mpld.num2date(xl[0]))
        print("Stop:  %s" % mpld.num2date(xl[1]))
        for i in range(0,len(xt)):
            print("Tick: %s" % mpld.num2date(xt[i]))

    if dir == 'x':
        axes.xaxis.set_major_locator(Mtick)
        axes.xaxis.set_minor_locator(mtick)
        axes.xaxis.set_major_formatter(fmt)
        draw(fig) # Render new labels so updated for next line
        labels = [item.get_text() for item in axes.get_xticklabels()]
        ticks = axes.get_xticks()
        time = mpld.num2date(ticks)
    else:
        axes.yaxis.set_major_locator(Mtick)
        axes.yaxis.set_minor_locator(mtick)
        axes.yaxis.set_major_formatter(fmt)
        draw(fig) # Render new labels so updated for next line
        labels = [item.get_text() for item in axes.get_yticklabels()]
        ticks = axes.get_yticks()
        time = mpld.num2date(ticks)

    if debug:
        xl = axes.get_xlim()
        print(mpld.num2date(xl[0]))
        print(mpld.num2date(ticks[0]))        
        print(mpld.num2date(xl[1]))
        print(mpld.num2date(ticks[-1]))
        if ticks[0] < xl[0]:
            print('Left-most tick label will be clipped.')
        if ticks[-1] > xl[1]:
            print('Right-most tick label will be clipped.')
        for i in range(0,len(ticks)):
            print("Tick: %s" % mpld.num2date(ticks[i]))

    if fmt2 != '':
        first = 0
        if ticks[0] < xl[0]:
            # Work-around for bug in Matplotlib where left-most tick is less than
            # lower x-limit.
            first = 1

        # Always apply fmt2 to first tick label
        labels[first] = '%s\n%s' % (labels[first], datetime.strftime(time[first], fmt2))

        for i in range(first+1,len(time)):
            # First label will always have fmt applied.
            # Modify labels after first under certain conditions.            
            modify = False 
            
            if time[i].year > time[i-1].year:
                modify = True
            if nDays < 60 and time[i].month > time[i-1].month:
                modify = True
            if nDays < 4 and time[i].day > time[i-1].day:
                modify = True
            if nSecs < 60*30 and time[i].hour > time[i-1].hour:
                modify = True
            if nSecs < 1 and time[i].minute > time[i-1].minute:
                modify = True
            if nSecs < 1 and time[i].second > time[i-1].second:
                modify = True

            if not modify: continue

            if i == first + 1 and dir == 'x':
                # If first two major tick labels have fmt2 applied, the will
                # likely run together. This keeps fmt2 label for second major
                # tick.
                #labels[i] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(ticks[i]), fmt2))
                pass
            else:
                labels[i] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(ticks[i]), fmt2))

    if dir == 'x':            
        axes.set_xticklabels(labels)
    if dir == 'y':            
        axes.set_yticklabels(labels)

    # Trigger update of ticks when limits change due to user interaction.
    if DOPTS['set_cb']:
        if dir == 'x':
            axes.callbacks.connect('xlim_changed', on_xlims_change)
        else:
            axes.callbacks.connect('ylim_changed', on_ylims_change)

def numsize():
    '''Returns (width, height) of number '0' in pixels'''
    # Not used.
    # Based on https://stackoverflow.com/q/5320205
    # TODO: numsize(fig, dir) should inspect fig to get used fonts
    # for dir='x' and dir='y' and get bounding box for x and y labels.
    r = plt.figure().canvas.get_renderer()
    t = plt.text(0.5, 0.5, '0')    
    bb = t.get_window_extent(renderer=r)
    w = bb.width
    h = bb.height
    plt.close()
    return (w,h)
                