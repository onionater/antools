# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 13:13:29 2013

@author: amyskerry
"""
##CORRESPONDING IPNB=NDIM
import csv
import aeslazy as asl
import numpy as np
from itertools import *
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.io
from sklearn import svm, cluster, decomposition
import dealwithNDIMdata_funcs as ndim

global othercols, excludecols, othercols
filename='/Users/amyskerry/NDE_dimdl.csv'
#important columns
othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts']
suffix='allvars'
smallfig=[3,2]
screesize=[4,3]
matrixsize=[6,6]
largefig=[12,8]

if suffix=='allvars':
    excludecols=[]
elif suffix=='nv':
    excludecols=['pleasantness', 'goal_consistency', 'safety']
elif suffix=='vonly':
    excludecols=['expectedness','fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'self_involvement']

# for reference: dims included='expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'safety', 'self_involvement'
#I want to specify an intuitive ordering for visualizing dimensions
newdimordering=['familiarity','expectedness','certainty','suddenness','pleasantness', 'goal_consistency',  'control', 'fixing','self_cause','agent_cause', 'agent_intention', 'coping','pressure', 'freedom', 'moral','fairness', 'past_present', 'bodily_disease','consequences', 'safety', 'close_others','people','mental_states', 'others_knowledge', 'confidence','relevance', 'self_involvement']

        
# find useable subejcts and define vectors of class labels
[subjects, dims, emolabelmapping]=ndim.extractdata(filename, excludecols, othercols, newdimordering)
keepers=[subj for subj in subjects if subj.passedcheck()]
qlabels=set([keep.label for keep in keepers])
emolabels=set(keep.emo for keep in keepers)
keepers=ndim.assignCVfolds(keepers,qlabels,emolabels)
#actualy emolabels are randomly orded, here use manually sorted labels
[orderedlabels, orderedemos]=ndim.orderlists(emolabels,qlabels,keepers)

#compute item, emo, and dim avgs
[itemavgs,itemlabels, dimlabels, itememos]=ndim.getitemavgs(keepers,orderedlabels, dims)
[emoavgs, emolabels, dimlabels]=ndim.getemoavgs(keepers,orderedemos, dims)
#for row in emoavgs:
#    printables.append([round(x) for x in row])
#print printables
ndim.plotweightmatrix('emo-avgs x dimensions)', dimlabels, emolabels, emoavgs, 'emosxdims_'+suffix+'.png')
dimavgs=np.array(itemavgs).T
ndim.plotcorrmatrix('item-wise correlations (of avg item vectors of dim scores)', orderedlabels, itemavgs, 'items_'+suffix+'.png')
ndim.plotcorrmatrix('emo-wise correlations (of avg emo vectors of dim scores)', orderedemos, emoavgs, 'emos_'+suffix+'.png')
ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors of item avgs)', dimlabels, dimavgs, 'dims_'+suffix+'.png')

#do clustering analysis with number of emotions imposed:
k_means = cluster.KMeans(n_clusters=len(emolabels))
k_means.fit(itemavgs)
kclusters=k_means.labels_
kclusters, itememos = zip(*sorted(zip(kclusters, itememos))) # nifty trick for zipping together, sorting, and unzipping
for cn, c in enumerate(kclusters):
    print str(c+1) +': '+itememos[cn]

thresh=.02 #.02% variance explained
#do pca with dimensions as columns
[dim_eigenvectors, dim_eigenvalues, dim_transformed, dim_evlabels, dim_evvalues]=ndim.myPCA(thresh, np.array(itemavgs), 'PCA on dimensions', dimlabels)
[passedvals, passnames]=ndim.eigentable(emolabelmapping,dim_evlabels,dim_evvalues,num=3)
ndim.plotcorrmatrix('item-wise correlations (of tranformed item vectors in dimension PC space)', orderedlabels, dim_transformed, 'RD_items_'+suffix+'.png')
#do pca with items as columns
[item_eigenvectors, item_eigenvalues, item_transformed, item_evlabels,item_evvalues]=ndim.myPCA(thresh, np.array(itemavgs).T, 'PCA on items', orderedlabels)
[passedvals, passnames]=ndim.eigentable(emolabelmapping,item_evlabels,item_evvalues,num=3)
ndim.plotcorrmatrix('item-wise correlations (of tranformed dimension vectors in item PC space)', dimlabels, item_transformed, 'RD_items_'+suffix+'.png')


#do things seperately for different subsets of the items
## note to do randomized permutations rather than fixed folds based on hitnum, put the following inside a permutation loop and set hitnum=indices[i]
#indices=range(5)
#shuffle(indices)
cvfolds=range(5)
cvtype='hitnum'
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos
    ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png')
#    
## classify, cross validate across split halves    
cvfolds=range(2)
cvtype='half'
alldata=[]
alllabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos
    ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png')
    alldata.append(theseemoavgs)
    alllabels.append(theseemolabels)
[classdeets1, accuracies1, chance1]= ndim.classify(cvfolds, alldata, alllabels)
crosscorrs=ndim.crossmatrixcorr(alldata)
ndim.plotweightmatrix('emo-wise correlations (across halves)', theseemolabels, theseemolabels, crosscorrs, 'emosimilarities_xhalves'+suffix+'.png', figuresize=[11,7])
#    
## classify cross validate across items
cvfolds=range(5)
cvtype='hitnum'
alldata=[]
alllabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos 
    ##ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png')
    alldata.append(theseemoavgs)
    alllabels.append(theseemolabels)
[classdeets2, accuracies2, chance2]= ndim.classify(cvfolds, alldata, alllabels)
crosscorrs=ndim.crossmatrixcorr(alldata)
ndim.plotweightmatrix('emo-wise correlations (across items)', theseemolabels, theseemolabels, crosscorrs, 'emosimilarities_xitems'+suffix+'.png', figuresize=[11,7])