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
    
print 'paired sample ttests'
rootdir='/Users/amyskerry/Documents/analysis2/allFSFbetas/'
roilist=['RTPJ_tomloc','LTPJ_tomloc','PC_tomloc','LSTS_tomloc','RSTS_tomloc','DMPFC_tomloc','MMPFC_tomloc','VMPFC_tomloc','rFFA_kan','lFFA_kan','rOFA_kan','lOFA_kan', 'rSTS_kan', 'lSTS_kan', 'rSTS_peelen', 'lSTS_peelen']
versions=['binary','parametric', 'mushedbinary', 'mushedbinary_mesoph','mushedparametric', 'mushedbinary_faos','mushedparam_faos']#'mushedparametric', ']
versiontypes=['b','p','mb','mb', 'mp', 'mb','mp']
subject_subset=[0,8]
#subject_subset='all'
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
    print version
    roisummaries={}
    comparisons=[['mental','social'],['mental', 'physical'],['social', 'physical'],['faces', 'objects/scenes'],['faces', 'objects'],['faces', 'scenes']]
    for key in roidata.keys():
        thisroi=roidata[key]
        if versiontypes[vn]=='b':
            conditionmushes={'mental':['me'], 'social':['so'],'physical':['ph'], 'faces':['fa'],'objects':['ob'],'scenes':['sc']} #can combine conditions to collapse them into one avg beta
            tomrows=['physical', 'social', 'mental','scenes', 'objects', 'faces']
            facerows=['physical', 'social', 'mental','scenes', 'objects', 'faces']
        elif versiontypes[vn]=='mb':
            conditionmushes={'mental':['me'], 'social':['so'],'physical':['ph'], 'faces':['fa'],'objects/scenes':['os']}   
            tomrows=['physical', 'social', 'mental','objects/scenes', 'faces']
            facerows=['physical', 'social', 'mental','objects/scenes', 'faces']
        elif versiontypes[vn]=='p':
            conditionmushes={'mental':['mexextremity^1'], 'social':['soxextremity^1'],'physical':['phxextremity^1'], 'faces':['faxextremity^1'],'objects':['obxextremity^1'],'scenes':['scxextremity^1']}
        elif versiontypes[vn]=='mp':
            conditionmushes={'mental':['mexextremity^1'], 'social':['soxextremity^1'],'physical':['phxextremity^1'], 'faces':['faxextremity^1'],'objects/scenes':['osxextremity^1']}
        roisummaries[key]=collapseconds(thisroi,key,conditionmushes)
        thisdata=roisummaries[key]
        for compare in comparisons:
            try:
                array1=getattr(thisdata, compare[0]+'summary')
                array2=getattr(thisdata, compare[1]+'summary')
                df=len([el for el in array2 if ~np.isnan(el)])-1
                t,p =  sst.ttest_rel(array1, array2)
                if not np.isnan(t):
                    string=key+', '+compare[0]+'-'+compare[1]+': t(%.0f)=%.3f, p=%.4f.' % (df,t,p)
                    print string
            except:
                pass
                #print 'could not find '+compare[0]+' or '+compare[1]

    
        
    
    
