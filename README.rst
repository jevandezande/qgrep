QGrep (Quantum Grep)
====================

A repository for various scripts designed to ease using and extracting data
from quantum chemistry programs


Install
-------
* Obtain the scripts
 * ``git clone git@github.com:jevandezande/qgrep.git``
* Edit PATH and PYTHONPATH to include scripts (bash/zsh format shown)
 * ``export PATH=$PATH:/replace/with/your/path/to/qgrep/bin/``
 * ``export PYTHONPATH=$PYTHONPATH:/replace/with/your/path/to/qgrep/``


Use
---
All of the scripts you will run are located in qgrep/bin, here are the most useful.
 * get_geom - gets the last geometry of an output file
 * plot - plots all steps of an output file
 * check_convergence - lists the convergence steps of an output file
 * qinfo2 - updated version of qinfo
