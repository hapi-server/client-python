import os
import datetime
import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
from hapiclient.util.datetick import datetick

def plotit(ds1, ds2):
    # Plots two points separated by varying time ranges.
    # For testing date/time tick labeling code datetick.py.
    dt1 = dateutil.parser.parse(ds1)
    dt2 = dateutil.parser.parse(ds2)
    x = np.array([dt1,dt2], dtype=object)
    y = [0.0,0.0]
    plt.figure()
    plt.plot(x, y, '*')
    plt.title(ds1 + ' - ' + ds2)
    datetick('x')
    plt.grid()

###############################################################################
# > 50 years

from datetime import timedelta

plotit('1950-01-01T00:00:00Z','2012-01-04T00:00:00Z')

###############################################################################
# 366*15 days <= dt < 366*40 days

plotit('2000-01-01T00:00:00Z','2017-01-04T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2018-01-04T00:00:00Z')
plotit('2002-01-01T00:00:00Z','2019-01-04T00:00:00Z')
plotit('2003-01-01T00:00:00Z','2020-01-04T00:00:00Z')
plotit('2004-01-01T00:00:00Z','2030-01-04T00:00:00Z')

###############################################################################
# 366*8 days <= dt < 366*15 days

plotit('2001-01-01T00:00:00Z','2009-01-04T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2012-01-04T00:00:00Z')

###############################################################################
# 366*2 days <= dt < 366*8 days

plotit('2001-01-01T00:00:00Z','2003-01-04T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2008-12-31T00:00:00Z')
plotit('2001-04-01T00:00:00Z','2002-04-30T00:00:00Z')


###############################################################################
# 367 <= dt < 366*2 days

plotit('2001-01-01T00:00:00Z','2002-01-03T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2002-12-31T00:00:00Z')
plotit('2001-04-01T00:00:00Z','2002-04-30T00:00:00Z')

###############################################################################
# 183 <= dt < 367 days

plotit('2001-01-01T00:00:00Z','2001-07-02T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-12-31T00:00:00Z')
plotit('2001-02-12T00:00:00Z','2002-01-31T00:00:00Z')

###############################################################################
# 60 <= dt < 183 days

plotit('2001-01-01T00:00:00Z','2001-05-02T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-02-27T23:00:00Z')
plotit('2001-12-31T00:00:00Z','2002-02-26T23:00:00Z')
    
###############################################################################
# 32 <= dt < 60 days

plotit('2001-01-01T00:00:00Z','2001-02-02T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-02-27T23:00:00Z')
plotit('2001-01-15T00:00:00Z','2001-02-16T23:00:00Z')
plotit('2001-12-31T00:00:00Z','2002-02-26T23:00:00Z') # Span year boundary

###############################################################################
# 16 <= dt < 32 days

plotit('2001-01-01T00:00:00Z','2001-01-31T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-16T23:00:00Z')
plotit('2001-01-30T00:00:00Z','2001-02-15T23:00:00Z') # Span month boundary
plotit('2001-12-30T00:00:00Z','2001-01-15T23:00:00Z') # Span year boundary

###############################################################################
# 8 <= dt < 16 days

plotit('2001-01-01T00:00:00Z','2001-01-09T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-16T23:00:00Z')
plotit('2001-01-30T00:00:00Z','2001-02-04T23:00:00Z') # Span month boundary
plotit('2001-12-30T00:00:00Z','2002-01-04T23:00:00Z') # Span year boundary

###############################################################################
# 4 <= dt < 8 days

plotit('2001-01-01T00:00:00Z','2001-01-05T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-05T00:00:00Z')
plotit('2001-01-30T00:00:00Z','2001-02-01T23:00:00Z') # Span month boundary
plotit('2001-12-30T00:00:00Z','2002-01-01T23:00:00Z') # Span year boundary

###############################################################################
# 48 <= dt < 72 hours

