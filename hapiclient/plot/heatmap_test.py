# TODO: Change to unit tests.
# * Take screenshot of figure window canvas and compare with referenc
# * Print image to file and compare with reference
# * Compare figure window screenshot with printed image.

from hapiclient.plot.heatmap import heatmap
from datetime import datetime, timedelta
import numpy as np

all = True

if all:
    # 1x1 ints
    if True:
        x = np.array([1]) # Columns
        y = np.array([1]) # Rows
        z = np.array([[1]])
        title = 'z=1x1 int; col center and row center'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1]) # Columns
        y = np.array([0,10]) # Rows
        z = np.array([[1]])
        title = 'z=1x1 int; col center and row edges'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([0,10]) # Columns
        y = np.array([0,5]) # Rows
        z = np.array([[1]])
        title = 'z=1x1 int; col edges and row edges'
        heatmap(x, y, z, title=title)
    
    # 2x1 and 1x2 ints
    if True:
        x = np.array([1]) # Columns
        y = np.array([1,2]) # Rows
        z = np.array([[1],[2]])
        title = 'z=2x1 ints; col center and row centers'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,2]) # Columns
        y = np.array([1,2]) # Rows
        z = np.array([[1],[2]])
        title = 'z=2x1 ints; col edges and row centers'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1],[2]])
        title = 'z=2x1 ints; col center and row edges'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,4]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1],[2]])
        title = 'z=2x1 ints; col edges and row edges'
        heatmap(x, y, z, title=title)
    
    if True:
        x = np.array([1,2]) # Columns
        y = np.array([1]) # Rows
        z = np.array([[1,2]])
        title = 'z=1x2 ints; col centers and row center'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,2]) # Columns
        y = np.array([1,2]) # Rows
        z = np.array([[1,2]])
        title = 'z=1x2 ints; col centers and row edges'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,2,3]) # Columns
        y = np.array([1]) # Rows
        z = np.array([[1,2]])
        title = 'z=1x2 ints; col edges and row center'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,3,4]) # Columns
        y = np.array([1,2.5]) # Rows
        z = np.array([[1,2]])
        title = 'z=1x2 ints; col edges and row edges'
        heatmap(x, y, z, title=title)
    
    # 2x2, 3x3, 10x10 ints
    if True:
        # TODO: Category for 3 should not be there (or should be white to indicate no 3s)
        x = np.array([1,2]) # Columns
        y = np.array([1,5]) # Rows
        z = np.array([[1.0,2.0],[4.0,5.0]])
        title = 'z=2x2 ints; col centers and row centers'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,2,3]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]]) 
        title = 'z=3x3 ints; col centers and row centers'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array(np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(np.arange(1,101,1),(10,10))
        title = 'z=10x10 ints; col centers and row centers'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array(np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(np.arange(1,101,1),(10,10))
        title = 'z=10x10 ints; col centers and row centers'
        heatmap(x, y, z, title=title)
    
    # 10x10 floats
    if True:
        # Note that max and min are not labeled.
        x = np.array(1.5+np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(0.5+np.arange(1,101,1),(10,10))
        title = 'z=10x10 floats; col centers and row centers'
        heatmap(x, y, z, title=title)
            
    # Centers with non-uniform spacing
    if True:
        # Will generate warning b/c non-uniform centers
        x = np.array([1,2,3]) # Columns
        y = np.array([1,2.5,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]]) 
        title = '3x3; uniform col centers nonuniform row centers + warning'
        heatmap(x, y, z, title=title)
    if True:
        # Will generate warning b/c non-uniform centers
        x = np.array([1,2.5,3]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]]) 
        title = '3x3; nonuniform col centers uniform row centers + warning'
        heatmap(x, y, z, title=title)
    if True:
        # Will generate warning b/c non-uniform centers
        x = np.array([1,2.5,3]) # Columns
        y = np.array([1,2.5,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]]) 
        title = '3x3; nonuniform col centers nonuniform row centers + warning'
        heatmap(x, y, z, title=title)
    
    # Gaps
    if True:
        x = np.array([1,2]) # Columns
        y = np.array([[1,2],[2.5,3]]) # Rows
        z = np.array([[1.0,2.0],[4.0,5.0]])
        title = '2x2 col centers and row edges w/gap'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([[1,2],[3,4]]) # Columns
        y = np.array([[1,2],[2.5,3]]) # Rows
        title = '2x2 col edges w/gap and row edges w/gap'
        z = np.array([[1.0,2.0],[4.0,5.0]])
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([1,2,3]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])    
        title = '3x3 col centers and row edges w/gaps'
        heatmap(x, y, z, title=title)
    if True:
        x = np.array([[1,2.5],[3,4],[7,8]]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])    
        title = '3x3 col edges w/gaps and row edges w/gaps'
        heatmap(x, y, z, title=title)
    
# Gaps and NaNs
# With %matplotlib inline, sometimes this is cropped. Seems
# like a bug in iPython as position of axes box differs fromt the
# next plot below.

if True:
    # TODO: Need to distinguish between gaps and nans
    x = np.array([[1,2.5],[3,4],[7,8]]) # Columns
    y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
    z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])    
    title = '3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
    heatmap(x, y, z, title=title)
    
# Time axes
start = datetime(1970, 1, 1)
tb0 = [start,start+timedelta(seconds=2.5)]
tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]
    
# Gaps and NaNs
if False:
    # TODO: Need to distinguish between gaps and nans
    x = np.array([tb0[1],tb1[1],tb2[1]]) # Columns
    y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
    z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])    
    title = '3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
    opts = {
                'title': 'title',
                'ztitle': 'ztitle',
                'xlabel': 'xlabel',
                'ylabel': 'ylabel',
                'zlabel': 'zlabel'
            }
    heatmap(x, y, z, **opts)

# Gaps and NaNs
if True:
    # TODO: Need to distinguish between gaps and nans
    x = np.array([tb0,tb1,tb2]) # Columns
    y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
    z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])    
    title = '3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
    heatmap(x, y, z, title=title)
