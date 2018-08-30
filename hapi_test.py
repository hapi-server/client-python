#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 11:44:25 2018

@author: robertweigel
"""

from hapi import hapi
from hapiplot import hapiplot
import time

server     = 'http://hapi-server.org/servers/TestData/hapi'
#server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-02T00:00:00'
logging    = False
use_cache  = False

#############################################################################
#%% Read method test
parameters = 'vectormulti'

opts       = {'format': 'csv', 'method': 'numpy', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
print(data)

opts       = {'format': 'csv', 'method': 'pandas', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
print(data)

opts       = {'format': 'csv', 'method': 'numpynolength', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
print(data)

opts       = {'format': 'csv', 'method': 'pandasnolength', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
print(data)

opts       = {'format': 'binary', 'logging': logging, 'use_cache': use_cache}
data,meta  = hapi(server, dataset, parameters, start, stop, **opts)
print(data)
#############################################################################
