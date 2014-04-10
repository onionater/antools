# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 17:51:56 2014

@author: amyskerry
"""
import scipy.io as sio
import scipy.stats as sst
import glob
import statsmodels.stats.weightstats as smws
import numpy as np
import h5py 
import matplotlib.pylab as plt
import seaborn as sns 

class data():
    def __init__(self, roi=[], disc=[], selector=[], accuracies=[]):
        self.roi=roi
        self.disc=disc
        self.selector=selector 
        self.accuracies=accuracies 

olddir='/users/amyskerry/documents/analysis2/EIB_classificationsOLD/specifics/'
tempdir='/users/amyskerry/documents/analysis2/EIB_classificationsTEMP/specifics/'
newdir='/users/amyskerry/documents/analysis2/EIB_classificationsNEW/specifics/'
ROIlist=['DMPFC_tomloc','MMPFC_tomloc','VMPFC_tomloc','RTPJ_tomloc','LTPJ_tomloc', 'RSTS_tomloc','LSTS_tomloc','PC_tomloc','rOFA_kan','rFFA_kan','rSTS_kan','lSTS_peelen','rSTS_peelen','rpSTS_BDbiomot']
ROIstatus=['old','old','old','old','old','old','old','old', 'new', 'new', 'new', 'new', 'new', 'new']
#newdir='/users/amyskerry/documents/analysis2/ASD_classification_temp/specifics/'
#ROIlist=['DMPFC_tomloc','MMPFC_tomloc','VMPFC_tomloc','RTPJ_tomloc','LTPJ_tomloc', 'RSTS_tomloc','LSTS_tomloc','PC_tomloc','rOFA_kan','rFFA_kan','rSTS_kan','lSTS_peelen','rSTS_peelen','rpSTS_BDbiomot']
#ROIstatus=['new','new','new','new','new','new','new','new', 'new', 'new', 'new', 'new', 'new', 'new']

discriminations=['socialVSnonsoc','socialnVSsocialp','nonsocnVSnonsocp','negVSposTWO','negVSposONE','negVSpos', 'negfVSposf','negfVSposf', 'negcVSposc','negcVSposc', 'maleVSfemale', 'femalenVSfemalep','malenVSmalep','faceVScontext']
selectors=['_runs', '_runs', '_runs', '_crossruns', '_crossruns', '_stimselector', '_runs', '_gender', '_runs', '_context', '_runs', '_runs', '_runs', '_runs']
labeldict={'negVSposABSTRACT':'cross-\nstimulus', 'negfVSposf':'facial \nexpressions','negcVSposc':'situations'}
alldata=[]
for roin,thisroi in enumerate(ROIlist):
    for discn, disc in enumerate(discriminations):
        thisdisc=discriminations[discn]
        thisselector=selectors[discn]
        if ROIstatus[roin]=='old':
            rootdir=olddir
        elif ROIstatus[roin]=='temp':
            rootdir=tempdir
        elif ROIstatus[roin]=='new':
            rootdir=newdir
        thisresultfile=rootdir+thisroi+ '*'+thisdisc+'*'+thisselector+'*groupavgs.mat'
        files=glob.glob(thisresultfile)    
        if files:
            f = h5py.File(files[0],'r') 
            roidata = f.get('avgPerfGroup').value
            roidata=[float(x) for x in roidata]
            alldata.append(data(roi=thisroi, disc=thisdisc, selector=thisselector, accuracies=roidata))
            #should save this as .dat or something
for dataset in alldata:
    if dataset.disc=='negVSposTWO':
        sechalf=dataset.accuracies
        curroi=dataset.roi
        for paireddataset in alldata:
            if paireddataset.roi==curroi and paireddataset.disc=='negVSposONE':
                firsthalf=paireddataset.accuracies
                combined=[]
                for eln,el in enumerate(sechalf):
                    combined.append((el+firsthalf[eln])/2)
                alldata.append(data(roi=curroi, disc='negVSposABSTRACT', selector='_crossruns', accuracies=combined))
discriminations.append('negVSposABSTRACT')
selectors.append('_crossruns')
print 'tests of classification accuracies (one-tailed one sample t test against chance of .5)'
for discn,disc in enumerate(discriminations):
    sel=selectors[discn]
    print 'disc='+disc+', selector='+sel
    for roi in ROIlist:
        for dataset in alldata:
            t=0
            p=0
            if dataset.roi==roi and dataset.selector==sel and dataset.disc==disc:
                #print dataset.roi
                keepers=[el for el in dataset.accuracies if ~np.isnan(el)]
                #print keepers
                [t,p]=sst.ttest_1samp(keepers, .5)
                #[t2,p2]=smws.ztest(keepers, value=.5, alternative='larger') smws is off in the pvalues... unclear why
                meanacc=np.mean(keepers)
                df=len(keepers)-1
                if t>0:
                    string=roi+': M=%.3f, t(%.0f)=%.3f,p=%.3f.' %(meanacc,df,t,p/2) #dividing by two for one-tailed test
                else:
                    string=roi+': M=%.3f, t(%.0f)=%.3f,p=%.3f.' %(meanacc,df,t,(1-p/2))
                #string2=roi+': M=%.3f, t(%.0f)=%.3f,p=%.3f.' %(meanacc,df,t2,p2)
                print string
                #print string2
print 'comparions of classification accuracies (one-tailed paired samples t test)'
comparisonsets=[['negfVSposf','negVSposABSTRACT'],['negfVSposf','negcVSposc'],['socialnVSsocialp','nonsocnVSnonsocp']]
selectorsets=[['_runs', '_crossruns'],['_runs', '_runs'],['_runs','_runs']]
for comparen,compare in enumerate(comparisonsets):
    selset=selectorsets[comparen]
    print 'comparison='+compare[0]+' vs '+compare[1]
    for roi in ROIlist:
        compA=0
        compB=0
        for dataset in alldata:
            t=0
            p=0
            if dataset.roi==roi and dataset.selector==selset[0] and dataset.disc==compare[0]:
                compA=[el for el in dataset.accuracies if ~np.isnan(el)]
            elif dataset.roi==roi and dataset.selector==selset[1] and dataset.disc==compare[1]:
                compB=[el for el in dataset.accuracies if ~np.isnan(el)]
        if compA>0:
            [t,p]=sst.ttest_rel(compA, compB)
            #[t2,p2]=smws.ztest(keepers, value=.5, alternative='larger') smws is off in the pvalues... unclear why
            meanA=np.mean(compA)
            meanB=np.mean(compB)
            df=len(compA)-1
            string=roi+': M=%.3f, M=%.3f, t(%.0f)=%.3f,p=%.3f.' %(meanA,meanB,df,t,p/2) #divide p by two for one-tailed test
            print string
analysissets=['Medial Prefrontal Cortex', 'Posterior Superior Temporal Cortex', 'Face regions', 'Theory of mind regions']
setrois={'Medial Prefrontal Cortex':['DMPFC_tomloc','MMPFC_tomloc','VMPFC_tomloc'], 'Posterior Superior Temporal Cortex':['lSTS_peelen','rSTS_peelen'],'Face regions':['rOFA_kan','rFFA_kan','rSTS_kan'], 'Theory of mind regions':['RTPJ_tomloc','LTPJ_tomloc', 'RSTS_tomloc','LSTS_tomloc','PC_tomloc']}
setdiscs={'Medial Prefrontal Cortex':['negfVSposf','negcVSposc','negVSposABSTRACT'], 'Posterior Superior Temporal Cortex':['negfVSposf','negcVSposc','negVSposABSTRACT'],'Face regions':['negfVSposf','negcVSposc','negVSposABSTRACT'], 'Theory of mind regions':['negfVSposf','negcVSposc','negVSposABSTRACT']}
setselectors={'Medial Prefrontal Cortex':['_runs','_runs','_crossruns'], 'Posterior Superior Temporal Cortex':['_runs','_runs','_crossruns'],'Face regions':['_runs','_runs','_crossruns'], 'Theory of mind regions':['_runs','_runs','_crossruns']}
ylims={'Medial Prefrontal Cortex':[.49,.58],'Posterior Superior Temporal Cortex':[.48,.56],'Face regions':[.475,.575],'Theory of mind regions':[.46,.56]}
chance=.5
for analysis in analysissets:
    theserois=setrois[analysis]
    thesediscs=setdiscs[analysis]
    theseselectors=setselectors[analysis]
    theseylims=ylims[analysis]
    for roi in theserois:
        axislabels=['empty']
        allplotsmean=[]
        allplotssem=[]
        for discn,disc in enumerate(thesediscs):
            sel=theseselectors[discn]
            for dataset in alldata:
                if dataset.roi==roi and dataset.disc==disc and dataset.selector==sel:
                    string=roi+', '+disc+','+sel
                    #print string
                    values=np.array(dataset.accuracies)
                    mean=np.nanmean(values)
                    #print mean
                    SEM=np.nanstd(values)/np.sqrt(len(values))
                    #print SEM
                    allplotsmean.append(mean)
                    allplotssem.append(SEM)
                    axislabels.append(labeldict[disc])
        base=np.array([0 for el in allplotsmean])
        colors=['g','b','r']
        colors=sns.color_palette(['#3E7C10','#6666C2', '#884433'])
        sns.set_axes_style('nogrid', 'notebook')
        sns.despine()
        fig, axis = plt.subplots(1, figsize=[2.6,4]) 
        for valn,val in enumerate(allplotsmean):
            means=[el for el in base]
            means[valn]=val
            sems=[el for el in base]
            sems[valn]=allplotssem[valn]
            color=colors[valn]
            axis.errorbar(np.arange(len(means)), np.array(means), yerr=np.array(sems),elinewidth=3, markersize=12, fmt='o', color=color) 
            #axis.errorbar(np.arange(len(means[0:2])), np.array(means[0:2]), yerr=np.array(sems[0:2]),elinewidth=3, markersize=12, fmt='o', color=color) 
        axis.locator_params(nbins=len(allplotsmean)+2)
        #axis.locator_params(nbins=2,axis='x')
        #axis.set_xticklabels(axislabels[0:2], visible=0)
        axis.set_xticklabels(axislabels, visible=1)
        xlim_deets=[-.25, len(allplotsmean)-.75]
        #xlim_deets=[-.25, len(allplotsmean[0:2])-.75]
        axis.set_xlim(xlim_deets)
        axis.set_ylim([theseylims[0], theseylims[1]])
        axis.set_title(roi)
        axis.plot(xlim_deets, [chance,chance], ls='dashed', color='orange')
        plt.tight_layout()
