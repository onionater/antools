# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 18:34:17 2014

@author: amyskerry
"""

import matplotlib
import numpy as np
matplotlib.use('webagg')
import matplotlib.pyplot as plt

X = np.linspace(-np.pi, np.pi, 256, endpoint=True) # create an array from -pi to pi
COS, SIN = np.cos(X), np.sin(X)
plt.plot(X, COS, label='cos')
plt.plot(X, SIN, label='sin')
plt.show()