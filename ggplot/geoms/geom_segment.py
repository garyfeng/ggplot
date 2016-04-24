# Gary Feng, 2016-04
# Implementing something close to the R/ggplot2 geom_segment()
# https://github.com/cran/ggplot2/blob/master/R/geom-segment.r
# based on geom_bar

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import itertools
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook
from matplotlib.patches import *
from matplotlib.lines import *

from .geom import geom
from ggplot.utils import is_string
from ggplot.utils import is_categorical
import warnings

class geom_segment(geom):

    # from r:
    """
    required_aes = c("x", "y", "xend", "yend"),
    non_missing_aes = c("linetype", "size", "shape"),
    default_aes = aes(colour = "black", size = 0.5, linetype = 1, alpha = NA),

    """

    # DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
    #                'linetype': 'solid', 'size': 1.0, 'weight': None, 'y': None, 'width' : None}
    # REQUIRED_AES = {'x'}
    # DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}
    DEFAULT_AES = {'alpha': None, 'color': "black",
                    'fill': '#333333', 'barwidth':2, 'method':"bar",
                    'linetype': 'solid', 'size': 0.5,
                    'weight': None, 'y': None, 'width' : None}
    REQUIRED_AES = {'x', 'y', 'xend'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _extra_requires = {'y', 'yend', 'width', 'barwidth', 'method'}
    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'color', 'color': 'edgecolor'}
    # NOTE: Currently, geom_bar does not support mapping
    # to alpha and linestyle. TODO: raise exception
    _units = {'edgecolor', 'color', 'alpha', 'linestyle', 'linewidth'}


    def __init__(self, *args, **kwargs):
        # TODO: Change self.__class__ to geom_segment
        super(geom_segment, self).__init__(*args, **kwargs)
        self.ax = None


    def _plot_unit(self, pinfo, ax):
        # not using weight
        pinfo.pop('weight')

        # getting the data
        x = np.asarray(pinfo.pop('x'))
        xend = np.asarray(pinfo.pop('xend'))

        # bar width with as a constant or as an aes parameter
        barwidth = np.ones(len(x))*2
        if "barwidth" in pinfo:
            barwidth = np.ones(len(x)) * np.asarray(pinfo.pop('barwidth'))
        maxBarWidth = np.max(barwidth)

        categoricalY = is_categorical(pinfo['y'])
        # TODO:
        # if y is categorical:
        #   make up y coordinates, adjust the barwidth etc
        #   do not print y ticks or the y axis
        y = np.asarray(pinfo.pop('y'))

        #warnings.warn(str(len(y)))

        if categoricalY:
            y = pd.Series(y, dtype="category")
            y.cat.categories = range(y.cat.categories.shape[0])
            y = np.asarray(y) * max(maxBarWidth,1 )
            # y = np.asarray(range(len(x))) * (maxBarWidth +1)
        else:
            # plot horizontal bars around y; +/- half width
            y = y - barwidth/2

        #warnings.warn(str(y))

        if not "yend" in pinfo:
            yend = y + barwidth/2
        else:
            yend = np.asarray(pinfo.pop('yend')) + barwidth/2

        w = xend - x
        h = yend - y

        # width is the linewidth
        width_elem = pinfo.pop('width')
        # If width is unspecified, default is an array of 1's
        if width_elem is None:
            width = np.ones(len(x))
        else :
            width = np.array(width_elem)

        self.ax = ax
        # ax.bar(left=x, height=barwidth, width=w, bottom=y, **pinfo)

        # consider using rect instead of bar
        # matplotlib.patches.Rectangle(xy, width, height, angle=0.0, **kwargs)
        # http://matplotlib.org/api/patches_api.html#matplotlib.patches.Rectangle
        # ax.add_patch(Rectangle((someX - .1, someY - .1), 0.2, 0.2, fill=True, alpha=1))

        method = pinfo.pop('method').lower()
        if method == "rect":
            # patches.Rectangle() does not take vectors; need to iterate
            # use izip for efficient iteration; don't really need enumerate
            for ix, iy, ib, iw in itertools.izip(x,y,barwidth,w):
                ax.add_patch(Rectangle(xy = (ix,iy), \
                        height=ib, width=iw, fill=True, **pinfo))
        elif method == "line":
            # note that linewidth is already set with the `size` aes()
            # and Line2D draws a continueous line for (x,y)
            # we need to break it apart
            # get rid of linewide in the aes(), because we will set here.
            pinfo.pop('linewidth')
            c = pinfo.pop('color')
            for ix, iy, ib, iw in itertools.izip(x,y,barwidth,w):
                # ax.add_line(Line2D((ix, ix+iw), (iy, iy), lw=ib, **pinfo))
                ax.add_line(Line2D((ix, ix+iw), (iy, iy), lw=ib, color=c))

        else:
            ax.bar(left=x, height=barwidth, width=w, bottom=y, **pinfo)

        ax.autoscale()
