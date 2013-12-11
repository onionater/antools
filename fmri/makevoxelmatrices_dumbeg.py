# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 18:18:18 2013

@author: amyskerry
"""

dataA1=np.random.random((20, 4))
dataA2=np.random.random((20, 4))
dataB1=np.random.random((20, 4))
dataB2=np.random.random((20, 4))
dataB2[0:9,:]=dataB2[0:9,:]*.4
dataB1[0:9,:]=dataB1[0:9,:]*.4
dataA1[10:20,:]=dataA1[10:20,:]*.4
dataA2[10:20,:]=dataA2[10:20,:]*.4
#pcolor(dataA1, cmap='hot')
#pcolor(dataA2, cmap='hot')
#pcolor(dataB1, cmap='hot')
pcolor(dataB2, cmap='hot')