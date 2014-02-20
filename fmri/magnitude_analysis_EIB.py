# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 10:59:21 2014

@author: amyskerry
"""
import os
import glob
import csv
#import seaborn as sns
import numpy as np
import pandas as pd
import pandas.rpy.common as com
from rpy2.robjects import Formula
base = com.importr('base')
stats = com.importr('stats')
import pyvttbl
import scipy.stats as sst

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
def findfiles(rootdir,mainkey,keylist,version):
    foundfiles=[]
    for roi in roilist:
        os.chdir(rootdir)
        for files in glob.glob(mainkey+'*'+roi +'*'+version+'.csv'):
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
    if subject_subset=='all':
        pass
    else:
        subjects=subjects[subject_subset[0]:subject_subset[1]]
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
        setattr(d,c+'_SEM',SEM)
        setattr(d,c+'_MEAN',MEAN)
    return d
    


#rootdir='/Users/amyskerry/Documents/analysis2/FSFbetas_parametric/'
rootdir='/Users/amyskerry/Documents/analysis2/EIB_NT_ROI_MAGNITUDE/'
roilist=['RTPJ_tomloc','LTPJ_tomloc','PC_tomloc','LSTS_tomloc','RSTS_tomloc','DMPFC_tomloc','MMPFC_tomloc','VMPFC_tomloc','rFFA_kan','lFFA_kan','rOFA_kan','lOFA_kan', 'rSTS_kan', 'lSTS_kan', 'rSTS_peelen', 'lSTS_peelen']
#subject_subset=[0,8]
versions=['']
subject_subset='all'
substring=str(subject_subset)
for vn,version in enumerate(versions):
    foundfiles=findfiles(rootdir,'BETA_',roilist,version)
    roidata={}
    for f in foundfiles:
        if f[:8]=='BETA_ROI':
            myf=f[9:]
        else:
            myf=f[5:]
        fstop=[i for i,n in enumerate(myf) if n=='_'][1]
        flabel=myf[:fstop]
        indices, roidata[flabel]=extractbetas(f)
#make pandas df
conditions=['facial_expression_negative','facial_expression_positive','situation_negative', 'situation_positive']
stimsort={'facial_expression_negative':'face','facial_expression_positive':'face','situation_negative':'situation', 'situation_positive':'situation'}
emosort={'facial_expression_negative':'negative','facial_expression_positive':'positive','situation_negative':'negative', 'situation_positive':'positive'}
thisroilist=roidata.keys()
conditionmushes={'situation_positive':['sh', 'nh'], 'situation_negative':['su','nu'],'facial_expression_positive':['mh', 'fh'], 'facial_expression_negative':['mu', 'fu']} #can combine conditions to collapse them into one avg beta
print 'repeated measures anova on betas'
for keyn,key in enumerate(thisroilist):
    mycolumns=['subject', 'condition']
    myindices=[]
    thisroi=roidata[key]
    summary=collapseconds(thisroi,key,conditionmushes)
    roivector=[]
    stimvector=[]
    emovector=[]
    condvector=[]
    subjects=[]
    count=0
    for cond in conditions:
        stimval=stimsort[cond]
        emoval=emosort[cond]
        dataarray=getattr(summary, cond+'summary')
        subjects.append(['subj'+str(valn) for valn,val in enumerate(dataarray)])
        roivector.append(dataarray)
        for el in dataarray:
            myindices.append(count)
            count=count+1
        condvector.append([cond for val in dataarray])
        emovector.append([emoval for val in dataarray])
        stimvector.append([stimval for val in dataarray])
    mycolumns.append(key)
    roivector=[np.array(vector).flatten() for vector in roivector]
    mycolumns.append('stim')
    mycolumns.append('emo')
    myindices=np.array(myindices)
    mycolumns=np.array(mycolumns)
    condvector=np.array(condvector).flatten()
    stimvector=np.array(stimvector).flatten()
    emovector=np.array(emovector).flatten()
    subjects=np.array(subjects).flatten()
    roivector=np.array(roivector).flatten()
    myindices=np.array(myindices)
    matrix=np.array([subjects, condvector, roivector,stimvector,emovector])
    newmatrix=[]
    for eln,el in enumerate(myindices):
        newmatrix.append([str(subjects[eln]), str(condvector[eln]), roivector[eln], str(stimvector[eln]), str(emovector[eln])])
    frame=pd.DataFrame(data=newmatrix, index=myindices, columns=mycolumns)
    labels=['residuals','emo', 'stim', 'interaction']     
    for labeln, label in enumerate(labels):
        fml = key+' ~ emo * stim + Error(subject/ (emo + stim + emo * stim))'  #  formula string. note that you need to explicitly specify main effects an interaction in the error term, for some reason. this formula checks out against output on vassarstats        
        dframe = com.convert_to_r_dataframe(frame, True)  # convert from pandas to R and make string columns factors
        fml_ = Formula(fml)  #  make a formula    obect
        result=base.summary(stats.aov(fml_, dframe))
        for resn,res in enumerate(result):
            thisresult=res[0]
            bothdf=[i for i in thisresult[0].iteritems()]
            if len(bothdf)>1:
                bothdfstr=str(int(bothdf[0][1]))+','+str(int(bothdf[1][1]))
            else:
                bothdfstr=str(bothdf[0][1])
            sumsq=thisresult[1][0]
            fval=thisresult[3][0]
            pval=thisresult[4][0]
            roundnum=3
            if resn==labeln and resn!=0:
                string=key+','+label+ ': F(' + bothdfstr +')=%.3f, p=%.3f' % (fval,pval)
                print string
                    
print 'paired sample ttests'
roisummaries={}
comparisons=[['facial_expression_negative','facial_expression_positive'],['situation_negative', 'situation_positive']]
for key in roidata.keys():
    thisroi=roidata[key]
    conditionmushes={'situation_positive':['sh', 'nh'], 'situation_negative':['su','nu'],'facial_expression_positive':['mh', 'fh'], 'facial_expression_negative':['mu', 'fu']} #can combine conditions to collapse them into one avg beta
    roisummaries[key]=collapseconds(thisroi,key,conditionmushes)
    thisdata=roisummaries[key]
    for compare in comparisons:
        array1=getattr(thisdata, compare[0]+'summary')
        array2=getattr(thisdata, compare[1]+'summary')
        df=len([el for el in array2 if ~np.isnan(el)])-1
        t,p =  sst.ttest_rel(array1, array2)
        string=key+', '+compare[0]+'-'+compare[1]+': t(%.0f)=%.3f, p=%.3f.' % (df,t,p)
        print string

    
        
    
    
