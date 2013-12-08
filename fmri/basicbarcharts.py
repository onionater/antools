# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 14:44:45 2013

@author: amyskerry
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def makebarplot(thisax,data,sems,columnlabels,rowlabels,title, xaxislabel,yaxislabel,colors, *args, **kwargs):
    num_cols = len(data[0])
    num_rows=len(data)
    index=np.arange(num_cols)
    tickint= float(index[1]-index[0])
    bar_width = tickint/(num_rows+1.5)
    opacity = 1
    error_config = {'ecolor': '0.5'}
    minx=tickint+index[0]+bar_width
    maxx=tickint+index[-1]+bar_width*len(data)
    for nd, d in enumerate(data):
        x=tickint+index+bar_width*nd
        plt.bar(x, d, bar_width,
                     alpha=opacity,
                     color=colors[nd],
                     yerr=sems[nd],
                     error_kw=error_config,
                     label=rowlabels[nd])
    plt.xlabel(xaxislabel)
    plt.ylabel(yaxislabel)
    plt.title(title)
    xticks=tickint+index+bar_width*nd/2+bar_width/2
    plt.xticks(xticks, (columnlabels))
    thisax.set_xlim([minx-bar_width*2, maxx+bar_width])
    if 'legend' in args:
        plt.legend(loc=1)
        #plt.figlegend()
    if 'ylim' in kwargs.keys():
        thisax.set_ylim(kwargs['ylim'])
    plt.tight_layout()
    plt.show()

#general paramteres
rows=['face_h','face_u','context_h','context_u']
colorscheme= sns.color_palette('hls', len(rows))
xaxis='ROI'
yaxis='Beta value'
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)

#ToM betas
tomfigtitle=''
tomcolumnlabels=['rTPJ','lTPJ','rATL','lATL','PC']
tomdata=[[0.0416875, -0.15301875, 0.10955, -0.127971875, -0.162084375], [0.052053125, -0.1816625, 0.12475, -0.170734375, -0.15685625], [0.22218125, -0.00178125, -0.023484375, -0.21669375, -0.04264375], [0.316271875, 0.02769375, 0.00544375, -0.193390625, 0.003353125]]
tomsems=[[0.076022028, 0.044290962, 0.106316989, 0.030437369, 0.046202834], [0.0659039, 0.041151812, 0.103407694, 0.032367454, 0.047870655], [0.088104208, 0.06600023, 0.112525696, 0.040270687, 0.050013695], [0.089598484, 0.070197803, 0.132185695, 0.046711602, 0.062464682]]

#primary ROI betas
mainfigtitle='Univariate results'
maindata=[[-0.0711625, -0.19419375, 0.021603125, -0.1820625, -0.199090625], [-0.040721875, -0.290109375, -0.1738375, -0.21884375, -0.228540625], [-0.1835625, -0.41408125, -0.37576875, -0.063390625, 0.09244375], [0.0265875, -0.236659375, -0.412684375, -0.04426875, 0.11186875]]
mainsems=[[0.129704618, 0.118412892, 0.087444736, 0.081304096, 0.072695351], [0.142802851, 0.145088214, 0.107697137, 0.06891566, 0.066335394], [0.187395974, 0.111756478, 0.099626759, 0.088058643, 0.086789187], [0.217171498, 0.130213675, 0.114465503, 0.083279301, 0.08355038]]
maincolumnlabels=['dmPFC','mmPFC','vmPFC','rpSTC','lpSTC']

fig, ax = plt.subplots(2, figsize=[10,10])
mainax=plt.subplot(ax[0])
makebarplot(mainax,maindata,mainsems,maincolumnlabels,rows,mainfigtitle,'',yaxis,colorscheme, 'legend', ylim=[-.6,.6])
tomax=plt.subplot(ax[1])
makebarplot(tomax,tomdata,tomsems,tomcolumnlabels,rows,tomfigtitle,xaxis,yaxis,colorscheme, ylim=[-.6,.6])




