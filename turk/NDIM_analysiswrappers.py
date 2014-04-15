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

def basicdescriptives(keepers,orderedlabels, orderedemos, dimlabels, suffix, eliminateemos, savepath, figuresize=[10,6], matrixsize=matrixsize):
    [itemavgs,normeditemavgs, itemlabels, itememos]=ndim.getitemavgs(keepers,orderedlabels,eliminateemos)
    [emoavgs, normedemoavgs, emolabels]=ndim.getemoavgs(keepers,orderedemos,eliminateemos)
    dimavgs=np.array(itemavgs).T
    ndim.plotweightmatrix(savepath,'emo-avgs x dimensions', dimlabels, emolabels, emoavgs, 'emosxdims_'+suffix+'.png', figuresize=figuresize,cmin=0, cmax=10)
    ndim.plotcorrmatrix(savepath,'item-wise correlations (of avg item vectors of dim scores)', orderedlabels, itemavgs, 'items_'+suffix+'.png', figuresize=matrixsize)
    ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg emo vectors of dim scores)', orderedemos, emoavgs, 'emos_'+suffix+'.png',figuresize=matrixsize)
    emosimilarityspace=np.corrcoef(emoavgs)    
    ndim.plotcorrmatrix(savepath,'dim-wise correlations (of avg dimension vectors of item avgs)', dimlabels, dimavgs, 'dims_'+suffix+'.png',figuresize=matrixsize)
    return itemavgs,normeditemavgs,itemlabels,itememos,emoavgs,normedemoavgs,dimavgs, emosimilarityspace

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

def classifysummaries(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, useitemsummaries=0, usenormed=0, matrixtitle='emo-wise correlations', classfigsize=matrixsize, corrfiguresize=smallfig, savetitle='emosimilarities', suffix='nosuffixprovided'):
    result={'listofavgs':[], 'listoflabels':[], 'listoffolds':[]}
    for i in cvfolds:
        fold={}
        fold['name']=cvtype+'_'+str(i)
        [fold['itemavgs'],fold['normeditemavgs'], fold['itemlabels'],fold['itememos']]=ndim.getitemavgs(keepers,orderedlabels, **{cvtype:i})
        [fold['emoavgs'],fold['normedemoavgs'], fold['emolabels']]=ndim.getemoavgs(keepers,orderedemos, **{cvtype:i})
        [fold['ordereditems'], fold['orderedemos']]=ndim.orderlists(fold['emolabels'],fold['itemlabels'],keepers,orderedemos,item2emomapping) # reorder in case you lost some emos
        #ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg dimension vectors) in each fold', fold['orderedemos'], fold['emoavgs'], 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=corrfiguresize)
        #since we only have one item per emotion per fold, emoavgs and itemavgs are identical        
        if usenormed==0 and useitemsummaries==0:        
            result['listofavgs'].append(fold['emoavgs'])
            result['listoflabels'].append(fold['emolabels'])
            print "found "+str(len(fold['emoavgs']))
        elif usenormed==1 and useitemsummaries==0:
            result['listofavgs'].append(fold['normedemoavgs'])
            result['listoflabels'].append(fold['emolabels'])
            print "found "+str(len(fold['normedemoavgs']))
        elif usenormed==0 and useitemsummaries==1:        
            result['listofavgs'].append(fold['itemavgs'])
            result['listoflabels'].append(fold['itemlabels'])
            print "found "+str(len(fold['itemavgs']))
        elif usenormed==1 and useitemsummaries==1:
            result['listofavgs'].append(fold['normeditemavgs'])
            result['listoflabels'].append(fold['itemlabels'])
            print "found "+str(len(fold['normeditemavgs']))
        result['listoffolds'].append(fold['name'])
    [result['classdeets'], result['accuracies'], result['chance'], result['confusions']]= ndim.classifymultiSVM(cvfolds, result['listofavgs'], result['listoflabels'], orderedemos)
    result['confusionavg']=np.mean(result['confusions'],0)    
    ndim.plotweightmatrix(savepath,'confusionmatrix_'+cvtype+'emoavgs', orderedemos, orderedemos, result['confusionavg'], suffix, figuresize=matrixsize, cmin=0, cmax=1, cmapspec='hot')
    result['crosscorrs']=ndim.crossmatrixcorr(result['listofavgs'])
    result['summaryacc']=np.mean(result['accuracies'])
    ndim.plotweightmatrix(savepath,matrixtitle, fold['emolabels'], fold['emolabels'], result['crosscorrs'], savetitle+suffix+'.png', figuresize=classfigsize,cmin=-1, cmax=1, cmapspec='RdYlBu_r')
    return result
    
