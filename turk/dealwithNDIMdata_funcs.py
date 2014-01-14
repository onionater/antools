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
import matplotlib.font_manager as fmnger
import seaborn as sns
import scipy.io
from sklearn import svm, cluster, decomposition
import itertools

global subdate, check, explicit, subjid
subdate='submission_date'
check='main_character'
explicit='emotion'
subjid='subjid'


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


def extractdata(datafile, excludecols, othercols, *args):
    count=0
    data=[]
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        mapdict={}
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                sqlnames=row
                incindex=sqlnames.index(subdate)
                checkindex=sqlnames.index(check)
                explindex=sqlnames.index(explicit)
                nameindex=sqlnames.index(subjid)
                [labelind, dims, dimind, emoind]=extractvardeets(sqlnames, checkindex, explindex, othercols, excludecols)
                if args:
                    newdimorder=args[0]
                    newdimind=[]
                    for dim in newdimorder:
                        try:
                            dimindex=dims.index(dim)
                            newdimind.append(dimind[dimindex])
                        except:
                            print "dimension included in dimordering but not in data"
                    dimind=newdimind
                    dims=newdimorder
            else:
                subjdata=row
                if subjdata[incindex] != 'NULL' and subjdata[emoind[0]] != 'CHECK':
                    dimvect=[]
                    for x in dimind:
                        dimvect.append(int(subjdata[x]))
                    subj=subject(subjid=subjdata[nameindex], label=subjdata[labelind[0]], emo=subjdata[emoind[0]], dimvect=dimvect, check=subjdata[checkindex], explicit=subjdata[explindex]) #eac subj saw single emo/quest so we can just rovide the value from the first of these columns
                    mapdict[subjdata[labelind[0]]]=subjdata[emoind[0]] #okay to do this in each row since it will just rewrite existing ones andthe mapping is the same for all subjects
                    data.append(subj)
    return data, dims, mapdict
                    
def extractvardeets(names,checkindex, explindex, othercols, excludecols):
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
        if not np.isnan(np.sum(dimavg)):
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
        if not np.isnan(np.sum(dimavg)):
            emovects.append(dimavg)
            newlabels.append(la)
    return emovects, newlabels, dims   
def plotcorrmatrix(title, axis, datamatrix, suffix,figuresize=[8,8],cmin=-1,cmax=1, cmapspec='RdYlBu'):
    fig=plt.figure(figsize=figuresize)   
    ax=plt.subplot()
    im=plt.pcolor(np.corrcoef(datamatrix), vmin=cmin, vmax=cmax, cmap=cmapspec) #symmetrical by necessity
    plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(axis))),axis, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(axis))),axis)
    ax.set_xlabel(title)
    fig.savefig('/Users/amyskerry/Dropbox/antools/turk/NDE_dim/'+suffix)
def crossmatrixcorr(data):
    versions=range(len(data))
    combos=[]
    for combo in itertools.combinations(versions,2):
        combos.append(combo)
    corrmatrices=[]
    for c in combos:
        dataA=data[c[0]]
        dataB=data[c[1]]
        corrmatrix=[]
        for rowA in dataA:
            corrmatrix.append(np.array([np.corrcoef(rowA,rowB)[0,1] for rowB in dataB]))
        corrmatrices.append(corrmatrix)
    corrmeans=np.mean(np.array(corrmatrices),0)
    return corrmeans
