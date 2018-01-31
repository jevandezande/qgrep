#!/usr/bin/env python3
import sys
import numpy as np

import matplotlib.pyplot as plt

for file in sys.argv[1:]:
    with open(file) as f:
        vals = [list(map(float, line.split())) for line in f]
    vals = np.array(vals)
    plt.plot(vals[:, 0], vals[:, 1], label=file)
    print(file)
plt.legend()
plt.show()