plotit('2001-01-01T00:00:00Z','2001-01-03T00:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-03T12:30:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-03T23:59:59Z')

###############################################################################
# 24 <= dt < 48 hours

plotit('2001-01-01T00:00:00Z','2001-01-02T01:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-02T23:00:00Z')
plotit('2001-01-01T06:00:00Z','2001-01-02T07:00:00Z')
plotit('2001-01-01T00:30:00Z','2001-01-02T01:00:00Z')

###############################################################################
# 12 <= dt < 24 hours

plotit('2001-01-01T00:00:00Z','2001-01-01T18:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-01T12:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-01T23:00:00Z')
plotit('2001-01-01T02:00:00Z','2001-01-02T01:00:00Z')

###############################################################################
# 6 <= dt < 12 hours
    
plotit('2001-01-01T00:00:00Z','2001-01-01T06:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-01T09:00:00Z')
plotit('2001-01-01T00:00:00Z','2001-01-01T11:00:00Z')

if False:
    ###############################################################################
    # 20 <= dt < 30 second
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:00Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:21Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:00Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:29Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross minute boundary
    d1 = dateutil.parser.parse('2001-01-01T00:00:58Z')
    d2 = dateutil.parser.parse('2001-01-01T00:01:18Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary
    d1 = dateutil.parser.parse('2001-01-01T00:59:58Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:28Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    ###############################################################################
    # 1 <= dt < 5 second
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:00Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:05Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:00Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:01Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross day boundary
    d1 = dateutil.parser.parse('2001-01-01T00:00:59Z')
    d2 = dateutil.parser.parse('2001-01-01T00:01:03Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary
    d1 = dateutil.parser.parse('2001-01-01T00:59:58Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:03Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross day boundary
    d1 = dateutil.parser.parse('2001-01-01T23:59:58Z')
    d2 = dateutil.parser.parse('2001-01-02T00:00:03Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    ###############################################################################
    # 5 <= dt < 10 second
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:00Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:07Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:00Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:09Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Simple
    d1 = dateutil.parser.parse('2001-01-01T00:00:01Z')
    d2 = dateutil.parser.parse('2001-01-01T00:00:06Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross day boundary
    d1 = dateutil.parser.parse('2001-01-01T23:59:58Z')
    d2 = dateutil.parser.parse('2001-01-02T00:00:05Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross day boundary
    # Problem: Second row of labels overlap
    d1 = dateutil.parser.parse('2001-01-01T23:59:59Z')
    d2 = dateutil.parser.parse('2001-01-02T00:00:05Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary only
    d1 = dateutil.parser.parse('2001-01-01T00:59:58Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:05Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary/max time span for this tick locator
    d1 = dateutil.parser.parse('2001-01-01T00:59:58Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:07Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary/min time span for this tick locator
    d1 = dateutil.parser.parse('2001-01-01T00:59:58Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:03')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    
    ###############################################################################
    # 10 <= dt < 20 second
    
    # Cross day boundary
    d1 = dateutil.parser.parse('2001-01-01T23:59:56Z')
    d2 = dateutil.parser.parse('2001-01-02T00:00:10Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross day boundary
    # Problem: Second row of labels overlap
    d1 = dateutil.parser.parse('2001-01-01T23:59:58Z')
    d2 = dateutil.parser.parse('2001-01-02T00:00:10Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary only
    d1 = dateutil.parser.parse('2001-01-01T00:59:56Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:10Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary/max time span for this tick locator
    d1 = dateutil.parser.parse('2001-01-01T00:59:56Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:15Z')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    
    # Cross hour boundary/min time span for this tick locator
    d1 = dateutil.parser.parse('2001-01-01T00:59:56Z')
    d2 = dateutil.parser.parse('2001-01-01T01:00:06')
    x = np.array([d1,d2], dtype=object)
    y = [0.0,0.0]
    plt.clf()
    plt.plot(x, y, '*')
    datetick('x')
    