def plotweightmatrix(title, xaxis, yaxis, datamatrix, suffix,figuresize=[8,8],cmin=[],cmax=[], cmapspec='hot'):
    fig=plt.figure(figsize=figuresize)   
    ax=plt.subplot()
    if type(cmin)!=list and type(cmax)!=list:
        im=plt.pcolor(np.array(datamatrix),vmin=cmin,vmax=cmax,cmap=cmapspec)
        plt.colorbar(im)
    else:    
        im=plt.pcolor(np.array(datamatrix), cmap=cmapspec) #symmetrical by necessity
        plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(xaxis))),xaxis, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(yaxis))),yaxis)
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
def orderlists(emos,qlabels,keepers):
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
def plotscree(pcs_var, title,figuresize=[10,8]):
    fig = plt.figure(figsize=figuresize)
    x = np.arange(len(pcs_var)) + 1
    plt.plot(x, pcs_var, 'ro-', linewidth=2)
    plt.title(title + ' (eigenvalues)')
    plt.xlabel('principle components')
    plt.ylabel('variance explained')
    #I don't like the default legend so I typically make mine like below, e.g.
    #with smaller fonts and a bit transparent so I do not cover up data, and make
    #it moveable by the viewer in case upper-right is a bad place for it 
    leg = plt.legend(['variance explained'], loc='best', borderpad=0.3, 
                     shadow=False, prop=fmnger.FontProperties(size='small'),
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

def myPCA(thresh, data,title,columnlabels, figuresize=[6,4]):
    pca = decomposition.PCA()
    [eigenvectors,score,latent]=princomp(data) #this is mostly redundant but scikit-learn doesn't provide easy access to the eigenvectors? eigenvectors canbe used to find top and bottom 3 dimensions for each PC, for example
    #latent maps onto pcs_var, and score maps onto dims_reduced (though unreduced), though these are not identical.... unclear why?
    score=score.T #get back to dimensions of data
    print np.shape(latent)
    latent=[round(np.real(l),4) for l in latent]
    pca.fit(data)
    pcs_var=pca.explained_variance_ratio_ #eigenvalues= explained_variance_ . here we instead use explained_variance_ratio, as using ratio of eigenvalue/all eigenvalues gives percentage of variance n data explained by that component
    maxpcs=len(pcs_var)
    latent=latent[0:maxpcs] #since you can't have more variance explaining PCs than you do observations/rows. see http://stats.stackexchange.com/questions/28909/pca-when-the-dimensionality-is-greater-than-the-number-of-samples
    plotscree(pcs_var,title, figuresize=figuresize)
    comps=[int(pc>thresh) for pc in pcs_var]
    pca.n_components=np.sum(comps)
    dims_reduced = pca.fit_transform(data) # each item in terms of the new dimensions (to limit number of dimensions, update n_components after inspecting screen plot). dims_reduced is the equal to original dataset * the eigenvectors (linear transform of data into PC space, where variables are uncorrelatted)
    #sort eigenvectors based on their eigenvalues
    rankedeigenvalues=sorted(range(len(latent)), key=lambda i:latent[i])
    rankedindices=rankedeigenvalues[-pca.n_components:]
    rankedindices.reverse()
    useableeigenvectors=np.array(eigenvectors.T)
    useableeigenvectors=useableeigenvectors[rankedindices]
    evvalues=[]
    evlabels=[]
    for ev in useableeigenvectors:
        ev=[np.real(x) for x in ev]
        # sort variables based on their loading on the eigenvectors
        evindices=sorted(range(len(ev)), key=lambda i:ev[i])
        evvalues.append(np.array(ev)[evindices])
        evlabels.append(np.array(columnlabels)[evindices])
    return eigenvectors, pcs_var, dims_reduced, evlabels, evvalues
def eigentable(emolabelmapping,evlabels,evvalues,**kwargs):
    thresh=0
    num=0
    string='eigenvector #'
    passedvals=[]
    passednames=[]
    if 'thresh' in kwargs:
        thresh=kwargs['thresh']
        for evectorn, evector in enumerate(evvalues):
            evlabelvector=evlabels[evectorn]
            passedvals.append([ev for ev in evector if ev>thresh])
            passednames.append([evlabelvector[evn] for evn, ev in enumerate(evvector) if ev>thresh])
    if 'num' in kwargs:
        num=kwargs['num']
        for evectorn, evector in enumerate(evvalues):
            evlabelvector=evlabels[evectorn]
            passedvals.append(evector[-num:])
            passednames.append(evlabelvector[-num:])
    for namen, name in enumerate(passednames):
        try:
            names=list(name)
            emos=[emolabelmapping[ql] for ql in names]
            printstring=string+str(namen+1)+'--- high-loaders: ' +', '.join(name) +'; emos: ' +', '.join(emos)+'; loadings: '+', '.join([str(round(x,3)) for x in passedvals[namen]])
        except:
            printstring=string+str(namen+1)+'--- high-loaders: ' +', '.join(name) +'; loadings: '+', '.join([str(round(x,3)) for x in passedvals[namen]])
        print printstring
    return passedvals, passednames
        
    
        