# Gary Feng, 2016-04
# Implementing something close to the R/ggplot2 geom_segment()
# https://github.com/cran/ggplot2/blob/master/R/geom-segment.r
# based on geom_bar

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook

from .geom import geom
from ggplot.utils import is_string
from ggplot.utils import is_categorical


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
    DEFAULT_AES = {'alpha': None, 'color': "black", 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5, 'weight': None, 'y': None, 'width' : None}
    REQUIRED_AES = {'x', 'y', 'xend'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _extra_requires = {'y', 'width'}
    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'color', 'color': 'edgecolor'}
    # NOTE: Currently, geom_bar does not support mapping
    # to alpha and linestyle. TODO: raise exception
    _units = {'edgecolor', 'color', 'alpha', 'linestyle', 'linewidth'}


    def __init__(self, *args, **kwargs):
        # TODO: Change self.__class__ to geom_segment
        super(geom_segment, self).__init__(*args, **kwargs)
        # self.bottom = None
        self.ax = None


    def _plot_unit(self, pinfo, ax):
        categorical = is_categorical(pinfo['y'])
        # TODO:
        # if y is categorical:
        #   make up y coordinates, adjust the barwidth etc
        #   do not print y ticks or the y axis

        # not using weight
        pinfo.pop('weight')

        # getting the data
        x = np.asarray(pinfo.pop('x'))
        xend = np.asarray(pinfo.pop('xend'))

        width_elem = pinfo.pop('width')
        # If width is unspecified, default is an array of 1's
        if width_elem is None:
            width = np.ones(len(x))
        else :
            width = np.array(width_elem)

        if not "barwidth" in pinfo:
            barwidth = 2
        else:
            barwidth = np.asarray(pinfo.pop('barwidth'))

        # plot horizontal bars around y; +/- half width
        y = np.asarray(pinfo.pop('y')) - barwidth/2

        if not "yend" in pinfo:
            yend = y + barwidth/2
        else:
            yend = np.asarray(pinfo.pop('yend'))

        w = xend - x
        h = yend - y

        self.ax = ax
        ax.bar(left=x, height=h, width=w, bottom=y, **pinfo)
        ax.autoscale()
