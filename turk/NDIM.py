
# In[1]:



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


# In[4]:

global othercols, excludecols, othercols
filename='/Users/amyskerry/NDE_dimdl.csv'
#important columns
othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts']
suffix='allvars'
smallfig=[3,2]
screesize=[4,3]
matrixsize=[6,6]
largefig=[12,8]


# for reference: dims included='expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'safety', 'self_involvement'

# In[5]:

#I want to specify an intuitive ordering for visualizing dimensions
newdimordering=['familiarity','expectedness','certainty','suddenness','pleasantness', 'goal_consistency',  'control', 'fixing','self_cause','agent_cause', 'agent_intention', 'coping','pressure', 'freedom', 'moral','fairness', 'past_present', 'bodily_disease','consequences', 'safety', 'close_others','people','mental_states', 'others_knowledge', 'confidence','relevance', 'self_involvement']


# In[6]:

if suffix=='allvars':
    excludecols=[]
elif suffix=='nv':
    excludecols=['pleasantness', 'goal_consistency', 'safety']
elif suffix=='vonly':
    excludecols=['expectedness','fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'self_involvement']


# find useable subejcts and define vectors of class labels:

# In[7]:

[subjects, dims]=ndim.extractdata(filename, excludecols, othercols, newdimordering)
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
ndim.plotcorrmatrix('item-wise correlations (of avg item vectors of dim scores)', orderedlabels, itemavgs, 'items_'+suffix+'.png', figuresize=matrixsize)
ndim.plotcorrmatrix('emo-wise correlations (of avg emo vectors of dim scores)', orderedemos, emoavgs, 'emos_'+suffix+'.png',figuresize=matrixsize)
ndim.plotcorrmatrix('emo-wise correlations (of avg dimension vectors of item avgs)', dimlabels, dimavgs, 'dims_'+suffix+'.png',figuresize=matrixsize)


# Out[9]:

# image file:

# image file:

# image file:

# do clustering analysis with number of emotions imposed:

# In[10]:

k_means = cluster.KMeans(n_clusters=len(emolabels))
k_means.fit(itemavgs)
kclusters=k_means.labels_
kclusters, itememos = zip(*sorted(zip(kclusters, itememos))) # nifty trick for zipping together, sorting, and unzipping
#for cn, c in enumerate(kclusters):
#    print str(c+1) +': '+itememos[cn]


# do pca with dimensions as columns

# In[11]:

thresh=.02 #.02% variance explained
[dim_eigenvectors, dim_eigenvalues, dim_transformed]=ndim.myPCA(thresh, np.array(itemavgs), 'PCA on dimensions', figuresize=screesize)
# plot in PC space (based on suggested n components)
ndim.plotcorrmatrix('item-wise correlations (of tranformed item vectors in dimension PC space)', orderedlabels, dim_transformed, 'RD_items_'+suffix+'.png',figuresize=matrixsize)


# Out[11]:

# image file:

#     suggested n components: 10
# 

# image file:

# do pca with items as columns

# In[12]:

[item_eigenvectors, item_eigenvalues, item_transformed]=ndim.myPCA(thresh, np.array(itemavgs).T, 'PCA on items',figuresize=screesize)
ndim.plotcorrmatrix('item-wise correlations (of tranformed dimension vectors in item PC space)', dimlabels, item_transformed, 'RD_items_'+suffix+'.png',figuresize=matrixsize)


# Out[12]:

# image file:

#     suggested n components: 10
# 

# image file:

# In[28]:




# In[ ]:



