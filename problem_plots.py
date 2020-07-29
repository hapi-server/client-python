from hapiclient import hapi
from hapiclient import hapiplot

# CDAWeb data - Magnitude and BGSEc from dataset AC_H0_MFI
server     = 'https://cdaweb.gsfc.nasa.gov/hapi'
dataset    = 'AC_H0_MFI'
start      = '1997-12-10T00:00:00'
stop       = '1997-12-11T10:00:00'
parameters = 'Magnitude,BGSEc'
opts       = {'logging': True, 'usecache': True}    
data, meta = hapi(server, dataset, parameters, start, stop, **opts)
hapiplot(data, meta, **opts)

opts['returnimage'] = True
meta = hapiplot(data, meta, **opts)
fig = meta['parameters'][1]['hapiplot']['figure']