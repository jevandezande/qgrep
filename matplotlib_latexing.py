import matplotlib.pyplot as plt

golden_mean = (5**0.5 - 1) / 2  # Aesthetic ratio


def latexplots(height: float = None, width: float = 16, fontsize: int = 12, pad: float = 2, heightmult: float = 1):
    fig_width = width / 2.54  # width in inches
    fig_height = fig_width * golden_mean if not height else height / 2.54  # height in inches

    plt.rcParams |= {
        # fmt: off
        'backend'                   : 'pdf',
        'pgf.texsystem'             : 'pdflatex', # change this if using xetex or lautex
        'axes.labelsize'            : fontsize,
        'font.size'                 : fontsize,
        'axes.titlesize'            : fontsize,
        'legend.fontsize'           : fontsize - 2,
        'xtick.labelsize'           : fontsize - 2,
        'ytick.labelsize'           : fontsize - 2,
        'xtick.major.pad'           : pad,
        'xtick.minor.pad'           : pad,
        'ytick.major.pad'           : pad,
        'ytick.minor.pad'           : pad,
        'figure.figsize'            : (fig_width, fig_height * heightmult),
        'font.family'               : 'serif',
        'text.usetex'               : True,
        'axes.grid'                 : True,
        'axes.linewidth'            : 0.5,
        'legend.numpoints'          : 1,
        'legend.borderaxespad'      : 0.3, # distance to axes edge
        'legend.borderpad'          : 0.3,
        'legend.labelspacing'       : 0.4,
        'legend.framealpha'         : 1.0,
        'legend.frameon'            : True,
        'legend.handlelength'       : 1.0,
        'legend.handletextpad'      : 0.5,
        'legend.columnspacing'      : 1.0,
        'axes.color_cycle'          : colors(8),
        'axes.formatter.useoffset'  : False,
        "text.latex.preamble": [
            r"\usepackage{siunitx}",
            r"\usepackage{helvet}",
            r"\usepackage[usenames]{color}",
            r"\usepackage{bm}",
        ],
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",  # use utf8 fonts because your computer can handle it :)
            r"\usepackage[T1]{fontenc}",  # plots will be generated using this preamble
        ],
    }
