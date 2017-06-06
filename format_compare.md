[Table description](https://github.com/hapi-server/matlab-client/blob/master/format_compare.md).

```
csv (faden)        0.5928s	# HAPI CSV
csv (pandas)       0.1468s	# HAPI CSV
csv (pandas2)      0.0863s	# HAPI CSV
csv (genfromtext)  0.8768s	# HAPI CSV
fcsv               0.0797s	# Alt. CSV
fbin               0.0073s	# Alt. binary (all doubles)
fbin w/ints        0.0027s	# Alt. binary (time dbl, param int)
bin (fromfile)     0.0582s	# HAPI binary

Time Ratios
csv/fcsv   1.8424
bin/fbin   7.9645

csv/bin    2.5220
fcsv/fbin  10.9020
```
