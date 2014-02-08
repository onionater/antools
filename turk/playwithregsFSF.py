# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:19:27 2014

@author: amyskerry
"""
##CORRESPONDING IPNB=FSF_REGRESSORS
import scipy.io
import numpy as p
import matplotlib.pyplot as plt
import statsmodels.stats.outliers_influence

def plotcorrmatrix(title, axis, datamatrix,figuresize=[8,8],cmin=-1,cmax=1, cmapspec='RdYlBu', onecorner=0):
    fig=plt.figure(figsize=figuresize)   
    ax=plt.subplot()
    corrmatrix=np.corrcoef(datamatrix)
    if onecorner:
        tri=np.triu(corrmatrix)
        tri[tri==0]=np.nan
        pltmatrix=tri
    else:
        pltmatrix=corrmatrix
    im=plt.pcolor(pltmatrix, vmin=cmin, vmax=cmax, cmap=cmapspec) #symmetrical by necessity
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
#plot correlation between regressors
plotcorrmatrix('regressor collinearity', conds, bigtimecourses,figuresize=[5,4],cmin=-1,cmax=1, cmapspec='RdYlBu_r')
frequency=[float(sum(x))/len(x) for x in bigtimecourses]
string='proportion of timepoints: \n'
for cn,c in enumerate(conds):
    string=string+c+ ': '+str(round(frequency[cn],2))+'\n '
print string
print "variance inflation factors" #VIF=a measure for the increase of the variance of the parameter estimates if an additional variable, given by exog_idx is added to the linear regression... one recommendation is that VIF > 5 is highly collinear with the other explanatory variables, and the parameter estimates will have large standard errors
for inum, i in enumerate(conds):
    print i+': ' + str(statsmodels.stats.outliers_influence.variance_inflation_factor(np.array(bigtimecourses).T, inum))
