
# In[1]:

pylab inline


# Out[1]:

#     Populating the interactive namespace from numpy and matplotlib
# 

# In[2]:

import csv
import aeslazy as asl
import numpy as np
from itertools import *
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.io
from sklearn import svm, cluster, decomposition
import dealwithNDIMdata_funcs as ndim
import itertools


# In[3]:

global othercols, excludecols, othercols
filename='/Users/amyskerry/NDE_dimdl.csv'
#important columns
othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts']
suffix='allvars'
smallfig=[3,2]
screesize=[4,3]
matrixsize=[7,6]
largefig=[12,8]


# In[4]:

alldims=['expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'safety', 'self_involvement']


# In[5]:

#I want to specify an intuitive ordering for visualizing dimensions
newdimordering=['familiarity','expectedness','certainty','suddenness','pleasantness', 'goal_consistency',  'control', 'fixing','self_cause','agent_cause', 'agent_intention', 'coping','pressure', 'freedom', 'moral','fairness', 'past_present', 'bodily_disease','consequences', 'safety', 'close_others','people','mental_states', 'others_knowledge', 'confidence','relevance', 'self_involvement']


# In[6]:

if suffix=='allvars':
    excludecols=[]
elif suffix=='nv':
    excludecols=['pleasantness', 'goal_consistency', 'safety']
elif suffix=='vonly':
    valence=['pleasantness', 'goal_consistency', 'safety']
    excludecols=[i for i in alldims if i not in valence]
    #excludecols=['expectedness','fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'self_involvement']


# find useable subejcts and define vectors of class labels:

# In[7]:

[subjects, dims,emolabelmapping]=ndim.extractdata(filename, excludecols, othercols, newdimordering)
keepers=[subj for subj in subjects if subj.passedcheck()]
qlabels=set([keep.label for keep in keepers])
emolabels=set(keep.emo for keep in keepers)
keepers=ndim.assignCVfolds(keepers,qlabels,emolabels)


# actualy emolabels are randomly orded, here use manually sorted labels:

# In[8]:

[orderedlabels, orderedemos]=ndim.orderlists(emolabels,qlabels,keepers)


# compute item, emo, and dim avgs:

# In[9]:

[itemavgs,itemlabels, dimlabels, itememos]=ndim.getitemavgs(keepers,orderedlabels, dims)
[emoavgs, emolabels, dimlabels]=ndim.getemoavgs(keepers,orderedemos, dims)
dimavgs=np.array(itemavgs).T
ndim.plotweightmatrix('emo-avgs x dimensions', dimlabels, emolabels, emoavgs, 'emosxdims_'+suffix+'.png', figuresize=[10,6],cmin=0, cmax=10)
ndim.plotcorrmatrix('item-wise correlations (of avg item vectors of dim scores)', orderedlabels, itemavgs, 'items_'+suffix+'.png', figuresize=matrixsize)
ndim.plotcorrmatrix('emo-wise correlations (of avg emo vectors of dim scores)', orderedemos, emoavgs, 'emos_'+suffix+'.png',figuresize=matrixsize)
ndim.plotcorrmatrix('dim-wise correlations (of avg dimension vectors of item avgs)', dimlabels, dimavgs, 'dims_'+suffix+'.png',figuresize=matrixsize)


# Out[9]:

# image file:

# image file:

# image file:

# image file:

# do clustering analysis with number of emotions imposed:

# In[10]:

k_means = cluster.KMeans(n_clusters=len(emolabels))
k_means.fit(itemavgs)
kclusters=k_means.labels_
kclusters, itememos = zip(*sorted(zip(kclusters, itememos))) # nifty trick for zipping together, sorting, and unzipping
for cn, c in enumerate(kclusters):
    print str(c+1) +': '+itememos[cn]


# Out[10]:

#     1: Joyful
#     1: Joyful
#     1: Proud
#     1: Proud
#     1: Proud
#     1: Proud
#     2: Annoyed
#     2: Annoyed
#     2: Disgusted
#     2: Disgusted
#     2: Disgusted
#     2: Embarrassed
#     2: Guilty
#     3: Angry
#     3: Grateful
#     3: Grateful
#     4: Disappointed
#     4: Impressed
#     4: Impressed
#     4: Impressed
#     4: Impressed
#     4: Surprise
#     5: Angry
#     5: Angry
#     5: Annoyed
#     5: Annoyed
#     5: Annoyed
#     5: Apprehensive
#     5: Apprehensive
#     5: Disappointed
#     5: Disgusted
#     5: Embarrassed
#     5: Lonely
#     5: Lonely
#     5: Sad
#     6: Afraid
#     6: Afraid
#     6: Disgusted
#     7: Apprehensive
#     7: Apprehensive
#     7: Guilty
#     8: Nostalgic
#     9: Grateful
#     9: Grateful
#     9: Hopeful
#     9: Hopeful
#     9: Joyful
#     9: Joyful
#     10: Embarrassed
#     10: Embarrassed
#     10: Embarrassed
#     10: Grateful
#     10: Guilty
#     10: Guilty
#     11: Disappointed
#     11: Disappointed
#     11: Surprise
#     12: Content
#     12: Hopeful
#     12: Nostalgic
#     12: Nostalgic
#     12: Nostalgic
#     12: Nostalgic
#     13: Joyful
#     13: Surprise
#     13: Surprise
#     13: Surprise
#     14: Apprehensive
#     14: Disappointed
#     14: Sad
#     14: Sad
#     14: Sad
#     15: Afraid
#     15: Afraid
#     15: Afraid
#     15: Angry
#     15: Angry
#     15: Sad
#     16: Guilty
#     17: Hopeful
#     17: Hopeful
#     17: Impressed
#     17: Lonely
#     17: Lonely
#     17: Lonely
#     17: Proud
#     18: Content
#     18: Content
#     18: Content
#     18: Content
# 

# do pca with dimensions as columns
# display dimensions with highest loadings on top eigenvectors

# In[11]:

thresh=.02 #.02% variance explained
[dim_eigenvectors, dim_eigenvalues, dim_transformed, dim_evlabels, dim_evvalues]=ndim.myPCA(thresh, np.array(itemavgs), 'PCA on dimensions', dimlabels, figuresize=screesize)
[passedvals, passnames]=ndim.eigentable(emolabelmapping,dim_evlabels,dim_evvalues,num=3)
# plot in PC space (based on suggested n components)
ndim.plotcorrmatrix('item-wise correlations (of tranformed item vectors in dimension PC space)', orderedlabels, dim_transformed, 'RD_items_'+suffix+'.png',figuresize=matrixsize)


# Out[11]:

#     (27,)
# 

# image file:

#     eigenvector #1--- high-loaders: fairness, goal_consistency, pleasantness; loadings: 0.3, 0.367, 0.393
#     eigenvector #2--- high-loaders: people, relevance, consequences; loadings: 0.33, 0.426, 0.471
#     eigenvector #3--- high-loaders: pressure, control, self_cause; loadings: 0.242, 0.417, 0.501
#     eigenvector #4--- high-loaders: expectedness, safety, others_knowledge; loadings: 0.202, 0.236, 0.253
#     eigenvector #5--- high-loaders: past_present, self_involvement, agent_intention; loadings: 0.192, 0.284, 0.373
#     eigenvector #6--- high-loaders: past_present, moral, expectedness; loadings: 0.24, 0.243, 0.249
#     eigenvector #7--- high-loaders: safety, moral, fairness; loadings: 0.296, 0.305, 0.307
#     eigenvector #8--- high-loaders: self_cause, bodily_disease, close_others; loadings: 0.204, 0.208, 0.616
#     eigenvector #9--- high-loaders: agent_intention, others_knowledge, consequences; loadings: 0.229, 0.247, 0.416
#     eigenvector #10--- high-loaders: mental_states, freedom, pleasantness; loadings: 0.197, 0.256, 0.3
# 

# image file:

# do pca with items as columns
# display items with highest loadings on top eigenvectors

# In[12]:

#[item_eigenvectors, item_eigenvalues, item_transformed, item_evlabels,item_evvalues]=ndim.myPCA(thresh, np.array(itemavgs).T, 'PCA on items', orderedlabels, figuresize=screesize)
#[passedvals, passnames]=ndim.eigentable(emolabelmapping,item_evlabels,item_evvalues,num=3)
#ndim.plotcorrmatrix('item-wise correlations (of tranformed dimension vectors in item PC space)', dimlabels, item_transformed, 'RD_items_'+suffix+'.png',figuresize=matrixsize)


# classify emo based on all dimensions
# cross validate across split halves
# display emo similarity space in each fold  
# 

# In[15]:

cvfolds=range(2)
cvtype='half'
alldata=[]
alllabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos
    #ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors) in each fold', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=smallfig)
    alldata.append(theseemoavgs)
    alllabels.append(theseemolabels)
[classdeets1, accuracies1, chance1]= ndim.classify(cvfolds, alldata, alllabels)
crosscorrs=ndim.crossmatrixcorr(alldata)
ndim.plotweightmatrix('emo-wise correlations (across halves)', theseemolabels, theseemolabels, crosscorrs, 'emosimilarities_xhalves'+suffix+'.png', figuresize=[7,5],cmin=-1, cmax=1, cmapspec='RdYlBu')


# Out[15]:

# image file:

# classify emo based on dimensions...do things seperately for different subsets of the items. 
# note: do randomized permutations rather than fixed folds based on hitnum...
# put the following inside a permutation loop and set hitnum=indices[i]
# display similarity matrices for different folds (comment out the plotting if doing permutation)
# 

# In[16]:

#indices=range(5)
#shuffle(indices)
cvfolds=range(5)
cvtype='hitnum'
alldata=[]
alllabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos 
    #ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors) in each fold', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=smallfig)
    alldata.append(theseemoavgs)
    alllabels.append(theseemolabels)
[classdeets2, accuracies2, chance2]= ndim.classify(cvfolds, alldata, alllabels)
crosscorrs=ndim.crossmatrixcorr(alldata)
ndim.plotweightmatrix('emo-wise correlations (across items)', theseemolabels, theseemolabels, crosscorrs, 'emosimilarities_xitems'+suffix+'.png', figuresize=[7,5], cmin=-1, cmax=1, cmapspec='RdYlBu')


# Out[16]:

# image file:

# figure out how to show that you are capitalizing on a higher-d space
#     -show that eigenvectors explaining the most variance aren't just valence
#     -show that you can classify even if excluding valence related dimensions
#     -show that you take a hit if reducing to massively lower-d space
#     -show that you can classify above chance when analyzing positive and negative valence separately

# In[14]:




# In[ ]:



