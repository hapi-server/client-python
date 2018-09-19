import matplotlib.dates as mpld
from datetime import datetime
import numpy as np

# To allow to run from command line, find a back-end that works
import matplotlib
gui_env = ['Qt5Agg','QT4Agg','GTKAgg','TKAgg','WXAgg']
for gui in gui_env:
    try:
        #print("xtesting", gui)
        matplotlib.use(gui,warn=False, force=True)
        import matplotlib.pyplot as plt
        break
    except:
        continue

def datetick(dir, **kwargs):
    '''
    datetick('x') or datetick('y') formats the major and minor tick labels
    of the current plot.
    Example:
        d1 = dt.datetime(1900, 1, 2)
        d2 = datetime.fromordinal(i + datetime.toordinal(d1))
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
    
    def on_xlims_change(ax): datetick('x', set_cb=False)
    def on_ylims_change(ax): datetick('y', set_cb=False)
    
    def millis(x, pos):
        'The two args are the value and tick position'
        return '$%1.1fM' % (x*1e-6)

    debug = False
    
    axes = plt.gca()
    fig = plt.gcf()
    
    # By default, trigger update of ticks when limits
    # change due to user interaction.
    set_cb = True
    if 'set_cb' in kwargs:
        set_cb = kwargs['set_cb']
    if set_cb == True:
        # Trigger update of ticks when limits change.
        if dir == 'x':
            axes.callbacks.connect('xlim_changed', on_xlims_change)
        else:
            axes.callbacks.connect('ylim_changed', on_ylims_change)
 
    line = axes.lines[0]
    datamin = mpld.date2num(line.get_xdata()[0])
    datamax = mpld.date2num(line.get_xdata()[-1])
    if debug == True:
        print('Data min time: %f' % datamin)
        print('Data max time: %f' % datamax)

    xlim = axes.get_xlim()

    tmin = np.max((xlim[0], datamin))
    tmax = np.min((xlim[1], datamax))
    
    if dir == 'x':
        time = mpld.num2date((tmin,tmax))
    else:
        time = mpld.num2date(axes.get_ylim())
    
    deltaT = time[-1] - time[0]
    nHours = deltaT.days * 24.0 + deltaT.seconds/3600.0
    if debug == True:
        print("Total seconds: %s" % deltaT.total_seconds())

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
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second,60,1)) )
        mtick = mpld.MicrosecondLocator(interval=100000)
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 5:
        # < 5 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 1)) )
        mtick = mpld.MicrosecondLocator(interval=200000)
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 10:
        # < 10 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 1)) )
        mtick = mpld.MicrosecondLocator(interval=500000)
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 20:
        # < 20 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 2)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 1)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 30:
        # < 30 seconds
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 5)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 1)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60:
        # < 1 minute
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 10)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 2)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*2:
        # < 2 minutes
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 20)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 5)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*3:
        # < 3 minutes
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 20)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 5)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*5:
        # < 5 minutes
        Mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 30)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 10)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*10:
        # < 10 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 1)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 15)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*20:
        # < 20 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 2)) )
        mtick = mpld.SecondLocator(bysecond=list(range(time[0].second, 60, 30)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*30:
        # < 30 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 5)) )
        mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 1)) )
        fmt   = mpld.DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 60*60:
        # < 60 minutes
        Mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 10)) )
        mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 2)) )
        fmt   = mpld.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 2:
        Mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 15)) )
        mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 5)) )
        fmt   = mpld.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 4:
        Mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 20)) )
        mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 5)) )
        fmt   = mpld.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 6:
        Mtick = mpld.HourLocator(byhour=list(range(time[0].hour,24,1)) )
        mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 10)) )
        fmt   = mpld.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 12:
        Mtick = mpld.HourLocator(byhour=list(range(time[0].hour,24,2)) )
        mtick = mpld.MinuteLocator(byminute=list(range(time[0].minute, 60, 30)) )
        fmt   = mpld.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 24:
        # < 1 day
        Mtick = mpld.HourLocator(byhour=list(range(time[0].hour, 24, 4)) )
        mtick = mpld.HourLocator(byhour=list(range(time[0].hour, 24, 1)) )
        fmt   = mpld.DateFormatter('%H:%M:%S')
        fmt2  = '%Y-%m-%d'
    elif nHours < 48:
        # < 2 days
        Mtick = mpld.HourLocator(byhour = [0, 3, 6, 9, 12, 15, 18, 21])
        mtick = mpld.HourLocator(byhour = list(range(24)))
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 72:
        # < 3 days
        Mtick = mpld.HourLocator(byhour = [0, 6, 12, 18])
        mtick = mpld.HourLocator(byhour = list(range(0, 24, 3)))
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 96:
        # < 4 days
        Mtick = mpld.HourLocator(byhour = [0, 12])
        mtick = mpld.HourLocator(byhour = list(range(0, 24, 3)))
        fmt   = mpld.DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif deltaT.days < 8:
        Mtick = mpld.DayLocator(bymonthday=list(range(32)))
        mtick = mpld.HourLocator(byhour=list(range(0, 24, 4)))
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 16:
        Mtick = mpld.DayLocator(bymonthday=list(range(time[0].day, 32, 2)))
        mtick = mpld.DayLocator(interval=1)
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 32:
        Mtick = mpld.DayLocator(bymonthday=list(range(time[0].day, 32, 4)))
        mtick = mpld.DayLocator(interval=1)
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 60:
        Mtick = mpld.DayLocator(bymonthday=list(range(time[0].day, 32, 7)))
        mtick = mpld.DayLocator(interval=2)
        fmt   = mpld.DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 183:
        Mtick = mpld.MonthLocator(bymonthday=time[0].day, interval=2)
        mtick = mpld.MonthLocator(bymonthday=time[0].day, interval=1)
        if time[0].day == 1:
            fmt   = mpld.DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            fmt   = mpld.DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 367:
        Mtick = mpld.MonthLocator(bymonth=list(range(1,13,4)), bymonthday=time[0].day)
        if time[0].day == 1:
            mtick = mpld.MonthLocator(bymonthday=time[0].day, interval=1)
            fmt   = mpld.DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            mtick = mpld.MonthLocator(bymonthday=time[0].day, interval=1)
            fmt   = mpld.DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 366*2:
        Mtick = mpld.MonthLocator(bymonth=list(range(1,13,6)), bymonthday=time[0].day)
        mtick = mpld.MonthLocator(bymonthday=time[0].day, interval=1)
        if time[0].day == 1:
            fmt   = mpld.DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            fmt   = mpld.DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 366*8:
        Mtick = mpld.YearLocator()
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

    # Force first time value to be labeled for axis locator
    xt = axes.get_xticks()
    xl = axes.get_xlim()
    if debug == True:
        print("Default xlim[0]:    %s" % mpld.num2date(xl[0]))
        print("Default xlim[1]:    %s" % mpld.num2date(xl[1]))
        print("Default xticks[0]:  %s" % mpld.num2date(xt[0]))
        print("Default xticks[-1]: %s" % mpld.num2date(xt[-1]))

    fig.canvas.draw()
    xt = np.insert(xt,0,xl[0])
    axes.set_xticks(xt)

    if False:
        print("Start: %s" % mpld.num2date(xl[0]))
        print("Stop:  %s" % mpld.num2date(xl[1]))
        for i in range(0,len(xt)):
            print("Tick: %s" % mpld.num2date(xt[i]))

    fig.canvas.draw() 
    if dir == 'x':
        axes.xaxis.set_major_locator(Mtick)
        axes.xaxis.set_minor_locator(mtick)
        axes.xaxis.set_major_formatter(fmt)
        fig.canvas.draw() # Render new labels so updated for next line
        labels = [item.get_text() for item in axes.get_xticklabels()]
    else:
        axes.yaxis.set_major_locator(Mtick)
        axes.yaxis.set_minor_locator(mtick)
        axes.yaxis.set_major_formatter(fmt)
        fig.canvas.draw() # Render new labels so updated for next line
        labels = [item.get_text() for item in axes.get_yticklabels()]

    labels[0] = '%s\n%s' % (labels[0],datetime.strftime(time[0],fmt2))
    xt = axes.get_xticks()
    time = mpld.num2date(xt)
    if fmt2 != '':
        for i in range(1,len(time)):
            if time[i].year > time[i-1].year:
                labels[i] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(xt[i]), fmt2))
            if deltaT.days > 1 and time[i].month > time[i-1].month:
                labels[i] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(xt[i]), fmt2))
            if nHours < 96 and time[i].day > time[i-1].day:
                labels[i] = '%s\n%s' % (labels[i], datetime.strftime(mpld.num2date(xt[i]), fmt2))
            
    if dir == 'x':            
        axes.set_xticklabels(labels)
    if dir == 'y':            
        axes.set_yticklabels(labels)        

def numsize():
    '''Returns (width, height) of number '0' in pixels'''
    # Not used.
    # Based on https://stackoverflow.com/q/5320205
    # TODO: numsize(fig,dir) should inspect fig to get used fonts
    # for dir='x' and dir='y' and get bounding box for x and y labels.
    r = plt.figure().canvas.get_renderer()
    t = plt.text(0.5, 0.5, '0')    
    bb = t.get_window_extent(renderer=r)
    w = bb.width
    h = bb.height
    plt.close()
    return (w,h)
                