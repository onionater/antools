# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#pylab inline

# <codecell>

import sys 
sys.path.append('/Users/amyskerry/Dropbox/antools/utilities')

import csv
import aeslazy as asl
import numpy as np
from itertools import *
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.io
from sklearn import svm, cluster, decomposition
import aesbasicfunctions as abf
import dealwithNDIMdata_funcs as ndim
#import dealwithNDEdata as nde
import analyzeNDE as nde_data
#import itertools

# <rawcell>

# <codecell>
#
#NDIM
#rootdir='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/NDIM_data/'
rootdir='/Users/amyskerry/'
#filename=rootdir+'/sqldata/NDE_dimdl2.csv
filename='NDE_dimdl.csv'
savepath=rootdir+'/outputfigs/'

#appraisals
appraisalfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/task/appdata/appraisals.csv/'


#NDE
resultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim/data/NDE_data/sqldata/NDEdl.csv'
#resultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/NDE_data/sqldata/NDEdl_combined.csv' #contains NDEdl.csv and the first row of the two woops (with checks manually corrected since these subjects didn't have Neutral option)

# checkout NDE data...

# <codecell>
####
#NDE INFO
#checkquestions=(201,202)#(86,87)
expectedanswers=('Neutral', 'Neutral') #what do you expect from these two checks
#orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise','Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed']
maxN=10 #blacklist questions with this many or more
inclusioncols={'submission_date': (lambda inputval: inputval not in ('NULL',))} #key=column, value=function returning whether given item is a keeper

#NDIM INFO

# <codecell>

suffix='vonly'

othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts']
#orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise', 'Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed'] #same as NDE but without surprise
orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
names,data= abf.extractdata(appraisalfile)
alldims=[row['Dqname'] for row in data]
newdimordering=['familiarity','expectedness','certainty','suddenness','pleasantness', 'goal_consistency',  'control', 'fixing','self_cause','agent_cause', 'agent_intention', 'coping','pressure', 'freedom', 'moral','fairness', 'past_present', 'bodily_disease','consequences', 'safety', 'close_others','people','mental_states', 'others_knowledge', 'confidence','relevance', 'self_involvement']
valenceddims=['pleasantness', 'goal_consistency', 'safety']
columndict={'subdate':'submission_date', 'check':'main_character','explicit':'emotion','subjid':'subjid'}
suffixmappings={'allvars':[], 'nv':valenceddims, 'vonly':[i for i in alldims if i not in valenceddims] }
excludecols=suffixmappings[suffix]

# <codecell>
#dumb parameters
bigfig=[8,10]
medfig=[6,4]
smallfig=[3,2]
screesize=[4,3]
matrixsize=[7,6]
largefig=[12,8]
thresh=7


####

#NDE main analyses
#<codecell>
[varnames,datamatrix]=nde_data.extractdata(resultsfile)
checkfailers=nde_data.findcheckfailers(datamatrix, varnames, checkquestions, expectedanswers)
incfailers=nde_data.testinclusioncrit(datamatrix, varnames, inclusioncols)
excl_list=[cf*incfailers[cfn] for cfn,cf in enumerate(checkfailers)]
[labels,answers,correctness,responses,counts]=nde_data.scoreitems(varnames,datamatrix,checkquestions,excl_list)
stimmeans=list(np.nanmean(correctness,0))
f,axes=plt.subplots(2)
axes[0].bar(range(len(stimmeans)), stimmeans);axes[0].set_xlim([0,len(stimmeans)]);axes[0].set_title('accuracies')
axes[1].bar(range(len(stimmeans)), counts);axes[1].set_xlim([0,len(stimmeans)]);axes[1].set_title('counts')
[emonames, emoaccuracies, emoerrorcounts, emoerrors]=nde_data.condenseaccuracies(varnames, stimmeans,answers,checkquestions, responses,orderedemos)
blacklist=[l for ln, l in enumerate(labels) if counts[ln]>maxN]
nde_data.printdeets(labels, counts, stimmeans, blacklist, maxN)

# <rawcell>

# NDIM data...

# <codecell>

#I want to specify an intuitive ordering for visualizing dimensions
newdimordering= ndim.reorderdims(newdimordering, excludecols, alldims)
# <markdowncell>

