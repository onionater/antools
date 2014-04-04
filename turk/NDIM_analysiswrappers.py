# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 11:14:03 2014

@author: amyskerry

"""
import matplotlib.pyplot as plt
import aesbasicfunctions as abf
import analyzeNDIM as ndim
from sklearn import svm, cluster, decomposition
import numpy as np

#dumb parameters
bigfig=[8,10]
medfig=[6,4]
smallfig=[3,2]
screesize=[4,3]
matrixsize=[7,6]
largefig=[12,8]

def basicdescriptives(keepers,orderedlabels, orderedemos, dimlabels, suffix, savepath, figuresize=[10,6], matrixsize=matrixsize):
    [itemavgs,itemlabels, itememos]=ndim.getitemavgs(keepers,orderedlabels)
    [emoavgs, emolabels]=ndim.getemoavgs(keepers,orderedemos)
    dimavgs=np.array(itemavgs).T
    ndim.plotweightmatrix(savepath,'emo-avgs x dimensions', dimlabels, emolabels, emoavgs, 'emosxdims_'+suffix+'.png', figuresize=figuresize,cmin=0, cmax=10)
    ndim.plotcorrmatrix(savepath,'item-wise correlations (of avg item vectors of dim scores)', orderedlabels, itemavgs, 'items_'+suffix+'.png', figuresize=matrixsize)
    ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg emo vectors of dim scores)', orderedemos, emoavgs, 'emos_'+suffix+'.png',figuresize=matrixsize)
    ndim.plotcorrmatrix(savepath,'dim-wise correlations (of avg dimension vectors of item avgs)', dimlabels, dimavgs, 'dims_'+suffix+'.png',figuresize=matrixsize)
    return itemavgs,itemlabels,itememos,emoavgs,dimavgs

def pcaanalysis(rows, columnstype, labels, item2emomapping, savepath, savetitle, orderedlabels, suffix, figuresize=matrixsize, screesize=screesize, thresh=.02):
    #thresh is variance explained
    if columnstype=='dimensions':
        noncolumntype='items'
    else: 
        noncolumntype='dimensions'
    title='PC on '+columnstype
    [eigenvectors, eigenvalues, transformed, evlabels, evvalues]=ndim.myPCA(thresh, np.array(rows), title, labels, figuresize=screesize)
    [passedvals, passnames]=ndim.eigentable(item2emomapping,evlabels,evvalues,num=3)
    ## plot in PC space (based on suggested n components)
    ndim.plotcorrmatrix(savepath,savetitle, orderedlabels, transformed, 'RD_'+noncolumntype+'_'+suffix+'.png',figuresize=matrixsize)
    pcaresults= {'columns':columnstype, 'eigenvectors':eigenvectors,'eigenvalues':eigenvalues,'transformed':transformed, 'evlabels': evlabels, 'evvalues': evvalues, 'passedvals':passedvals, 'passnames':passnames}
    return pcaresults
    
def kmeansclustering(itemavgs, itememos, emolabels, **kwargs):
    if 'numclusters' in kwargs:
        numclust=kwargs['numclusters']
    else:
        numclust=len(emolabels)
    k_means = cluster.KMeans(n_clusters=numclust)
    k_means.fit(itemavgs)
    kclusters=k_means.labels_
    kclusters, itememos = zip(*sorted(zip(kclusters, itememos))) # zipping together, sorting, and unzipping
    for cn, c in enumerate(kclusters):
        print str(c+1) +': '+itememos[cn]
    return {'k_means':k_means, 'kclusters':kclusters, 'itememos':itememos, 'numclusters':numclust}

def classifyitemsummaries(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, matrixtitle='emo-wise correlations', classfigsize=matrixsize, corrfiguresize=smallfig, savetitle='emosimilarities', suffix='nosuffixprovided'):
    result={'listofemoavgs':[], 'listofemolabels':[], 'listoffolds':[]}
    for i in cvfolds:
        fold={}
        fold['name']=cvtype+'_'+str(i)
        [fold['itemavgs'], fold['itemlabels'],fold['itememos']]=ndim.getitemavgs(keepers,orderedlabels, **{cvtype:i})
        [fold['emoavgs'], fold['emolabels']]=ndim.getemoavgs(keepers,orderedemos, **{cvtype:i})
        #[fold['itemavgs'], fold['itemlabels'], fold['itememos'], fold['emoavgs'], fold['emolabels']]=reduce2subset(basicsubset,fold['itemavgs'], fold['itemlabels'], fold['itememos'], fold['emoavgs'], fold['emolabels'])
        [fold['ordereditems'], fold['orderedemos']]=ndim.orderlists(fold['emolabels'],fold['itemlabels'],keepers,orderedemos,item2emomapping) # reorder in case you lost some emos
        ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg dimension vectors) in each fold', fold['orderedemos'], fold['emoavgs'], 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=corrfiguresize)
        result['listofemoavgs'].append(fold['emoavgs'])
        result['listofemolabels'].append(fold['emolabels'])
        result['listoffolds'].append(fold['name'])
    [result['classdeets'], result['accuracies'], result['chance']]= ndim.classifymultiSVM(cvfolds, result['listofemoavgs'], result['listofemolabels'])
    result['crosscorrs']=ndim.crossmatrixcorr(result['listofemoavgs'])
    result['summaryacc']=np.mean(result['accuracies'])
    ndim.plotweightmatrix(savepath,matrixtitle, fold['emolabels'], fold['emolabels'], result['crosscorrs'], savetitle+suffix+'.png', figuresize=classfigsize,cmin=-1, cmax=1, cmapspec='RdYlBu_r')
    return result
    
def plotclassresults(classresults):
    numclasstests=len(classresults)
    fig, axes=plt.subplots(numclasstests)
    for keyn,key in enumerate(classresults):
        result=classresults[key]
        accuracies=[ac for ac in result['accuracies']]
        ax=axes[keyn]
        ax.bar(range(len(accuracies)), accuracies)
        ax.plot([0,len(accuracies)],[result['chance'], result['chance']],color='r')
        ax.set_xticks([i+.4 for i in range(len(accuracies))])
        ax.set_xticklabels([fold for fold in result['listoffolds']])
        ax.set_ylim([0,1])