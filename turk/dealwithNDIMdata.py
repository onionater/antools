# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 13:13:29 2013

@author: amyskerry
"""
import csv
import aeslazy as asl
import numpy as np
from itertools import *
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.io
from sklearn import svm, cluster, decomposition

global othercols, excludecols
filename='/Users/amyskerry/NDE_dimdl.csv'
#important columns
subdate='submission_date'
check='main_character'
explicit='emotion'
subjid='subjid'
othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts']

suffix='allvars'
excludecols=[]

#suffix='nv'
#excludecols=['pleasantness', 'goal_consistency', 'safety']

#suffix='allvars'
#excludecols=['expectedness','fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'self_involvement']

# for reference: dims included='expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'fixing', 'moral', 'confidence', 'suddenness', 'familiarity', 'past_present', 'certainty', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'safety', 'self_involvement'

class subject():
    def __init__(self, subjid=[], label=[], emo=[], dimvect=[], check=[], explicit=[], hitnum=[], subjnum=[], half=[]):
        self.subjid=subjid
        self.label=label
        self.emo=emo
        self.dimvect=dimvect
        self.check=int(check)
        self.explicit=explicit
        self.half=half #split data for each item into two CV halves
        self.hitnum=hitnum #ind num for each item in the emo (1-5)
        self.subjnum=subjnum #ind num for each subject in the item (1 through num of hits/item)
    def passedcheck(self):
        if self.check<7 and self.explicit!=self.emo:
            passed=False
        else:
            passed=True
        return passed


def extractdata(datafile):
    count=0
    data=[]
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                sqlnames=row
                incindex=sqlnames.index(subdate)
                checkindex=sqlnames.index(check)
                explindex=sqlnames.index(explicit)
                nameindex=sqlnames.index(subjid)
                [labelind, dims, dimind, emoind]=extractvardeets(sqlnames, checkindex, explindex)
            else:
                subjdata=row
                if subjdata[incindex] != 'NULL' and subjdata[emoind[0]] != 'CHECK':
                    dimvect=[]
                    for x in dimind:
                        dimvect.append(int(subjdata[x]))
                    subj=subject(subjid=subjdata[nameindex], label=subjdata[labelind[0]], emo=subjdata[emoind[0]], dimvect=dimvect, check=subjdata[checkindex], explicit=subjdata[explindex]) #eac subj saw single emo/quest so we can just rovide the value from the first of these columns
                    data.append(subj)
    return data, dims
                    
def extractvardeets(names,checkindex, explindex):
    labels=[]
    labelindices=[]
    dims=[]
    dimindices=[]
    emos=[]
    emoindices=[]
    for sqlnum,sqln in enumerate(names):
        if 'qlabel' in sqln:
            labelindices.append(sqlnum)
        elif 'qemo' in sqln:
            emoindices.append(sqlnum)
        elif sqlnum==checkindex or sqlnum==explindex:
            pass
        elif sqln not in othercols and sqln not in excludecols:
            dimindices.append(sqlnum)
            dims.append(sqln)
    return labelindices, dims, dimindices,emoindices
            
def getitemavgs(keepers, labels,dims,**kwargs):
    for condition in kwargs:
        keepers=[keep for keep in keepers if getattr(keep,condition)==kwargs[condition]]
    labelvects=[]
    newlabels=[]
    itememos=[]
    for la in labels:
        subset=np.array([keep.dimvect for keep in keepers if keep.label==la])
        keeps=[keep for keep in keepers if keep.label==la]
        try:
            emo=keeps[0].emo
        except:
            pass
        dimavg=np.mean(subset,0)
        if not isnan(np.sum(dimavg)):
            labelvects.append(dimavg)
            newlabels.append(la)
            itememos.append(emo)
    return labelvects, newlabels, dims, itememos
def getemoavgs(keepers, emolabels, dims, **kwargs):
    for condition in kwargs:
        keepers=[keep for keep in keepers if getattr(keep,condition)==kwargs[condition]]
    emovects=[]
    newlabels=[]
    for la in emolabels:
        subset=np.array([keep.dimvect for keep in keepers if keep.emo==la])
        dimavg=np.mean(subset,0)
        if not isnan(np.sum(dimavg)):
            emovects.append(dimavg)
            newlabels.append(la)
    return emovects, newlabels, dims   
def plotcorrmatrix(title, axis, datamatrix, suffix):
    fig=plt.figure(figsize=[10,10])   
    ax=plt.subplot()
    pcolor(corrcoef(datamatrix), cmap='hot') #symmetrical by necessity
    plt.xticks(map(lambda x:x+.5, range(len(axis))),axis, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(axis))),axis)
    ax.set_xlabel(title)
    fig.savefig('/Users/amyskerry/Dropbox/antools/turk/NDE_dim/'+suffix)
def assignCVfolds(keepers, qlabels, emolabels):
    for qlabel in qlabels:
        c=0
        half=0
        these=[keep for keep in keepers if keep.label==qlabel]
        for t in these:
            c+=1
            t.subjnum=c
            t.half=np.abs(half)+1
            half=np.abs(half)-1
    for emo in emolabels:
        these=[keep for keep in keepers if keep.emo==emo]
        rellabels=set([keep.label for keep in keepers if keep.emo==emo])
        rellabels=list(rellabels)
        relnums=range(len(rellabels))
        for t in these:
            t.hitnum=relnums[rellabels.index(t.label)]+1
    return keepers
def orderlists(emos,qlabels):
    orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise', 'Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed'] #same as NDE but without surprise
    #instead of qlabels, make item labels ordered to align with emos above
    orderedemos=[e for e in orderedemos if e in emos]
    qlabelsets=[]
    for emo in orderedemos:
        qlabelsets.append([keep.label for keep in keepers if keep.emo==emo])
    alllabels=[item for sublist in qlabelsets for item in sublist]
    orderedlabels=sorted(set(alllabels), key=alllabels.index) #trick for keeping set sorted
    orderedlabels=[o for o in orderedlabels if o in qlabels]    
    return orderedlabels, orderedemos
    
def classify(cvfolds, alldata, alllabels):
    accuracies=[]
    classdeets=[]
    for i in cvfolds:
        testlabels=np.array([label for label in [fold for foldnum, fold in enumerate(alllabels) if foldnum==i]]).flatten()
        trainlabels=np.array([label for label in [fold for foldnum, fold in enumerate(alllabels) if foldnum !=i]]).flatten()
        testdata=[d for d in [fold for foldnum,fold in enumerate(alldata) if foldnum==i]]
        traindata=np.array([d for d in [fold for foldnum,fold in enumerate(alldata) if foldnum !=i]])
        possanswers=set(trainlabels)
        chance=1.0/len(possanswers)
        testset=[]
        trainset=[]
        for test in testdata:
            testset.extend(test)
        for train in traindata:
            trainset.extend(train)
        clf = svm.SVC(gamma=0.001, C=100.)
        clf.fit(trainset, trainlabels)
        predictions=clf.predict(testset)
        corrects=[float(prediction==testlabels[pn]) for pn, prediction in enumerate(predictions)]
        accuracy=np.sum(corrects)/len(corrects)
        accuracies.append(accuracy)
        classdeets.append(clf)
    return classdeets, accuracies, chance
def plotscree(pcs_var):
    fig = plt.figure(figsize=(8,5))
    x = np.arange(len(pcs_var)) + 1
    plt.plot(x, pcs_var, 'ro-', linewidth=2)
    plt.title('eigenvalues')
    plt.xlabel('principle components')
    plt.ylabel('variance explained')
    #I don't like the default legend so I typically make mine like below, e.g.
    #with smaller fonts and a bit transparent so I do not cover up data, and make
    #it moveable by the viewer in case upper-right is a bad place for it 
    leg = plt.legend(['variance explained'], loc='best', borderpad=0.3, 
                     shadow=False, prop=matplotlib.font_manager.FontProperties(size='small'),
                     markerscale=0.4)
    leg.get_frame().set_alpha(0.4)
    leg.draggable(state=True)
    plt.show()
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from pylab import plot,subplot,axis,stem,show,figure

def princomp(A):
     """ performs principal components analysis 
         (PCA) on the n-by-p data matrix A
         Rows of A correspond to observations, columns to variables. 
    
     Returns :  
      coeff :
        is a p-by-p matrix, each column containing coefficients 
        for one principal component. (each column is an eigenvector)
      score : 
        the principal component scores; that is, the representation 
        of A in the principal component space. Rows of SCORE 
        correspond to observations, columns to components.
      latent : 
        a vector containing the eigenvalues 
        of the covariance matrix of A.
     """
     # computing eigenvalues and eigenvectors of covariance matrix
     M = (A-np.mean(A.T,axis=1)).T # subtract the mean (along columns)
     [latent,coeff] = np.linalg.eig(np.cov(M)) # attention:not always sorted
     score = np.dot(coeff.T,M) # projection of the data in the new space
     return coeff,score,latent

def myPCA(thresh, data):
    pca = decomposition.PCA()
    [eigenvectors,score,latent]=princomp(data) #this is mostly redundant but scikit-learn doesn't provide easy access to the eigenvectors? eigenvectors canbe used to find top and bottom 3 dimensions for each PC, for example
    pca.fit(data)
    pcs_var=pca.explained_variance_ratio_ #eigenvalues= explained_variance_ . here we instead of explained_variance_ratio, as using ratio of eigenvalue/all eigenvalues gives percentage of variance n data explained by that component
    plotscree(pcs_var)
    comps=[int(pc>thresh) for pc in pcs_var]
    pca.n_components=np.sum(comps)
    print pca.n_components
    dims_reduced = pca.fit_transform(data) # each item in terms of the new dimensions (to limit number of dimensions, update n_components after inspecting screen plot). dims_reduced is the equal to original dataset * the eigenvectors (linear transform of data into PC space, where variables are uncorrelatted)
    return eigenvectors, pcs_var, dims_reduced
        
# find useable subejcts and define vectors of class labels
[subjects, dims]=extractdata(filename)
keepers=[subj for subj in subjects if subj.passedcheck()]
qlabels=set([keep.label for keep in keepers])
emolabels=set(keep.emo for keep in keepers)
keepers=assignCVfolds(keepers,qlabels,emolabels)
#actualy emolabels are randomly orded, here use manually sorted labels
[orderedlabels, orderedemos]=orderlists(emolabels,qlabels)

#compute item and emo avgs
[itemavgs,itemlabels, dimlabels, itememos]=getitemavgs(keepers,orderedlabels, dims)
[emoavgs, emolabels, dimlabels]=getemoavgs(keepers,orderedemos, dims)
plotcorrmatrix('item-wise correlations (of avg dimension vectors)', orderedlabels, itemavgs, 'items_'+suffix+'.png')
plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', orderedemos, emoavgs, 'emos_'+suffix+'.png')

#do clustering analysis with number of emotions imposed:
k_means = cluster.KMeans(n_clusters=len(emolabels))
k_means.fit(itemavgs)
kclusters=k_means.labels_
kclusters, itememos = zip(*sorted(zip(kclusters, itememos))) # nifty trick for zipping together, sorting, and unzipping
for cn, c in enumerate(kclusters):
    print str(c+1) +': '+itememos[cn]
    

thresh=.02 #1% variance explained
#do pca with dimensions as columns
[dim_eigenvectors, dim_eigenvalues, dim_transformed]=myPCA(thresh, np.array(itemavgs))
plotcorrmatrix('item-wise correlations (of tranformed vectors in PC space)', orderedlabels, dim_transformed, 'RD_items_'+suffix+'.png')
#do pca with items as columns
[item_eigenvectors, item_eigenvalues, item_transformed]=myPCA(thresh, np.array(itemavgs).T)



#do things seperately for different subsets of the items
## note to do randomized permutations rather than fixed folds based on hitnum, put the following inside a permutation loop and set hitnum=indice[i]
#indices=range(5)
#shuffle(indices)
cvfolds=range(5)
cvtype='hitnum'
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=orderlists(theseemolabels,theseitemlabels) # reorder in case you lost some emos
    #plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png')
#    
## classify, cross validate across split halves    
cvfolds=range(2)
cvtype='half'
alldata=[]
alllabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=orderlists(theseemolabels,theseitemlabels) # reorder in case you lost some emos
    ##plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png')
    alldata.append(theseemoavgs)
    alllabels.append(theseemolabels)
[classdeets1, accuracies1, chance1]= classify(cvfolds, alldata, alllabels)
#    
## classify cross validate across items
cvfolds=range(5)
cvtype='hitnum'
alldata=[]
alllabels=[]
for i in cvfolds:
    [theseitemavgs,theseitemlabels, thesedimlabels, theseitememos]=getitemavgs(keepers,orderedlabels, dims, **{cvtype:i+1})
    [theseemoavgs, theseemolabels, thesedimlabels]=getemoavgs(keepers,orderedemos, dims, **{cvtype:i+1})
    [theseorderedlabels, theseorderedemos]=orderlists(theseemolabels,theseitemlabels) # reorder in case you lost some emos 
    ##plotcorrmatrix('emo-wise correlations (of avg dimension vectors)', theseorderedemos, theseemoavgs, 'emos_'+suffix+cvtype+str(i)+'.png')
    alldata.append(theseemoavgs)
    alllabels.append(theseemolabels)
[classdeets2, accuracies2, chance2]= classify(cvfolds, alldata, alllabels)