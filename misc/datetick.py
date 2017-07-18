import matplotlib.pyplot as plt 
from matplotlib.dates import *
from datetime import datetime
import numpy as np

def numsize():
    # Returns (width, height) of number '0' in pixels
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

def on_xlims_change(ax): datetick('x',set_cb=False)
def on_ylims_change(ax): datetick('y',set_cb=False)

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
    # will cause overlap when default number major tick labels is used.

    axes = plt.gca()
    fig = plt.gcf()

    # By default, trigger update of ticks when limits change.
    set_cb = True
    if 'set_cb' in kwargs:
        set_cb = kwargs['set_cb']
    if set_cb == True:
        # Trigger update of ticks when limits change.
        if dir == 'x':
            axes.callbacks.connect('xlim_changed', on_xlims_change)
        else:
            axes.callbacks.connect('ylim_changed', on_ylims_change)

    if dir == 'x':
        time = num2date(axes.get_xlim())
    else:
        time = num2date(axes.get_ylim())
    
    deltaT = time[-1] - time[0]
    nHours = deltaT.days * 24.0 + deltaT.seconds/3600.0

    # TODO: If time[0].day > 28, need to make first tick at time[0].day = 28
    # as needed.

    if deltaT.total_seconds() < 300:
        Mtick = SecondLocator(bysecond=list(range(0,60,10)) )
        mtick = SecondLocator(bysecond=list(range(60)), interval=2)
        fmt   = DateFormatter('%M:%S')
        fmt2  = '%Y-%m-%dT%H'
    elif deltaT.total_seconds() < 600:
        Mtick = MinuteLocator(byminute=list(range(0,60,2)) )
        mtick = MinuteLocator(byminute=list(range(60)), interval=1)
        fmt   = DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < .5:
        Mtick = MinuteLocator(byminute=list(range(0,60,5)) )
        mtick = MinuteLocator(byminute=list(range(60)), interval=5)
        fmt   = DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 1:
        Mtick = MinuteLocator(byminute = [0,15,30,45])
        mtick = MinuteLocator(byminute = list(range(60)), interval = 5)
        fmt   = DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 2:
        Mtick = MinuteLocator(byminute=[0,15,30,45])
        mtick = MinuteLocator(byminute=list(range(60)), interval=5)
        fmt   =  DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 4:
        Mtick = MinuteLocator(byminute = [0,30])
        mtick = MinuteLocator(byminute = list(range(60)), interval = 10)
        fmt   = DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 12:
        Mtick = HourLocator(byhour = list(range(24)), interval = 2)
        mtick = MinuteLocator(byminute = [0,15,30,45])
        fmt   = DateFormatter('%H:%M')
        fmt2  = '%Y-%m-%d'
    elif nHours < 24:
        Mtick = HourLocator(byhour = [0,3,6,9,12,15,18,21])
        mtick = HourLocator(byhour = list(range(24)))
        fmt   = DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 48:
        Mtick = HourLocator(byhour = [0,3,6,9,12,15,18,21])
        mtick = HourLocator(byhour = list(range(24)))
        fmt   = DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 72:
        Mtick = HourLocator(byhour = [0,6,12,18])
        mtick = HourLocator(byhour = list(range(0,24,3)))
        fmt   = DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif nHours < 96:
        Mtick = HourLocator(byhour = [0,12])
        mtick = HourLocator(byhour = list(range(0,24,3)))
        fmt   = DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif deltaT.days < 8:
        Mtick = DayLocator(bymonthday=list(range(32)))
        mtick = HourLocator(byhour=list(range(0,24,4)))
        fmt   = DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 16:
        Mtick = DayLocator(bymonthday=list(range(time[0].day,32,2)))
        mtick = DayLocator(interval=1)
        fmt   = DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 32:
        Mtick = DayLocator(bymonthday=list(range(time[0].day,32,4)))
        mtick = DayLocator(interval=1)
        fmt   = DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 60:
        Mtick = DayLocator(bymonthday=list(range(time[0].day,32,7)))
        mtick = DayLocator(interval=2)
        fmt   = DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 183:
        Mtick = MonthLocator(bymonthday=time[0].day,interval=2)
        mtick = MonthLocator(bymonthday=time[0].day,interval=1)
        if time[0].day == 1:
            fmt   = DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            fmt   = DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 367:
        Mtick = MonthLocator(bymonthday=time[0].day,interval=3)
        if time[0].day == 1:
            mtick = MonthLocator(bymonthday=time[0].day,interval=1)
            fmt   = DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            mtick = MonthLocator(bymonthday=time[0].day,interval=1)
            fmt   = DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 366*2:
        Mtick = MonthLocator(bymonthday=time[0].day,interval=6)
        mtick = MonthLocator(bymonthday=time[0].day,interval=1)
        if time[0].day == 1:
            fmt   = DateFormatter('%Y-%m')
            fmt2  = ''
        else:
            fmt   = DateFormatter('%Y-%m-%d')
            fmt2  = ''
    elif deltaT.days < 366*8:
        Mtick = YearLocator()
        mtick = MonthLocator(bymonth=7)
        fmt   = DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*15:
        Mtick = YearLocator(2)
        mtick = YearLocator(1)
        fmt   = DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*40:
        Mtick = YearLocator(5)
        mtick = YearLocator(1)
        fmt   = DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*100:
        Mtick = YearLocator(10)
        mtick = YearLocator(2)
        fmt   = DateFormatter('%Y')
        fmt2  = ''
    elif deltaT.days < 366*200:
        Mtick = YearLocator(20)
        mtick = YearLocator(5)
        fmt   = DateFormatter('%Y')
        fmt2  = ''
    else:
        Mtick = YearLocator(50)
        mtick = YearLocator(byyear=10)
        fmt   = DateFormatter('%Y')
        fmt2  = ''

    # Force first time value to be labeled
    xt = axes.get_xticks()
    xl = axes.get_xlim()
    xt = np.insert(xt,0,xl[0])
    print "Start: %s" % num2date(xl[0])
    print "Stop:  %s" % num2date(xl[1])
    for i in xrange(0,len(xt)):
        print "Tick: %s" % num2date(xt[i])

    axes.set_xticks(xt)
    fig.canvas.draw() 
    #return
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

    print labels
    #labels[0] = '%s\n                %s' % (labels[0],datetime.strftime(time[0],fmt2))
    labels[0] = '%s\n%s' % (labels[0],datetime.strftime(time[0],fmt2))

    xt = axes.get_xticks()
    print xt

    print axes.get_xlim()
    time = num2date(xt)
    if fmt2 != '':
        for i in xrange(1,len(time)):
            if time[i].year > time[i-1].year:
                labels[i] = '%s\n%s' % (labels[i],datetime.strftime(num2date(xt[i]),fmt2))
            if deltaT.days > 1 and time[i].month > time[i-1].month:
                labels[i] = '%s\n%s' % (labels[i],datetime.strftime(num2date(xt[i]),fmt2))
            if nHours < 96 and time[i].day > time[i-1].day:
                labels[i] = '%s\n%s' % (labels[i],datetime.strftime(num2date(xt[i]),fmt2))
            
    if dir == 'x':            
        axes.set_xticklabels(labels)
    if dir == 'y':            
        axes.set_yticklabels(labels)        