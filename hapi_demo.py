from hapi import hapi
from hapiplot import hapiplot
import matplotlib.pyplot as plt 
import json

plt.close("all")

#format = 'binary' # Not yet implemented

# Should all give the same plot
format = 'fbinary'
format = 'csv'
format = 'fcsv'

#############################################################################
# Scalar and vector example
server     = 'http://mag.gmu.edu/TestData/hapi';
server     = 'http://localhost:8999/hapi'
dataset    = 'TestData'
parameters = 'scalar,vector'
start      = '1970-01-01'
stop       = '1970-01-01T00:20:00'
opts       = {'format': format, 'logging': True, 'use_cache': False}

data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalar']
# data['vector']

hapiplot(meta,data,"Demo 2")
#############################################################################

#############################################################################
# Scalar example
server     = 'http://mag.gmu.edu/TestData/hapi';
server     = 'http://localhost:8999/hapi'
dataset    = 'TestData'
parameters = 'scalar'
start      = '1970-01-01'
stop       = '1970-01-01T00:20:00'
opts       = {'format': 'fbinary', 'logging': True, 'use_cache': False}

data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalar']
hapiplot(meta,data,"Demo 1")
#############################################################################

#############################################################################
# Scalar and vector example
server     = 'http://mag.gmu.edu/TestData/hapi';
server     = 'http://localhost:8999/hapi'
dataset    = 'TestData'
parameters = 'scalar,vector'
start      = '1970-01-01'
stop       = '1970-01-01T00:20:00'
opts       = {'format': format, 'logging': True, 'use_cache': False}

data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalar']
# data['vector']

hapiplot(meta,data,"Demo 2")
#############################################################################

#############################################################################
# Integer scalar example
server     = 'http://mag.gmu.edu/TestData/hapi';
server     = 'http://localhost:8999/hapi'
dataset    = 'TestData'
parameters = 'scalarint'
start      = '1970-01-01'
stop       = '1970-01-01T00:20:00'
opts       = {'format': format, 'logging': True, 'use_cache': False}

data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalarint']

hapiplot(meta,data,"Demo 3")
#############################################################################

#############################################################################
# Metadata request examples
sn = 2 # Server number in servers.txt
dn = 0 # Dataset number from server sn

# Default parameters
opts = {'update_script': False,'logging': False,
        'cache_mlbin': True,'cache_hapi': True,
        'use_cache': True,'format': 'fbinary'}

# List servers to console
hapi(logging=True)
# or
# hapi(**opts)

# Get server list
Servers = hapi();
# or
# Servers = hapi(**opts)
print "Server list"
print json.dumps(Servers, sort_keys=True, indent=4)

# Get structure of datasets from server sn
print "Datasets from server number " + str(sn)
metad = hapi(Servers[sn])
# or
# metad = hapi(Servers[sn],**opts)
print json.dumps(metad, sort_keys=True, indent=4)

# Get dictionary of all parameters in dataset dn
print "Parameters in datataset number " + str(dn) + " from server " + str(sn)
metap = hapi(Servers[sn], metad['catalog'][dn]['id'])
# or
# metap = hapi(Servers[sn], metad['catalog'][dn]['id'], **opts)
print json.dumps(metap, sort_keys=True, indent=3)

# Get structure of first parameter in dataset dn
metap1 = hapi(Servers[sn], metad['catalog'][dn]['id'], metap["parameters"][2]["name"])
# or
# metap1 = hapi(Servers[sn], metad['catalog'][dn]['id'], metap["parameters"][2]["name"],**opts)

print "First parameter in datataset number " + str(dn) + " from server " + str(sn)
print json.dumps(metap1, sort_keys=True, indent=4)
#############################################################################
