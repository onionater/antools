# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:19:27 2014

@author: amyskerry
"""
import scipy.io
import numpy as p
import matplotlib.pyplot as plt

def plotcorrmatrix(title, axis, datamatrix,figuresize=[8,8],cmin=-1,cmax=1, cmapspec='RdYlBu'):
    fig=plt.figure(figsize=figuresize)   
    ax=plt.subplot()
    im=plt.pcolor(np.corrcoef(datamatrix), vmin=cmin, vmax=cmax, cmap=cmapspec) #symmetrical by necessity
    plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(axis))),axis, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(axis))),axis)
    ax.set_xlabel(title)

myfile='/Users/amyskerry/Dropbox/fsfcsvs/raw_regressors.mat'
mat = scipy.io.loadmat(myfile)
binaries=mat['binary_condensed']
condlist=[name[0:2] for name in mat['videonames']]
videolist=[name[-2:] for name in mat['videonames']]
conds=list(set(condlist))
bigtimecourses=[]
conds=[str(c) for c in conds]
for c in conds:
    binlist=[list(binary) for binaryn, binary in enumerate(binaries) if condlist[binaryn]==c]
    vidlist=[int(videolist[binaryn]) for binaryn, binary in enumerate(binaries) if condlist[binaryn]==c]
    zipped=zip(vidlist,binlist)
    zipped.sort(key = lambda t: t[0])
    result = ([ a for a,b in zipped ], [ b for a,b in zipped ])
    vidlist=result[0]
    binarylist=np.array(result[1]).flatten()
    bigtimecourses.append(binarylist)

corrmatrix=np.corrcoef(bigtimecourses)
plotcorrmatrix('regressor collinearity', conds, bigtimecourses,figuresize=[5,4],cmin=-1,cmax=1, cmapspec='RdYlBu_r')
frequency=[sum(x)/len(x) for x in bigtimecourses]
string='frequencies: '
for cn,c in enumerate(conds):
    string.join(c+ ' ('+str(frequency[cn])+'), ')