# find useable subejcts and define vectors of class labels:

# <codecell>

[subjects, dims,labelemomapping]=ndim.extractdata(filename, excludecols, othercols, newdimordering)
keepers=[subj for subj in subjects if subj.passedcheck()]
keeperlabels,keeperemos=[keep.label,keep.emo for keep in keepers]
qlabels=uniquifyordered(keeperlabels)#shouldn't matter that these are ordered, but just in case
emolabels=uniquifyordered(keeperemos)#shouldn't matter that these are ordered, but just in case
keepers=ndim.assignCVfolds(keepers,qlabels,emolabels,emolabelmapping)

# <markdowncell>

# actualy emolabels are randomly orded, here use manually sorted labels:

# <codecell>

[orderedlabels, orderedemos]=ndim.orderlists(emolabels,qlabels,keepers,orderemos,emolabelmapping)

# <markdowncell>

# compute item, emo, and dim avgs:

# <codecell>

[itemavgs,itemlabels, dimlabels, itememos]=ndim.getitemavgs(keepers,orderedlabels, dims)
[emoavgs, emolabels, dimlabels]=ndim.getemoavgs(keepers,orderedemos, dims)
dimavgs=np.array(itemavgs).T
ndim.plotweightmatrix(savepath,'emo-avgs x dimensions', dimlabels, emolabels, emoavgs, 'emosxdims_'+suffix+'.png', figuresize=[10,6],cmin=0, cmax=10)
ndim.plotcorrmatrix(savepath,'item-wise correlations (of avg item vectors of dim scores)', orderedlabels, itemavgs, 'items_'+suffix+'.png', figuresize=matrixsize)
ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg emo vectors of dim scores)', orderedemos, emoavgs, 'emos_'+suffix+'.png',figuresize=matrixsize)
ndim.plotcorrmatrix(savepath,'dim-wise correlations (of avg dimension vectors of item avgs)', dimlabels, dimavgs, 'dims_'+suffix+'.png',figuresize=matrixsize)

# <codecell>

# <codecell>

#temporarily limiting to subset of emos
basicsubset=['Afraid', 'Joyful', 'Disgusted', 'Sad', 'Surprise', 'Angry']
#[itemavgs, itemlabels, itememos, emoavgs, emolabels]=reduce2subset(basicsubset,itemavgs, itemlabels, itememos, emoavgs, emolabels)

# <markdowncell>

# do clustering analysis with number of emotions imposed:

# <codecell>

k_means = cluster.KMeans(n_clusters=len(emolabels))
k_means.fit(itemavgs)
kclusters=k_means.labels_
kclusters, itememos = zip(*sorted(zip(kclusters, itememos))) # zipping together, sorting, and unzipping
for cn, c in enumerate(kclusters):
    print str(c+1) +': '+itememos[cn]

# <rawcell>

# do pca with dimensions as columns
# display dimensions with highest loadings on top eigenvectors

# <codecell>

thresh=.02 #.02% variance explained
[dim_eigenvectors, dim_eigenvalues, dim_transformed, dim_evlabels, dim_evvalues]=ndim.myPCA(thresh, np.array(itemavgs), 'PCA on dimensions', dimlabels, figuresize=screesize)
[passedvals, passnames]=ndim.eigentable(emolabelmapping,dim_evlabels,dim_evvalues,num=3)
# plot in PC space (based on suggested n components)
ndim.plotcorrmatrix(savepath,'item-wise correlations (of tranformed item vectors in dimension PC space)', orderedlabels, dim_transformed, 'RD_items_'+suffix+'.png',figuresize=matrixsize)

# <rawcell>

# do pca with items as columns
# display items with highest loadings on top eigenvectors

# <codecell>

#[item_eigenvectors, item_eigenvalues, item_transformed, item_evlabels,item_evvalues]=ndim.myPCA(thresh, np.array(itemavgs).T, 'PCA on items', orderedlabels, figuresize=screesize)
#[passedvals, passnames]=ndim.eigentable(emolabelmapping,item_evlabels,item_evvalues,num=3)
#ndim.plotcorrmatrix(savepath,'item-wise correlations (of tranformed dimension vectors in item PC space)', dimlabels, item_transformed, 'RD_items_'+suffix+'.png',figuresize=matrixsize)

