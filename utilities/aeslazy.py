# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 14:31:34 2013

@author: amyskerry
"""
import numpy as np

def makeint(myval):
    try:
        myval=int(myval)
    except:
        pass
    return myval
    
def allindices(mylist,mycriterion):
    #takes a list and a string specifying a criterion for the list element (e.g. 'element>1'), returns indices that meet criterion   
    indices=[i for i, element in enumerate(mylist) if eval(mycriterion)]
    return indices
    
def floatrange(start, stop, step):
    myrange=[]
    r = start
    while r < stop:
        myrange.append(round(r,5))
        r += step
    return myrange
    
def binarizeregressors(stimdata, **kwargs):
    thresh=5
    if 'thresh' in kwargs.keys():
        thresh=kwargs['thresh']
    binarized=[]
    for rating in stimdata:
        binrate=int(rating>thresh)
        binarized.append(binrate)
    return binarized
    
def pairwisecorrel(listoflists,nan2one):
    if len(listoflists)>1:
        #print "mean: "+ str([str(x) for x in np.mean(listoflists,1)])
        #print "std: " + str([str(x) for x in np.std(listoflists,1)])
        corrs=np.corrcoef(listoflists)
        check=np.isnan(corrs)
        if check.any():
           corrs=np.corrcoef(listoflists) 
        tri=np.triu(corrs)
        tri[np.diag_indices_from(tri)]=0
        tri2=tri[tri !=0]
        if nan2one:
            tri2[np.isnan(tri2)]=1 #assume that nans are the result of correlating two unchanging vectors. we want to think of that as correlation=1
        tri2=tri2.flatten()
        #print np.isnan(tri2)
        avgR=np.mean(tri2)
    else:
        avgR='ONEONLY'
    return avgR
    
def addlegend(colortuples, colorlabels, axis, **kwargs):
    #if using seaborn, you can get the set of colors for the plot using current_palette = sns.color_palette()
    #order should correspond to order in which you plotted in some sense
    #can specify 'legtype' as 'inax' or 'infig', can specify location based on matplotlib legent strings/numbers
    import matplotlib.pyplot as plt
    plt.subplot(axis)
    colorboxes=[]
    for ncolor, color in enumerate(colorlabels):
        rec=plt.Rectangle((0, 0), 1, 1, color=colortuples[ncolor])
        colorboxes.append(rec)
    #defaults
    legtype='inax' 
    location='upper right'
    if 'location' in kwargs.values():
        location=kwargs['location']
    if 'legtype' in kwargs.values():
        legtype=kwargs['legtype']
    if legtype=='inax':
        plt.legend(colorboxes, colorlabels, loc=location)
    elif legtype=='infig':
        plt.figlegend(colorboxes, colorlabels, loc=location)
    else:
        print 'axis type not acceptable'        
    