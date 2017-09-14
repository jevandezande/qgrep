QGrep (Quantum Grep)
====================

A repository for various scripts designed to ease using and extracting data
from quantum chemistry programs


Install
-------
* Install python3.6 (only some scripts will work with python3.4)
* Install cclib ``pip3 install cclib``
* Obtain the scripts

  * ``git clone git@github.com:jevandezande/qgrep.git``

* Edit PATH and PYTHONPATH to include scripts (bash/zsh format shown)

  * ``export PATH=$PATH:/replace/with/your/path/to/qgrep/bin/``
  * ``export PYTHONPATH=$PYTHONPATH:/replace/with/your/path/to/qgrep/``


Use
---
All of the scripts you will run are located in qgrep/bin, here are the most
useful.

* check - shows the convergence steps of an output file
* get_geom - gets the last geometry of an output file
* inup - updates an input file with the geometry from another file
* nics - finds the NICS(0) and NICS(1) points for all rings in a system
* plot - plots all steps of an output file
* qinfo - completely rewritten (and improved) version of qinfo from Jay Agarwal
* quick_opt - runs a new optimization from a given geometry (needs sq)


Configuration
-------------

You can configure the output of various codes using a `.qgrepconfig` file
placed in your home directory. For example:

.. code-block::

    [queues]
        job_id_length = 6
        name_length = 22
        small_queue = 3

