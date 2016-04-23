from .theme_gray import theme_gray


class theme_noy(theme_gray):
    """
    White background w/ black gridlines
    """

    def __init__(self):
        super(theme_noy, self).__init__()
        self._rcParams['axes.facecolor'] = 'white'
        self._rcParams["axes.grid"] = "False"
        self._rcParams["ytick.color"] = "white"
