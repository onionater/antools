# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 10:59:21 2014

@author: amyskerry
"""
import os
import glob
import csv
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def extractbetas(datafile):
    data=[]
    indices={}
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                colnames=row
                indices['cond']=colnames.index('condition')
                indices['mean']=colnames.index('Mean')
                indices['roi']=colnames.index('roi')
                indices['art']=colnames.index('artifacts removed')
                indices['subjid']=colnames.index('subject')
            else:
                data.append(row)
    return indices, data
def findfiles(rootdir,mainkey,keylist):
    foundfiles=[]
    for roi in roilist:
        os.chdir(rootdir)
        for files in glob.glob(mainkey+'*'+roi +'*.csv'):
            foundfiles.append(files)
    return foundfiles

class data():
    def __init__(self,name=[], numsubj=0):
        self.name=name
        self.numsubj=numsubj

def collapseconds(thisroi,thisroiname,conditionmushes):
    conditions=conditionmushes.keys()
    d=data(thisroiname)
    subjects=list(set([row[indices['subjid']] for row in thisroi]))
    d.numsubj=len(subjects)
    for c in conditions:
        relcs=conditionmushes[c]
        subjindvalues=[[] for subj in subjects]
        subjsumvalues=[[] for subj in subjects]
        for subjn,subj in enumerate(subjects):
            subjindvalues[subjn]=np.array([float(row[indices['mean']]) for row in thisroi if row[indices['cond']] in relcs and row[indices['subjid']]==subj])
            subjsumvalues[subjn]=np.mean(subjindvalues[subjn])
        setattr(d,c+'ind',subjindvalues)
        setattr(d,c+'summary',subjsumvalues)
        SEM=np.std(subjsumvalues)/np.sqrt(d.numsubj)
        MEAN=np.mean(subjsumvalues)
        setattr(d,c+'SEM',SEM)
        setattr(d,c+'MEAN',MEAN)
    return d
    
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
    if 'legloc' in kwargs:
        legloc=kwargs['legloc']
    else:
        legloc=1 #default legen to upper corner
    if 'legend' in args:
        plt.legend(loc=legloc)
        #plt.figlegend()
    if 'ylim' in kwargs.keys():
        thisax.set_ylim(kwargs['ylim'])
    plt.tight_layout()
    #hack
    plt.show()


rootdir='/Users/amyskerry/Documents/analysis2/FSFbetas_parametric/'
roilist=['RTPJ','LTPJ','PC','LSTS','RSTS','DMPFC','MMPFC','VMPFC','rFFA','lFFA','rOFA','lOFA', 'rSTS', 'lSTS']

foundfiles=findfiles(rootdir,'BETA_',roilist)
roidata={}
for f in foundfiles:
    if f[:8]=='BETA_ROI':
        myf=f[9:]
    else:
        myf=f[5:]
    fstop=[i for i,n in enumerate(myf) if n=='_'][1]
    flabel=myf[:fstop]
    indices, roidata[flabel]=extractbetas(f)

roisummaries={}
for key in roidata.keys():
    thisroi=roidata[key]
    #conditionmushes={'mental':['me'], 'social':['so'],'physical':['ph'], 'faces':['fa'],'objects':['ob'],'scenes':['sc']} #can combine conditions to collapse them into one avg beta
    conditionmushes={'mental':['mexextremity^1'], 'social':['soxextremity^1'],'physical':['phxextremity^1'], 'faces':['faxextremity^1'],'objects':['obxextremity^1'],'scenes':['scxextremity^1']}
    roisummaries[key]=collapseconds(thisroi,key,conditionmushes)
    
fig, ax = plt.subplots(2, figsize=[12,8])
figtitle='betas'
xaxis='ROI'
yaxis='Beta value'
rows=conditionmushes.keys()
colorscheme= sns.color_palette('deep', len(rows))
#specifi to tomrois
#want more intuitive ordering
tomrows=['physical', 'social', 'mental','scenes', 'objects', 'faces']
tomax=plt.subplot(ax[0])
tomcolumnlabels=roisummaries.keys()
#want more intuitive ordering
tomcolumnlabels=['DMPFC_tomloc', 'MMPFC_tomloc', 'VMPFC_tomloc', 'PC_tomloc', 'RTPJ_tomloc', 'LTPJ_tomloc', 'RSTS_tomloc','LSTS_tomloc']
tomdata=[]
tomsems=[]
for cond in tomrows:
    tomdata.append([getattr(roisummaries[key],cond+'MEAN') for key in tomcolumnlabels])
    tomsems.append([getattr(roisummaries[key],cond+'SEM') for key in tomcolumnlabels])
makebarplot(tomax,tomdata,tomsems,tomcolumnlabels,tomrows,figtitle,'',yaxis,colorscheme[:len(tomrows)], 'legend', ylim=[-.1,.41])
#faceroi
#want more intuitive ordering
facerows=['physical', 'social', 'mental','scenes', 'objects', 'faces']
faceax=plt.subplot(ax[1])
facecolumnlabels=roisummaries.keys()
#want more intuitive ordering
facecolumnlabels=[ 'rOFA_kanparcel', 'lOFA_kanparcel', 'rFFA_kanparcel', 'lFFA_kanparcel', 'rSTS_kanparcel', 'lSTS_kanparcel']
facedata=[]
facesems=[]
for cond in facerows:
    facedata.append([getattr(roisummaries[key],cond+'MEAN') for key in facecolumnlabels])
    facesems.append([getattr(roisummaries[key],cond+'SEM') for key in facecolumnlabels])
makebarplot(faceax,facedata,facesems,facecolumnlabels,facerows,figtitle,'',yaxis,colorscheme,'legend', legloc=4)



    