# <rawcell>

# classify emo based on all dimensions
# cross validate across split halves
# display emo similarity space in each fold  

# <codecell>

cvfolds=range(2)
cvtype='half'
listofemoavgs=[]
listofemolabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    #[theseitemavgs, theseitemlabels, theseitememos, theseemoavgs, theseemolabels]=reduce2subset(basicsubset,theseitemavgs, theseitemlabels, theseitememos, theseemoavgs, theseemolabels)
    [theseorderedlabels, theseorderedemos]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos
    ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg dimension vectors) in each fold', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=smallfig)
    listofemoavgs.append(theseemoavgs)
    listofemolabels.append(theseemolabels)
[classdeets1, accuracies1, chance1]= ndim.classifymultiSVM(cvfolds, listofemoavgs, listofemolabels)
crosscorrs=ndim.crossmatrixcorr(alldata)
ndim.plotweightmatrix(savepath,'emo-wise correlations (across halves)', theseemolabels, theseemolabels, crosscorrs, 'emosimilarities_xhalves'+suffix+'.png', figuresize=[7,5],cmin=-1, cmax=1, cmapspec='RdYlBu_r')

# <codecell>

[classdeets1, accuracies1, chance1]= ndim.classifymultiSVM(cvfolds, listofemoavgs, listofemolabels)
accuracies1

# <rawcell>

# classify emo based on dimensions...do things seperately for different subsets of the items. 
# note: do randomized permutations rather than fixed folds based on hitnum...
# put the following inside a permutation loop and set hitnum=indices[i]
# display similarity matrices for different folds (comment out the plotting if doing permutation)

# <codecell>

#indices=range(5)
#shuffle(indices)
cvfolds=range(5)
cvtype='hitnum'
listofemoavgs=[]
listofemolabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=ndim.getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=ndim.getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    #[theseitemavgs, theseitemlabels, theseitememos, theseemoavgs, theseemolabels]=reduce2subset(basicsubset,theseitemavgs, theseitemlabels, theseitememos, theseemoavgs, theseemolabels)
    [theseorderedlabels]=ndim.orderlists(theseemolabels,theseitemlabels,keepers) # reorder in case you lost some emos 
    ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg dimension vectors) in each fold', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=smallfig)
    alldata.append(theseemoavgs)
    listofemolabels.append(theseemolabels)
[classdeets2, accuracies2, chance2]= ndim.classifymultiSVM(cvfolds, listofemoavgs, listofemolabels)
crosscorrs=ndim.crossmatrixcorr(alldata)
ndim.plotweightmatrix(savepath,'emo-wise correlations (across items)', theseemolabels, theseemolabels, crosscorrs, 'emosimilarities_xitems'+suffix+'.png', figuresize=[7,5], cmin=-1, cmax=1, cmapspec='RdYlBu_r')

# <codecell>

[classdeets2, accuracies2, chance2]= ndim.classifymultiSVM(cvfolds, listofemoavgs, listofemolabels)
accuracies=[ac for ac in accuracies1]
accuracies.extend(accuracies2)
print chance2
fig =plt.figure()
ax = fig.add_subplot(1,1,1,)
plt.bar(range(len(accuracies)), accuracies)
plt.plot([0,7],[chance2, chance2],color='r')
ax.set_xticks([i+.4 for i in range(7)])
ax.set_xticklabels(['split-half1','split-half2','item-cv1','item-cv2','item-cv3','item-cv4','item-cv5'])
ax.set_ylim([0,1])

# <rawcell>

# figure out how to show that you are capitalizing on a higher-d space
#     -show that eigenvectors explaining the most variance aren't just valence?
#     -show that you can classify even if excluding valence related dimensions?
#     -show that you take a hit if reducing to massively lower-d space?
#     -show that you can classify above chance when analyzing within positive and negative valence separately?

# <rawcell>

# compare nlp classification based on appraisals to..
#     -single level classification based on bag of words
#     -multilevel algorithm that estimates probabability of appraisals from words, and then emo label from appraisals

# <rawcell>

# individiual differences?
# asd?
# explain errors in terms of appraisal extraction? e.g. when emotions are ambiguous or there is less agreement is it because people differ in their appraisal judgments or in the appraisal/emotion mappings?

# <codecell>


# <codecell>


