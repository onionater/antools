# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 14:31:34 2013

@author: amyskerry
"""

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
    while r <= stop+step:
        myrange.append(round(r,5))
        r += step
    return myrange
    
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
    