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
        datetick('x')
        plt.show()


def on_xlims_change(ax): datetick('x')
def on_ylims_change(ax): datetick('y')

def datetick(dir):
    # Based on spacepy/plot/utils.p 07/10/2017
    from matplotlib.dates import *
    from datetime import datetime

    axes = plt.gca()
    fig = plt.gcf()        

    if dir == 'x':
        axes.callbacks.connect('xlim_changed', on_xlims_change)
        time = num2date(axes.get_xlim())
    else:
        axes.callbacks.connect('ylim_changed', on_ylims_change)
        time = num2date(axes.get_ylim())

    deltaT = time[-1] - time[0]
    nHours = deltaT.days * 24.0 + deltaT.seconds/3600.0
    
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
        Mtick = HourLocator(byhour = [0,6,12,18])
        mtick = HourLocator(byhour = list(range(24)))
        fmt   = DateFormatter('%H')
        fmt2  = '%Y-%m-%d'
    elif deltaT.days < 8:
        Mtick = DayLocator(bymonthday=list(range(32)))
        mtick = HourLocator(byhour=list(range(0,24,2)))
        fmt   =  DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 15:
        Mtick = DayLocator(bymonthday=list(range(2,32,2)))
        mtick = HourLocator(byhour=[0,6,12,18])
        fmt   =  DateFormatter('%d')
        fmt2  = '%Y-%m'
    elif deltaT.days < 32:
        Mtick = DayLocator(bymonthday=list(range(5,35,5)))
        mtick = HourLocator(byhour=[0,6,12,18])
        fmt    =  DateFormatter('%d')
        fmt2  = '%Y'
    elif deltaT.days < 60:
        Mtick = MonthLocator()
        mtick = DayLocator(bymonthday=list(range(5,35,5)))
        fmt   =  DateFormatter('%d')
        fmt2  = '%Y'
    elif deltaT.days < 367:
        Mtick = MonthLocator()
        mtick = DayLocator(bymonthday=list(range(5,35,5)))
        fmt   =  DateFormatter('%m')
        fmt2  = '%Y'
    elif deltaT.days < 731:
        Mtick = MonthLocator()
        mtick = DayLocator(bymonthday=15)
        fmt   =  DateFormatter('%m')
        fmt2  = '%Y'
    else:
        Mtick = YearLocator()
        mtick = MonthLocator(bymonth=7)
        fmt   =  DateFormatter('%Y')
        fmt2  = ''

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
    for i in xrange(1,len(xt)):
        if xt[i] % 1 == 0:
            labels[i] = '%s\n%s' % (labels[i],datetime.strftime(num2date(xt[i],fmt2))
            
    axes.set_xticklabels(labels)
