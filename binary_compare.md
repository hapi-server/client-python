[Table description](https://github.com/hapi-server/matlab-client/blob/master/binary_compare.md).

```
csv (faden) tot.:  0.6218	# HAPI CSV
csv (pandas) tot.: 0.3280s	# HAPI CSV
csv total:         11.9132s	# HAPI CSV
fcsv total:        0.1390s	# Proposed fast CSV
fbin total:        0.0085s	# Proposed binary (all doubles)
fbin w/ints total: 0.0040s	# Proposed binary (time dbl, param int)
bin total:         0.7405s	# HAPI binary
  (bin memmap:        0.0076s)
  (bin extract time:  0.7329s)
  (bin extract data:  0.0000s)

Time Ratios
(best csv)/fcsv  : 2.3599
(best csv)/bin   : 0.4429
bin/fbin         : 86.8127
bin/(fbin w/ints): 185.2609
```
