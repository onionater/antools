# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 23:00:59 2013

@author: amyskerry
"""
import csv
import scipy
from statsmodels.formula.api import ols
import statsmodels.stats.weightstats as smws
import statsmodels
import numpy as np
import pandas as pd
import pandas.rpy.common as com
from rpy2.robjects import Formula
base = com.importr('base')
stats = com.importr('stats')
import pyvttbl


global othercols, conditioncol, condindex, subjcol
filename='/Users/amyskerry/Dropbox/EIB/magnitude_betas_final_NT1to27.csv'
othercols=['artifacts removed', 'subject', 'condition'] #columns to ignore
excludecols=['artifacts removed',] #columns to ignore with pandas
conditioncol='condition'
subjcol='subject'

#on way, get data from csv and make dataobjects. might be good for more complex data that you want to play with lots of different ways
class observation():
    def __init__(self, condition=[], variable=[], data=[]):
        self.condition=condition
        self.variable=variable
        self.data=data
def getcsvdeets(datafile):        
    with open(datafile, 'rU') as csvfile:
        reader=csv.reader(csvfile)
        count=0
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                colnames=row
            count+=1
    return colnames, count

def getdata(datafile, **kwargs):
    inclusioncol=None
    for k in kwargs:
        inclusioncol=kwargs
        inclusionval=kwargs[inclusioncol]
    keepers=[]
    conditions=[]
    with open(datafile, 'rU') as csvfile:
        reader=csv.reader(csvfile)
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                colnames=row
                print 'varnames in sql: '+str(colnames)
                if inclusioncol and inclusioncol in colnames:
                    incindex=colnames.index(inclusioncol)
                condindex=colnames.index(conditioncol)
                vois={col:ncol for ncol,col in enumerate(colnames) if col not in othercols}
            else:
                subjdata=row
                try:
                    if subjdata[incindex]==inclusionval:
                        conditions.append(subjdata[condindex])
                        keepers.append(subjdata)
                except:
                    conditions.append(subjdata[condindex])
                    keepers.append(subjdata)
    conditions=list(set(conditions))
    
    return keepers, conditions, vois, condindex
def sortobs(data, variables):
    alldata=[]
    for dp in data:
        for var in variables.items():
            obs=observation(data=dp[var[1]], condition=dp[condindex], variable=var[0])
            alldata.append(obs)
    return alldata
    
def pandasSEM(groupeddata, condcol):
    groupcounts=[]
    for groupname, groupdata in groupeddata:
        counts=[]
        for g in groupdata:
            if g not in condcol:
                counts.append(groupdata[g].count())
        groupcounts.append(np.sqrt(np.array(counts)))
    #print np.array(groupcounts)
    allsems=groupeddata.std()/np.array(groupcounts)
    return allsems
        

            
        
    
#old way   
[data, conditions, variables, condindex]=getdata(filename)   
dataobjs=sortobs(data,variables)

#pandas way
[columns, rows]=getcsvdeets(filename) 
names=[subjcol,conditioncol,'rTPJ', 'lTPJ', 'rATL', 'lATL', 'PC', 'dMPFC', 'mMPFC', 'vMPFC','rmSTS', 'rFFA', 'rOFA', 'rpSTC', 'lpSTC'] #new prettier names
df=pd.read_csv(filename,names=names,header=0,usecols=[xcol for xcol,col in enumerate(columns) if col not in excludecols])
df[names[2:]] = df[names[2:]].convert_objects(convert_numeric=True)

#statsmodels assumes repeated measures design
#basic stats for plotting
grouped=df.groupby(conditioncol)
basicmeans=grouped.mean()
basicstd=grouped.std()
basicsem=pandasSEM(grouped, [subjcol, conditioncol])
#grouped.boxplot()#very coarse visualization
#plt.tight_layout()

#multilevel (better)
emodict={'context_h': 'positive', 'context_u':'negative', 'face_h':'positive', 'face_u':'negative'}
stimdict={'context_h': 'situation', 'context_u':'situation', 'face_h':'face', 'face_u':'face'}
df['stim']=[stimdict[cond] for cond in df[conditioncol]]
df['emo']=[emodict[cond] for cond in df[conditioncol]]
multigrouped=df.groupby(['stim'])
#means=multigrouped.mean()
#sem=pandasSEM(multigrouped, [subjcol, 'emo', 'stim', conditioncol])
#formiat is ols('dv ~ iv1+iv2+iv3+...', pandas dataframe).fit()

#
rois=names[2:]
roundnum=3
print 'main effects of stimulus-type'
for roi in rois:
    formula=roi+' ~ emo * stim'
    interactionmodel = ols(formula, df).fit() #* specifies interaction term, and automatically includes main effects
    #print interactionmodel.summary()
    fresult= interactionmodel.f_test([0, 0, 1, 0]) # F test on stimtype
    #print fresult
    string=roi+': F('+str(fresult.df_num)+','+str(int(fresult.df_denom))+')='+str(round(fresult.fvalue[0][0],roundnum))+', p='+str(round(fresult.pvalue[0][0],roundnum))+')'
    #print string
print 'main effects of emotion'
for roi in rois:
    formula=roi+' ~ emo * stim'
    interactionmodel = ols(formula, df).fit() #* specifies interaction term, and automatically includes main effects
    #print interactionmodel.summary()
    fresult= interactionmodel.f_test([0, 1, 0, 0]) # F test on emo
    #print fresult
    string=roi+': F('+str(fresult.df_num)+','+str(int(fresult.df_denom))+')='+str(round(fresult.fvalue[0][0],roundnum))+', p='+str(round(fresult.pvalue[0][0],roundnum))+')'
    #print string
print 'emotion x stimulus-type intractions'
for roi in rois:
    formula=roi+' ~ emo * stim'
    interactionmodel = ols(formula, df).fit() #* specifies interaction term, and automatically includes main effects
    #print interactionmodel.summary()
    fresult= interactionmodel.f_test([0, 0, 0, 1]) # F test on interaction
    #print fresult
    string=roi+': F('+str(fresult.df_num)+','+str(int(fresult.df_denom))+')='+str(round(fresult.fvalue[0][0],roundnum))+', p='+str(round(fresult.pvalue[0][0],roundnum))+')'
    #print string
    
print 'repeated measures analysis'
labels=['residuals','emo', 'stim', 'interaction']
for labeln, label in enumerate(labels):
    print label
    for roi in rois:
    #R style, since statsmodel can't do repeated measures yet. treats subcol as the index for repeated measurements
        fml = roi+' ~ emo * stim + Error('+subjcol+'/ (emo + stim +emo * stim))'  #  formula string. note that you need to explicitly specify main effects an interaction in the error term, for some reason. this formula checks out against output on vassarstats
        dfr = com.convert_to_r_dataframe(df, True)  # convert from pandas to R and make string columns factors
        fml_ = Formula(fml)  #  make a formula    obect
        result=base.summary(stats.aov(fml_, dfr))
        for nr, r in enumerate(result):
            thisresult=r[0]
            bothdf=[i for i in thisresult[0].iteritems()]
            if len(bothdf)>1:
                bothdfstr=str(int(bothdf[0][1]))+','+str(int(bothdf[1][1]))
            else:
                bothdfstr=str(bothdf[0][1])
            sumsq=thisresult[1][0]
            fval=thisresult[3][0]
            pval=thisresult[4][0]
            if nr==labeln and nr!=0:
                string=roi+ ': F(' + bothdfstr +')='+str(round(fval, roundnum))+', p='+str(round(pval, roundnum))
                print string
print 'paired sample ttests'
for roi in rois:
    print roi
    for groupname, groupvalues in multigrouped:
        pos=groupvalues[roi][groupvalues['emo']=='positive'].values
        pos = pos[np.logical_not(np.isnan(pos))]
        neg=groupvalues[roi][groupvalues['emo']=='negative'].values
        neg = neg[np.logical_not(np.isnan(neg))]
        thisdf=len(neg)-1
        t,p =  scipy.stats.ttest_rel(neg, pos, axis=0)
        print groupname+': t('+str(int(thisdf))+')='+str(round(t,roundnum))+', p='+str(round(p, roundnum))
    