import matplotlib.dates as mpld
from datetime import datetime
import numpy as np

# To allow to run from command line, find a back-end that works
import matplotlib
gui_env = ['Qt5Agg','QT4Agg','GTKAgg','TKAgg','WXAgg']
for gui in gui_env:
    try:
        matplotlib.use(gui,warn=False, force=True)
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
        
    def millis(x, pos):
        'The two args are the value and tick position'
        return '$%1.1fM' % (x*1e-6)

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

    # Trigger update of ticks when limits change due to user interaction.
    if DOPTS['set_cb']:
        if dir == 'x':
            axes.callbacks.connect('xlim_changed', on_xlims_change)
        else:
            axes.callbacks.connect('ylim_changed', on_ylims_change)

    bbox = axes.dataLim

    if dir == 'x':        
        datamin = bbox.x0
        datamax = bbox.x1
        lim = axes.get_xlim()
    else:
        datamin = bbox.y0
        datamax = bbox.y1    
        lim = axes.get_ylim()

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

    # Note that interval=... is specified even when it would seem to be
    # redundant. It is needed to workaround the bug discussed at
    # https://stackoverflow.com/questions/31072589/matplotlib-date-ticker-exceeds-locator-maxticks-error-for-no-apparent-reason
    if deltaT.total_seconds() < .1:
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
        if debug == True:
            print(line.get_xdata())
            print("Warning: Cannot create accurate time labels with this time resolution.")
        # This does not locate microseconds.
        from matplotlib.ticker import FuncFormatter
        formatter = FuncFormatter(millis)
        Mtick = mpld.MicrosecondLocator(formatter)
        mtick = mpld.MicrosecondLocator(interval=1000)
        fmt   = mpld.DateFormatter('%M:%S:%f')
        fmt2  = '%Y-%m-%dT%H'
    if deltaT.total_seconds() < 1:
        # < 1 second
        #import pdb; pdb.set_trace()
        #Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        # https://matplotlib.org/api/dates_api.html#matplotlib.dates.MicrosecondLocator
        # MircosecondLocator() does not have a "bymicrosecond" option. If
        # First point is not at zero microseconds, it won't be labeled.
        Mtick = mpld.MicrosecondLocator(interval=200000)
        mtick = mpld.MicrosecondLocator(interval=100000)
        #fmt   = mpld.DateFormatter('%M:%S')
        fmt   = mpld.DateFormatter('%M:%S.%f')
        fmt2  = '%Y-%m-%dT%H'
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
        Mtick = mpld.MonthLocator(bymonth=list(range(1,13,1)))
        mtick = mpld.DayLocator(bymonthday=list(range(1, 32, 7)))
        fmt   = mpld.DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 367:
        Mtick = mpld.MonthLocator(bymonth=list(range(1,13,1)))
        mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 1)))
        fmt   = mpld.DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 366*2:
        Mtick = mpld.MonthLocator(bymonth=list(range(1,13,2)))
        mtick = mpld.MonthLocator(bymonth=list(range(1, 13, 1)))
        fmt   = mpld.DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 366*8:
        Mtick = mpld.YearLocator(1)
        mtick = mpld.MonthLocator(bymonth=7)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*15:
        Mtick = mpld.YearLocator(2)
        mtick = mpld.YearLocator(1)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''
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
        mtick = mpld.YearLocator(byyear=10)
        fmt   = mpld.DateFormatter('%Y')
        fmt2  = ''

    xt = axes.get_xticks()
    xl = axes.get_xlim()
    if debug:
        print("Default xlim[0]:    %s" % mpld.num2date(xl[0]))
        print("Default xlim[1]:    %s" % mpld.num2date(xl[1]))
        print("Default xticks[0]:  %s" % mpld.num2date(xt[0]))
        print("Default xticks[-1]: %s" % mpld.num2date(xt[-1]))

    def draw(fig):
        # Render new ticks and tick labels
        fig.canvas.draw()
    
    axes.set_xticks(xt)

    if debug:
        print("Start: %s" % mpld.num2date(xl[0]))
        print("Stop:  %s" % mpld.num2date(xl[1]))
        for i in range(0,len(xt)):
            print("Tick: %s" % mpld.num2date(xt[i]))

    draw(fig)
    
    if dir == 'x':
        axes.xaxis.set_major_locator(Mtick)
        axes.xaxis.set_minor_locator(mtick)
        axes.xaxis.set_major_formatter(fmt)
        #fig.canvas.draw() 
        draw(fig)
        labels = [item.get_text() for item in axes.get_xticklabels()]
        ticks = axes.get_xticks()
        time = mpld.num2date(ticks)
    else:
        axes.yaxis.set_major_locator(Mtick)
        axes.yaxis.set_minor_locator(mtick)
        axes.yaxis.set_major_formatter(fmt)
        #fig.canvas.draw() # Render new labels so updated for next line
        draw(fig)
        labels = [item.get_text() for item in axes.get_yticklabels()]
        ticks = axes.get_yticks()
        time = mpld.num2date(ticks)

    if debug:
        print(labels)

    if fmt2 != '':
        for i in range(1,len(time)):
            modify = False
            if time[i].year > time[i-1].year:
                modify = True
            if nDays < 60 and time[i].month > time[i-1].month:
                modify = True
            if nDays < 4 and time[i].day > time[i-1].day:
                modify = True
            if nSecs < 60*30 and time[i].hour > time[i-1].hour:
                modify = True

            if i == 1:
                # If first two major tick labels have fmt2 applied, the will
                # likely run together. This keeps fmt2 label for second major tick.
                if modify and dir == 'x':
                    labels[1] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(ticks[i]), fmt2))
                else:
                    labels[0] = '%s\n%s' % (labels[0], datetime.strftime(time[0], fmt2))
            else:
                if modify:
                    labels[i] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(ticks[i]), fmt2))

    if dir == 'x':            
        axes.set_xticklabels(labels)
    if dir == 'y':            
        axes.set_yticklabels(labels)

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
                