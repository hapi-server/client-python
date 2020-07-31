# TODO: Change to unit tests.
# * Take screenshot of figure window canvas and compare with referenc
# * Print image to file and compare with reference
# * Compare figure window screenshot with printed image.

from hapiclient.plot.heatmap import heatmap
from datetime import datetime, timedelta
import numpy as np

tests = range(0,31)
tests = range(27,31)
#tests = range(23,24)
tests = range(0,31)
tests = [31]

import matplotlib as plt
plt.rcParams.update({'figure.max_open_warning': 0})

for tn in tests:

    # 1x1 ints
    if tn == 0:
        x = np.array([1]) # Columns
        y = np.array([1]) # Rows
        z = np.array([[1]])
        title = 'test #' + str(tn) + '  z=1x1 int; col center and row center'
        heatmap(x, y, z, title=title)

    if tn == 1:
        x = np.array([1]) # Columns
        y = np.array([0,10]) # Rows
        z = np.array([[1]])
        title = 'test #' + str(tn) + '  z=1x1 int; col center and row edges'
        heatmap(x, y, z, title=title)

    if tn == 2:
        x = np.array([0,10]) # Columns
        y = np.array([0,5]) # Rows
        z = np.array([[1]])
        title = 'test #' + str(tn) + '  z=1x1 int; col edges and row edges'
        heatmap(x, y, z, title=title)

    # 2x1 and 1x2 ints
    if tn == 3:
        x = np.array([1]) # Columns
        y = np.array([1,2]) # Rows
        z = np.array([[1],[2]])
        title = 'test #' + str(tn) + '  z=2x1 ints; col center and row centers'
        heatmap(x, y, z, title=title)

    if tn == 4:
        x = np.array([1,2]) # Columns
        y = np.array([1,2]) # Rows
        z = np.array([[1],[2]])
        title = 'test #' + str(tn) + '  z=2x1 ints; col edges and row centers'
        heatmap(x, y, z, title=title)

    if tn == 5:
        x = np.array([1]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1],[2]])
        title = 'test #' + str(tn) + '  z=2x1 ints; col center and row edges'
        heatmap(x, y, z, title=title)

    if tn == 6:
        x = np.array([1,4]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1],[2]])
        title = 'test #' + str(tn) + '  z=2x1 ints; col edges and row edges'
        heatmap(x, y, z, title=title)

    if tn == 7:
        x = np.array([1,2]) # Columns
        y = np.array([1]) # Rows
        z = np.array([[1,2]])
        title = 'test #' + str(tn) + '  z=1x2 ints; col centers and row center'
        heatmap(x, y, z, title=title)

    if tn == 8:
        x = np.array([1,2]) # Columns
        y = np.array([1,2]) # Rows
        z = np.array([[1,2]])
        title = 'test #' + str(tn) + '  z=1x2 ints; col centers and row edges'
        heatmap(x, y, z, title=title)

    if tn == 9:
        x = np.array([1,2,3]) # Columns
        y = np.array([1]) # Rows
        z = np.array([[1,2]])
        title = 'test #' + str(tn) + '  z=1x2 ints; col edges and row center'
        heatmap(x, y, z, title=title)

    if tn == 10:
        x = np.array([1,3,4]) # Columns
        y = np.array([1,2.5]) # Rows
        z = np.array([[1,2]])
        title = 'test #' + str(tn) + '  z=1x2 ints; col edges and row edges'
        heatmap(x, y, z, title=title)

    # 2x2, 3x3, 10x10 ints
    if tn == 11:
        # TODO: Category for 3 should not be there (or should be white to indicate no 3s)
        x = np.array([1,2]) # Columns
        y = np.array([1,5]) # Rows
        z = np.array([[1.0,2.0],[4.0,5.0]])
        title = 'test #' + str(tn) + '  z=2x2 ints; col centers and row centers'
        heatmap(x, y, z, title=title)

    if tn == 12:
        x = np.array([1,2,3]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])
        title = 'test #' + str(tn) + '  z=3x3 ints; col centers and row centers'
        heatmap(x, y, z, title=title)

    if tn == 13:
        x = np.array(np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(np.arange(1,101,1),(10,10))
        title = 'test #' + str(tn) + '  z=10x10 ints; col centers and row centers'
        heatmap(x, y, z, title=title)

    if tn == 14:
        x = np.array(np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(np.arange(1,101,1),(10,10))
        title = 'test #' + str(tn) + '  z=10x10 ints; col centers and row centers'
        heatmap(x, y, z, title=title)

    # 10x10 floats
    if tn == 15:
        # Note that max and min are not labeled.
        x = np.array(1.5+np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(0.5+np.arange(1,101,1),(10,10))
        title = 'test #' + str(tn) + '  z=10x10 floats; col centers and row centers'
        heatmap(x, y, z, title=title)

    # Centers with non-uniform spacing
    if tn == 16:
        # Will generate warning b/c non-uniform centers
        x = np.array([1,2,3]) # Columns
        y = np.array([1,2.5,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3; uniform col centers nonuniform row centers + warning'
        heatmap(x, y, z, title=title)

    if tn == 17:
        # Will generate warning b/c non-uniform centers
        x = np.array([1,2.5,3]) # Columns
        y = np.array([1,2,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3; nonuniform col centers uniform row centers + warning'
        heatmap(x, y, z, title=title)

    if tn == 18:
        # Will generate warning b/c non-uniform centers
        x = np.array([1,2.5,3]) # Columns
        y = np.array([1,2.5,3]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3; nonuniform col centers nonuniform row centers + warning'
        heatmap(x, y, z, title=title)

    # Gaps
    if tn == 19:
        x = np.array([1,2]) # Columns
        y = np.array([[1,2],[2.5,3]]) # Rows
        z = np.array([[1.0,2.0],[4.0,5.0]])
        title = 'test #' + str(tn) + '  2x2 col centers and row edges w/gap'
        heatmap(x, y, z, title=title)

    if tn == 20:
        x = np.array([[1,2],[3,4]]) # Columns
        y = np.array([[1,2],[2.5,3]]) # Rows
        title = 'test #' + str(tn) + '  2x2 col edges w/gap and row edges w/gap'
        z = np.array([[1.0,2.0],[4.0,5.0]])
        heatmap(x, y, z, title=title)

    if tn == 21:
        x = np.array([1,2,3]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 col centers and row edges w/gaps'
        heatmap(x, y, z, title=title)

    if tn == 22:
        x = np.array([[1,2.5],[3,4],[7,8]]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,5,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 col edges w/gaps and row edges w/gaps'
        heatmap(x, y, z, title=title)

    if tn == 23:
        # TODO: Need to distinguish between gaps and nans
        # Gaps and NaNs
        # With %matplotlib inline, sometimes this is cropped. Seems
        # like a bug in iPython as position of axes box differs fromt the
        # next plot below.
        x = np.array([[1,2.5],[3,4],[7,8]]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
        heatmap(x, y, z, title=title)

    if tn == 24:
        start = datetime(1970, 1, 1)
        tb0 = [start,start+timedelta(seconds=2.5)]
        tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
        tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

        # Gaps and NaNs
        # TODO: Need to distinguish between gaps and nans
        x = np.array([tb0[1],tb1[1],tb2[1]]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
        opts = {
                    'title': 'title',
                    'ztitle': 'ztitle',
                    'xlabel': 'xlabel',
                    'ylabel': 'ylabel',
                    'zlabel': 'zlabel'
                }
        heatmap(x, y, z, **opts)

    if tn == 25:
        start = datetime(1970, 1, 1)
        tb0 = [start,start+timedelta(seconds=2.5)]
        tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
        tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

        # Gaps and NaNs
        # TODO: Need to distinguish between gaps and nans
        x = np.array([tb0,tb1,tb2]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
        heatmap(x, y, z, title=title)

    if tn == 26:
        start = datetime(1970, 1, 1)
        tb0 = [start,start+timedelta(seconds=2.5)]
        tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
        tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

        # Gaps and NaNs
        # TODO: Need to distinguish between gaps and nans
        x = np.array([tb0,tb1,tb2]) # Columns
        y = np.array(['A','B','C']) # Rows
        z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 w/NaNs and categorical y'
        heatmap(x, y, z, title=title)

    if tn == 27:
        start = datetime(1970, 1, 1)
        tb0 = [start,start+timedelta(seconds=2.5)]
        tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
        tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

        # Gaps and NaNs
        # TODO: Need to distinguish between gaps and nans
        x = np.array(['First','Second','Third']) # Columns
        y = np.array(['A','B','C']) # Rows
        z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 w/NaNs and categorical x and y'
        heatmap(x, y, z, title=title)
        
    if tn == 28:
        start = datetime(1970, 1, 1)
        tb0 = [start,start+timedelta(seconds=2.5)]
        tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
        tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

        # Gaps and NaNs
        # TODO: Need to distinguish between gaps and nans
        x = np.array([tb0,tb1,tb2]) # Columns
        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        z = np.array([[1,2,3],[4,np.nan,6],[7,8,9]])
        title = 'test #' + str(tn) + '  3x3 w/NaNs, col edges w/gaps. and row edges w/gaps'
        opts = {'title': title, 
                'nan.color': [0,1,1],
                'nan.hatch': '.',
                'nan.hatch.color':'k',
                'gap.color': [1,0,1],
                'gap.hatch': 'x',
                'gap.hatch.color':'k'}
        heatmap(x, y, z, **opts)

    if tn == 29:

        x = np.array(np.arange(20)) # Columns
        y = np.array(np.arange(20)) # Rows
        z = np.random.rand(20,20)

        title = 'test #' + str(tn) + ' TODO: bottom and top limits not shown'
        fig, cb = heatmap(x, y, z, title=title)

        x = np.array([1,2,3,4]) # Columns
        y = np.array([1,2,3,4]) # Rows
        z = np.array([[0,3,0,3],[0,3,0,3],[0,3,0,3],[0,3,0,3]])
        title = 'test #' + str(tn) + ' TODO: some colors not present'
        fig, cb = heatmap(x, y, z, title=title)

        x = np.array([1,2,3,4]) # Columns
        y = np.array([1,2,3,4]) # Rows
        z = np.array([[0,1e9,0,10],[0,10,0,10],[0,10,0,10],[0,10,0,10]])
        title = 'test #' + str(tn) + ' TODO: large z values'
        fig, cb = heatmap(x, y, z, title=title)

    if tn == 30:

        from matplotlib import rc_context

        rcParams = {
                    'savefig.dpi': 144,
                    'savefig.format': 'png',
                    'savefig.bbox': 'standard',
                    'savefig.transparent': True,
                    'figure.max_open_warning': 50,
                    'figure.figsize': (7, 3),
                    'figure.dpi': 144,
                    'axes.titlesize': 10}
        
        x = np.array(np.arange(1,11,1)) # Columns
        y = np.array(np.arange(1,11,1)) # Rows
        z = np.reshape(np.arange(1,101,1),(10,10))
        title = 'test #' + str(tn) + ' using rc_context'
        with rc_context(rc=rcParams):
            heatmap(x, y, z, title=title, zlabel="A")
            heatmap(x, y, z, title=title, zlabel="A\nB")
            heatmap(x, y, z, title=title, zlabel="A\nB\nC")

    if tn == 31:
        start = datetime(1970, 1, 1)
        tb0 = [start,start+timedelta(seconds=2.5)]
        tb1 = [start+timedelta(seconds=3),start+timedelta(seconds=4)]
        tb2 = [start+timedelta(seconds=7),start+timedelta(seconds=8)]

        y = np.array([1,2,3]) # Rows
        z = np.nan*np.array([[1,2,3],[4,5,6],[7,8,9]])

        x = np.array([1,2,3]) # Columns
        title = 'test #' + str(tn) + ' All NaN z, uniform bins'
        heatmap(x, y, z, title=title)

        x = [tb0, tb1, tb2]
        title = 'test #' + str(tn) + ' All NaNs z, non-uniform x'
        heatmap(x, y, z, title=title)

        y = np.array([[1,2.5],[3,4],[7,8]]) # Rows
        title = 'test #' + str(tn) + ' All NaN z, non-uniform x and y'
        heatmap(x, y, z, title=title)
