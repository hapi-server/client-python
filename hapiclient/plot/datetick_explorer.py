# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:09:42 2018

@author: Brendan
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import datetime
import sys
#sys.path.append('../hapiclient/util')
from hapiclient.plot.datetick import datetick
  
def update(val):
    
    YI = sYearI.val
    mI = sMonthI.val
    DI = sDayI.val
    HI = sHourI.val
    MI = sMinuteI.val
    SI = sSecondI.val
    
    YF = sYearF.val
    mF = sMonthF.val
    DF = sDayF.val
    HF = sHourF.val
    MF = sMinuteF.val
    SF = sSecondF.val
    
    xlow = datetime.datetime(int(YI), int(mI), int(DI), int(HI), int(MI), int(SI))
    xhigh = datetime.datetime(int(YF), int(mF), int(DF), int(HF), int(MF), int(SF))
    print(xlow,xhigh)

    plotit(xlow,xhigh)

def reset(event):
    sYearI.reset()
    sMonthI.reset()
    sDayI.reset()
    sHourI.reset()
    sMinuteI.reset()
    sSecondI.reset()
    
    sYearF.reset()
    sMonthF.reset()
    sDayF.reset()
    sHourF.reset()
    sMinuteF.reset()
    sSecondF.reset()
    
    YI = sYearI.val
    mI = sMonthI.val
    DI = sDayI.val
    HI = sHourI.val
    MI = sMinuteI.val
    SI = sSecondI.val
    
    YF = sYearF.val
    mF = sMonthF.val
    DF = sDayF.val
    HF = sHourF.val
    MF = sMinuteF.val
    SF = sSecondF.val
    
    xlow = datetime.datetime(int(YI), int(mI), int(DI), int(HI), int(MI), int(SI))
    xhigh = datetime.datetime(int(YF), int(mF), int(DF), int(HF), int(MF), int(SF))
    plotit(xlow,xhigh)
    
def plotit(xlow,xhigh):
    global ax1,t1

    x = np.array([xlow,xhigh], dtype=object)

    t1.set_xdata(x)
    ax1.set_xlim(xlow, xhigh)
    ax1.set_title(xlow.isoformat() + " to " + xhigh.isoformat())
    datetick('x', axes=ax1)
    
# Globals
ax1 = None
t1 = None
        
fig1 = plt.figure(figsize=(16,9))
plt.subplots_adjust(bottom=0.4)

if True:
    ax1 = plt.gca()
    y = [0.0, 0.0]
    
    xlow = datetime.datetime(1999, 1, 1, 0, 0, 0)
    xhigh = datetime.datetime(1999, 1, 1, 2, 0, 0)   
    
    x = np.array([xlow,xhigh], dtype=object)
    
    t1, = ax1.plot(x, y, '*')
    ax1.set_xlim(xlow, xhigh)
    ax1.set_title(xlow.isoformat() + " to " + xhigh.isoformat()) 
    datetick('x', axes=ax1, debug=True)


# designate axes object for sliders
axYearI = plt.axes([0.15, 0.23, 0.3, 0.02])
axMonthI = plt.axes([0.15, 0.19, 0.3, 0.02])
axDayI = plt.axes([0.15, 0.15, 0.3, 0.02])
axHourI = plt.axes([0.15, 0.11, 0.3, 0.02])
axMinuteI = plt.axes([0.15, 0.07, 0.3, 0.02])
axSecondI = plt.axes([0.15, 0.03, 0.3, 0.02])

axYearF = plt.axes([0.55, 0.23, 0.3, 0.02])
axMonthF = plt.axes([0.55, 0.19, 0.3, 0.02])
axDayF = plt.axes([0.55, 0.15, 0.3, 0.02])
axHourF = plt.axes([0.55, 0.11, 0.3, 0.02])
axMinuteF = plt.axes([0.55, 0.07, 0.3, 0.02])
axSecondF = plt.axes([0.55, 0.03, 0.3, 0.02])

axStart = plt.axes([0.23, 0.27, 0.15, 0.03])
axEnd = plt.axes([0.63, 0.27, 0.15, 0.03])

axreset = plt.axes([0.47, 0.29, 0.05, 0.05])

# make sliders and add update function 
sYearI = Slider(axYearI, 'Year', 1900, 2100, valinit=1999, valfmt='%0.0f')
sYearI.on_changed(update)
sMonthI = Slider(axMonthI, 'Month', 1, 12, valinit=1, valfmt='%0.0f')
sMonthI.on_changed(update)
sDayI = Slider(axDayI, 'Day', 1, 31, valinit=1, valfmt='%0.0f')
sDayI.on_changed(update)
sHourI = Slider(axHourI, 'Hour', 0, 23, valinit=1, valfmt='%0.0f')
sHourI.on_changed(update)
sMinuteI = Slider(axMinuteI, 'Minute', 0, 59, valinit=0, valfmt='%0.0f')
sMinuteI.on_changed(update)
sSecondI = Slider(axSecondI, 'Second', 0, 59, valinit=0, valfmt='%0.0f')
sSecondI.on_changed(update)

sYearF = Slider(axYearF, 'Year', 1900, 2100, valinit=1999, valfmt='%0.0f')
sYearF.on_changed(update)
sMonthF = Slider(axMonthF, 'Month', 1, 12, valinit=1, valfmt='%0.0f')
sMonthF.on_changed(update)
sDayF = Slider(axDayF, 'Day', 1, 31, valinit=1, valfmt='%0.0f')
sDayF.on_changed(update)
sHourF = Slider(axHourF, 'Hour', 0, 23, valinit=2, valfmt='%0.0f')
sHourF.on_changed(update)
sMinuteF = Slider(axMinuteF, 'Minute', 0, 59, valinit=0, valfmt='%0.0f')
sMinuteF.on_changed(update)
sSecondF = Slider(axSecondF, 'Second', 0, 59, valinit=0, valfmt='%0.0f')
sSecondF.on_changed(update)

bStart = Button(axStart, 'Start',color='1.0',hovercolor='1.0')
bEnd = Button(axEnd, 'End',color='1.0',hovercolor='1.0')

breset = Button(axreset, 'Reset')
breset.on_clicked(reset)