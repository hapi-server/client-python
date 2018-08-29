from hapi import hapi
from hapiplot import hapiplot
import matplotlib.pyplot as plt 
import json

# In IPython, enter %matplotlib qt on command line to open plots in 
# new window. Enter %matplotlib inline to revert.

plt.close("all")

#############################################################################
#%% CDAWeb example
server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
dataset    = 'AC_H0_MFI'
start      = '2001-01-01T05:00:00'
stop       = '2001-01-01T06:00:00'
parameters = 'Magnitude,BGSEc'
opts       = {'format': 'binary', 'logging': True, 'use_cache': False}
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta,logging=True)

#############################################################################
#%% Test data 
server     = 'http://mag.gmu.edu/TestData/hapi';
server     = 'http://localhost:8999/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01'
stop       = '1970-01-01T00:00:10'
opts       = {'logging': True, 'use_cache': False}
popts      = {'logging': True}

#############################################################################
#%% Scalar
parameters = 'scalar'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta,**popts)
#############################################################################

#############################################################################
#%% Scalar with integer type
parameters = 'scalar'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta,**popts)
#############################################################################

#############################################################################
#%% Scalar with string type
parameters = 'scalarstr'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta,**popts)
#############################################################################

#############################################################################
#%% Scalar with isotime type
parameters = 'scalariso'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
#hapiplot(data,meta)
#############################################################################

#############################################################################
#%% Vector
parameters = 'vector'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta,**popts)
#############################################################################

#############################################################################
#%% Two parameters
parameters = 'scalar,vector'
data,meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data,meta,**popts)
#############################################################################

#############################################################################
#%% Metadata request examples
sn = 0 # Server number in servers.txt
dn = 0 # Dataset number from server sn
pn = 0 # Parameter number in Dataset dn

# List servers to console
hapi(logging=True)
# or
# hapi(**opts)

# Get server list
Servers = hapi()
# or
# Servers = hapi(**opts)
print("Server list")
print(json.dumps(Servers, sort_keys=True, indent=4))

# Get structure of datasets from server sn
print("Datasets from server number " + str(sn))
metad = hapi(Servers[sn])
# or
# metad = hapi(Servers[sn],**opts)
print(json.dumps(metad, sort_keys=True, indent=4))

# Get dictionary of all parameters in dataset dn
print("Parameters in datataset number " + str(dn) + " from server " + str(sn))
metap = hapi(Servers[sn], metad['catalog'][dn]['id'])
# or
# metap = hapi(Servers[sn], metad['catalog'][dn]['id'], **opts)
print(json.dumps(metap, sort_keys=True, indent=3))

# Get structure of first parameter in dataset dn
metap1 = hapi(Servers[sn], metad['catalog'][dn]['id'], metap["parameters"][2]["name"])
# or
# metap1 = hapi(Servers[sn], metad['catalog'][dn]['id'], metap["parameters"][2]["name"],**opts)

print("Parameter " + str(pn) + " in datataset number " + str(dn) + " from server " + str(sn))
print(json.dumps(metap1, sort_keys=True, indent=4))
#############################################################################