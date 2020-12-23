# Allow "from hapiclient import hapi"
from hapiclient.hapi import hapi

# Allow "from hapiclient import hapitime2datetime"
from hapiclient.hapi import hapitime2datetime

import warnings
try:
    import matplotlib

    # Deal with this issue: https://github.com/matplotlib/matplotlib/issues/13118
    warnings.filterwarnings(action="ignore",
                            message=r'\n.*rcparam was deprecated',
                            category=matplotlib.cbook.MatplotlibDeprecationWarning)
    warnings.filterwarnings(action="ignore",
                            message=r'\n.*examples\.directory is deprecated',
                            category=matplotlib.cbook.MatplotlibDeprecationWarning)

    # Allow "from hapiclient import hapiplot"
    from hapiclient.hapiplot import hapiplot
except:
    print('Problem importing Matplotlib. hapiplot function will not work.')

from hapiclient.util import HAPIError

# Allow "from hapiclient import autoplot"
from hapiclient.autoplot.autoplot import autoplot

# Allow "from hapiclient import gallery"
from hapiclient.gallery.gallery import gallery

__version__ = '0.1.7'
