from hapi import hapi
from hapi import iso2format
from hapiplot import hapiplot
import matplotlib.pyplot as plt 
import json

plt.close("all")

# Specify format to use (for testing only; by default it will check 
# response from /capabilities and use binary if avaialble).
#format = 'csv'

server     = 'http://mag.gmu.edu/TestData/hapi';
#server     = 'http://localhost:8999/hapi'
dataset    = 'TestData'
start      = '1970-01-01'
stop       = '1970-01-02T00:00:00'
opts       = {'format': format, 'logging': True, 'use_cache': False}

#############################################################################
# Scalar example
parameters = 'scalar'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalar']

hapiplot(meta,data,"Demo 1")
#############################################################################

#############################################################################
# Scalar and vector example
parameters = 'vector'

data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalar']
# data['vector']

hapiplot(meta,data,"Demo 2")
#############################################################################

#############################################################################
# Scalar and vector example
parameters = 'scalar,vector'

data,meta = hapi(server, dataset, parameters, start, stop, **opts)
# data is numpy.ndarray with fields of Time and scalar
# data['Time']
# data['scalar']
# data['vector']

hapiplot(meta,data,"Demo 2")
#############################################################################

#############################################################################
# Integer scalar example
parameters = 'scalarint'
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
pn = 1 # Parameter number in Dataset dn

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

print "Parameter " + str(pn) + " in datataset number " + str(dn) + " from server " + str(sn)
print json.dumps(metap1, sort_keys=True, indent=4)
#############################################################################