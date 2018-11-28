from hapiclient import autoplot

server     = 'http://hapi-server.org/servers/TestData/hapi'
dataset    = 'dataset1'
start      = '1970-01-01Z'
stop       = '1970-01-01T00:00:11Z'
parameters = 'scalar,vector'
opts       = {'logging': True, 'usecache': False, 'version': 'nightly'}
autoplot(server, dataset, parameters, start, stop, **opts)