def regresstemsummaries(cvfolds, cvtype, keepers, dimnames, orderedlabels, labelxemo, orderedemos, item2emomapping, savepath, removeintendedemo=0, usenormed=0, matrixtitle='emo-wise correlations', classfigsize=matrixsize, corrfiguresize=smallfig, savetitle='emosimilarities', suffix='nosuffixprovided'):
    result={'listofitemavgs':[], 'listofemoratings':[], 'listoffolds':[]}
    result['allitemlabels']=[]
    for i in cvfolds:
        fold={}
        fold['name']=cvtype+'_'+str(i)
        [fold['itemavgs'],fold['normeditemavgs'], fold['itemlabels'],fold['itememos']]=ndim.getitemavgs(keepers,orderedlabels, item2emos=item2emomapping, orderedemos=orderedemos, **{cvtype:i})
        [fold['emoavgs'],fold['normedemoavgs'], fold['emolabels']]=ndim.getemoavgs(keepers,orderedemos, **{cvtype:i})
        fold['emoratings']=[ratings for ratingsn, ratings in enumerate(labelxemo) if orderedlabels[ratingsn] in fold['itemlabels']]
        [fold['ordereditems'], fold['orderedemos']]=ndim.orderlists(fold['emolabels'],fold['itemlabels'],keepers,orderedemos,item2emomapping) # reorder in case you lost some emos
        #ndim.plotcorrmatrix(savepath,'emo-wise correlations (of avg dimension vectors) in each fold', fold['orderedemos'], fold['emoavgs'], 'emos_'+suffix+cvtype+str(i)+'.png', figuresize=corrfiguresize)     
        if usenormed==0:
            result['listofitemavgs'].append(fold['itemavgs'])
            print "found "+str(len(fold['itemavgs']))
        elif usenormed==1:
            result['listofitemavgs'].append(fold['normeditemavgs']) 
            print "found"+str(len(fold['normeditemavgs']))
        result['listofemoratings'].append(fold['emoratings'])
        result['listoffolds'].append(fold['name'])
        result['allitemlabels'].extend(fold['itemlabels'])
    alloutput=ndim.plsr(cvfolds, result['listofitemavgs'], result['listofemoratings'], fold['orderedemos'], orderedemos, excludeselfemo=removeintendedemo)
    avgcorr=np.mean(alloutput['realpredcorrs'])
    avgR2=np.mean(alloutput['predictionR2s'])
    alloutput['pred_labelxemo'], labelxemocomparisons= ndim.analyzepredictedexplicits(orderedlabels, labelxemo, result['allitemlabels'], alloutput['pred_labelxemo'], fold['emolabels'],'item x explicit emotion predictions')
    coefmatrix=alloutput['dimcoefficients']
    ndim.plotweightmatrix(savepath,'dimweightmatrix_explicitregression', orderedemos,dimnames, coefmatrix, suffix, figuresize=matrixsize, cmin=-1, cmax=1, cmapspec='RdYlBu_r')
    dimweights=np.mean(abs(coefmatrix),1)    
    print "average correlation between real and predicted emo ratings: " + str(avgcorr) 
    print "average R2 in cross-validated predictions: " + str(avgR2) 
    print "comparison of real and predicted emo ratings: "
    print labelxemocomparisons
    results={'alloutput':alloutput, 'dimweights':dimweights, 'avgcorr': avgcorr, 'avgR2':avgR2, 'labelxemocompare':labelxemocomparisons}
    return results

def classifyindividualitems(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, usenormed=0, matrixtitle='emo-wise correlations', classfigsize=matrixsize, corrfiguresize=smallfig, savetitle='emosimilarities', suffix='nosuffixprovided'):
    result={'listofitemavgs':[], 'listofemolabels':[], 'listoffolds':[]}
    for i in cvfolds:
        fold={}
        fold['name']=cvtype+'_'+str(i)
        if usenormed==0:
            fold['itemavgs']=np.array([e.dimvect for e in keepers if getattr(e,cvtype)==i and e.emo in orderedemos])
        elif usenormed==1:
            fold['itemavgs']=np.array([e.normalizeddimvect for e in keepers if getattr(e,cvtype)==i and e.emo in orderedemos])
        print "found "+str(len(fold['itemavgs']))
        fold['emolabels']=np.array([e.emo for e in keepers if getattr(e,cvtype)==i and e.emo in orderedemos])
        result['listofitemavgs'].append(fold['itemavgs'])
        result['listofemolabels'].append(fold['emolabels'])
        result['listoffolds'].append(fold['name'])
    [result['classdeets'], result['accuracies'], result['chance'],result['confusions']]= ndim.classifymultiSVM(cvfolds, result['listofitemavgs'], result['listofemolabels'], orderedemos)
    #result['crosscorrs']=ndim.crossmatrixcorr(result['listofemoavgs'])
    result['confusionavg']=np.mean(result['confusions'],0)    
    ndim.plotweightmatrix(savepath,'confusionmatrix_'+cvtype+'singleitem', orderedemos, orderedemos, result['confusionavg'], suffix, figuresize=matrixsize, cmin=0, cmax=1, cmapspec='hot')
    result['summaryacc']=np.mean(result['accuracies'])
    #ndim.plotweightmatrix(savepath,matrixtitle, fold['emolabels'], fold['emolabels'], result['crosscorrs'], savetitle+suffix+'.png', figuresize=classfigsize,cmin=-1, cmax=1, cmapspec='RdYlBu_r')
    return result
    
def plotclassresults(classresults):
    numclasstests=len(classresults)
    fig, axes=plt.subplots(numclasstests)
    for keyn,key in enumerate(classresults):
        try: 
            result=classresults[key]
            accuracies=[ac for ac in result['accuracies']]
            ax=axes[keyn]
            ax.bar(range(len(accuracies)), accuracies)
            ax.plot([0,len(accuracies)],[result['chance'], result['chance']],color='r')
            ax.set_xticks([i+.4 for i in range(len(accuracies))])
            ax.set_xticklabels([fold for fold in result['listoffolds']])
            ax.set_ylim([0,1])
        except:
            pass