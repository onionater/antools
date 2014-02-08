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
    subjwisesummary=[[] for subj in subjects]
    for c in conditions:
        relcs=conditionmushes[c]
        subjindvalues=[[] for subj in subjects]
        subjsumvalues=[[] for subj in subjects]
        for subjn,subj in enumerate(subjects):
            subjindvalues[subjn]=np.array([float(row[indices['mean']]) for row in thisroi if row[indices['cond']] in relcs and row[indices['subjid']]==subj])
            condmean=np.mean(subjindvalues[subjn])
            subjsumvalues[subjn]=condmean 
            subjwisesummary[subjn].append(condmean)
        setattr(d,c+'ind',subjindvalues)
        setattr(d,c+'summary',subjsumvalues)
        SEM=np.std(subjsumvalues)/np.sqrt(d.numsubj)
        MEAN=np.mean(subjsumvalues)
        setattr(d,c+'SEM',SEM)
        setattr(d,c+'MEAN',MEAN)
    subjnormalized=[[] for subj in subjects]
    for rown, row in enumerate(subjwisesummary):
        subjgrandmean=np.mean(np.array(row))
        for c in row:
            subjnormalized[rown].append(c-subjgrandmean)
    for cn, c in enumerate(conditions):
        normalized=[row[cn] for row in subjnormalized]
        withinSEM=np.std(normalized)/np.sqrt(d.numsubj)
        normalizedMEAN=np.mean(normalized)
        setattr(d,c+'WITHINSUBJSEM',withinSEM)
        setattr(d,c+'NORMALIZEDMEAN',normalizedMEAN)
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
        legendhandle=plt.legend(loc=legloc)
        #legend.get_title().set_fontsize('6') #legend 'Title' fontsize
        plt.setp(gca().get_legend().get_texts(), fontsize='12') #legend 'list' fontsize
        #plt.figlegend()
    if 'ylim' in kwargs.keys():
        thisax.set_ylim(kwargs['ylim'])
    plt.tight_layout()
    #hack
    plt.show()


rootdir='/Users/amyskerry/Documents/analysis2/EIB_NT_ROI_MAGNITUDE/'
roilist=['RTPJ','LTPJ','PC','LSTS','RSTS','DMPFC','MMPFC','VMPFC','rOFA','rFFA','rSTS','lSTS']

foundfiles=findfiles(rootdir,'BETA_',roilist)
roidata={}
for f in foundfiles:
    if f[:8]=='BETA_ROI':
        myf=f[9:]
    else:
        myf=f[5:]
    fstop=[i for i,n in enumerate(myf) if n=='_'][1]
    flabel=myf[:fstop]
    print flabel
    indices, roidata[flabel]=extractbetas(f)

roisummaries={}
for key in roidata.keys():
    thisroi=roidata[key]
    conditionmushes={'situation_positive':['nh', 'sh'], 'situation_negative':['nu', 'su'],'faces_positive':['mh', 'fh'], 'faces_negative':['mu', 'fu']} #can combine conditions to collapse them into one avg beta
    roisummaries[key]=collapseconds(thisroi,key,conditionmushes)
    
fig, ax = plt.subplots(2, figsize=[12,8])
#figtitle='betas'
figtitle=''
xaxis='ROI'
yaxis='Beta value'
rows=conditionmushes.keys()
#colorscheme= sns.color_palette('deep', len(rows))
colorscheme=sns.color_palette(['#010199','#6666C2','#3E7C10','#96CE80'],4)
#specifi to tomrois
#want more intuitive ordering
tomrows=['situation_positive', 'situation_negative', 'faces_positive','faces_negative']
tomax=plt.subplot(ax[0])
tomcolumnlabels=roisummaries.keys()
#want more intuitive ordering
tomcolumnlabels=['DMPFC_tomloc', 'MMPFC_tomloc', 'VMPFC_tomloc', 'lSTS_peelenpeak','rSTS_peelenflip','RTPJ_tomloc', 'LTPJ_tomloc']
tomdata=[]
tomsems=[]
for cond in tomrows:
    tomdata.append([getattr(roisummaries[key],cond+'MEAN') for key in tomcolumnlabels])
    tomsems.append([getattr(roisummaries[key],cond+'WITHINSUBJSEM') for key in tomcolumnlabels])
makebarplot(tomax,tomdata,tomsems,tomcolumnlabels,tomrows,figtitle,'',yaxis,colorscheme[:len(tomrows)], 'legend', ylim=[-1,1.5])
plt.plot([0,8], [0,0], color='#A9B9D2')
#faceroi
#want more intuitive ordering
facerows=['situation_positive', 'situation_negative', 'faces_positive','faces_negative']
faceax=plt.subplot(ax[1])
facecolumnlabels=roisummaries.keys()
#want more intuitive ordering
facecolumnlabels=['PC_tomloc', 'RSTS_tomloc','LSTS_tomloc', 'rOFA_kanparcel','rFFA_kanparcel', 'rSTS_kanparcel']
facedata=[]
facesems=[]
for cond in facerows:
    facedata.append([getattr(roisummaries[key],cond+'MEAN') for key in facecolumnlabels])
    facesems.append([getattr(roisummaries[key],cond+'WITHINSUBJSEM') for key in facecolumnlabels])
makebarplot(faceax,facedata,facesems,facecolumnlabels,facerows,figtitle,'',yaxis,colorscheme, ylim=[-.5,2]) #,'legend', legloc=4)
plt.plot([0,7], [0,0], color='#A9B9D2')



    
