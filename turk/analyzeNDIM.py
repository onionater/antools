# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 14:47:40 2014

@author: amyskerry
"""

class Entry():
    def __init__(self, subjid=[], label=[], emo=[], dimvect=[], check=[], correctemorating=[], maxemo=[], stimnum=[], subjnum=[], evenodd=[]):
        self.subjid=subjid
        self.label=label #stimlabel
        self.emo=emo
        self.dimvect=dimvect
        self.check=int(check)
        self.correctemorating=correctemorating
        self.evenodd=evenodd #split data for each item into two CV halves
        self.stimnum=stimnum #ind num for each stim item in the emo category
        self.subjnum=subjnum #ind num for each subject in the item (1 through num of hits/item)
        self.maxemo=maxemo
        self.maxemopass=maxemo==emo
        self.explicitpass=correctemorating>thresh
        self.passedcheck=self.check>thresh

def extractdata(datafile, excludecols, othercols, columndict, *args):
    '''get the data from an excel file, returns good subject, list of relevant dimensions, and list of stim to emotion category mappings '''
    item2emomapping={}
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        sqlnames=reader.next()
        data=[row for row in reader]  
    incindex, checkindex, explindex,nameindex=[sqlnames.index(thekey) for thekey in columndict.keys()]  
    [labelind, dims, dimind, emoind]=extractvardeets(sqlnames, checkindex, explindex, othercols, excludecols)
    if args:
        newdimorder=args[0]
        dimind=[dimind(dims.index(dim)) for dim in newdimorder if dim in dims]
        dims=newdimorder
    keepers=[subj for subj in data if subj[incindex] != 'NULL']
    for subj in keepers:
        dimvect=[int(subjdata[d]) for d in dimind]
        subj=Entry(subjid=subjdata[nameindex], label=subjdata[labelind[0]], emo=subjdata[emoind[0]], dimvect=dimvect, check=subjdata[checkindex], explicit=subjdata[explindex]) #eac subj saw single emo/quest so we can just rovide the value from the first of these columns
        item2emomapping[subjdata[labelind[0]]]=subjdata[emoind[0]] #okay to do this in each row since it will just rewrite existing ones andthe mapping is the same for all subjects
    return keepers, dims, item2emomapping
    
def extractvardeets(names,checkindex, explindex, othercols, excludecols):
    ''' returns indices for questions columns, emotion columns, dimension columns, as well as list of dimension c'''
    excl=[othercols, excludecols, checkindex,eplindex]
    excludables=[el for el in sublist for sublist in excl]
    labelindices=[sqlnum for sqlnum,sqln in enumerate(names) if 'qlabel' in sqln]
    emoindices=[sqlnum for sqlnum,sqln in enumerate(names) if 'qemo' in sqln]
    dimindices=[sqlnum for sqlnum,sqln in enumerate(names) if not any(substr in sqln for substr in ('qemo', 'qlabel')) and not any([sqln in sublist for sublist in (othercols, excludecols, [checkindex, explindex])])]
    dims=[sqln for sqlnum,sqln in enumerate(names) if not any(substr in ('qemo', 'qlabel')) and not any([sqln in sublist for sublist in (othercols, excludecols, [checkindex, explindex])])]
    return labelindices, dims, dimindices,emoindices
    
def orderlists(emos,qlabels,keepers, orderedemos,item2emomapping):
    '''instead of qlabels, make item labels ordered to align with emos above'''
    orderedemos=[e for e in orderedemos if e in emos]
    labelsets=[]
    for e in orderedemos:
        labelsets.append([item for item in item2emomapping.keys() if item2emomapping[item]==emo])
    orderedlabels=[item for item in itemlist for itemlist in labelsets]
    return orderedlabels,orderedemos
    
def assignCVfolds(keepers, item2emomapping):
    '''give each item within an emotion category'''
    emolabels=set(item2emomapping.values())
    #get labels and emos matched in ordering
    labelsets
    for e in emolabels:
        labelsets.append([item for item in item2emomapping.keys() if item2emomapping[item]==emo])
    qlabels=[item for item in itemlist for itemlist in labelsets]
    #assign within item cv labels
    for qlabel in qlabels:
        entries=[keep for keep in keepers if keep.label==qlabel]
        for entryn,entry in enumerate(entries):
            entry.subjnum=entryn #index up through # of hits per item
            entry.evenodd= entryn % 2 ==1
    #assign item-based cv labels
    for emon, emo in enumerate(emolabels):
        entries=[keep for keep in keepers if keep.emo==emo]
        relevantlabels=labelsets[emon]
        relnums=range(len(relevantlabels))
        for entry in entries:
            entry.stimnum=relnums[rellabels.index(entry.label)]+1
    return keepers
    
def getitemavgs(keepers, labels,emolist, **kwargs):
    ''' prints vector of avg dimension scores (avg across subjects) for each item, as well as vector of item labels and their corresponding emotions'''
    for condition in kwargs:
        keepers=[keep for keep in keepers if getattr(keep,condition)==kwargs[condition]] # continues to eliminate for each kwarg (mainly for selecting cv based on hitnum)
    labelvects=[]
    newlabels=[]
    itememos=[]
    for lan, la in enumerate(labels):
        subset=np.array([keep.dimvect for keep in keepers if keep.label==la]) #datavectors for the dimension
        keeps=[keep for keep in keepers if keep.label==la] #full entries for the dimension
        emo=orderedemos[lan] 
        try:
            dimavg=np.mean(subset,0)
        except:
            print "warning: there were some nans in your dimension vectors for stim " + la +' (emo='+emo+')
            dimavg=np.nanmean(subset,0)
        if not any(np.isnan(val for val in dimavg):
            labelvects.append(dimavg)
            newlabels.append(la)
            itememos.append(emo)
        else:
            print "warning: some dimensions had nan avgs"
    return labelvects, newlabels, itememos

def getemoavgs(keepers, emolabels, dims, **kwargs):
    for condition in kwargs:
        keepers=[keep for keep in keepers if getattr(keep,condition)==kwargs[condition]]
    emovects=[]
    newlabels=[]
    for la in emolabels:
        subset=np.array([keep.dimvect for keep in keepers if keep.emo==la])
        dimavg=np.mean(subset,0)
        if not any(np.isnan(val for val in dimavg):
            emovects.append(dimavg)
            newlabels.append(la)
    return emovects, newlabels, dims  
def plotcorrmatrix(savepath, title, axis, datamatrix, suffix,figuresize=[8,8],cmin=-1,cmax=1, cmapspec='RdYlBu_r'):
    '''plots correlation matrix for each row in the datamatrix (symmetrical, diagonal of 1)'''    
    fig=plt.figure(figsize=figuresize)   
    ax=plt.subplot()
    im=plt.pcolor(np.corrcoef(datamatrix), vmin=cmin, vmax=cmax, cmap=cmapspec) #symmetrical by necessity
    plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(axis))),axis, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(axis))),axis)
    ax.set_xlabel(title)
    fig.savefig(savepath+suffix)
def crossmatrixcorr(data):
    '''computes correlations for each row across 2 matrices''' 
    versions=range(len(data))
    combos=[combo for combo in itertools.combinations(versions,2)]
    corrmatrices=[]
    for c in combos:
        dataA,dataB=data[c[0,2]]
        corrmatrix=[np.array([np.corrcoef(rowA,rowB)[0,1] for rowB in dataB]) for rowA in dataA]
        corrmatrices.append(corrmatrix)
    corrmeans=np.mean(np.array(corrmatrices),0)
    return corrmeans
def plotweightmatrix(savepath,title, xaxis, yaxis, datamatrix, suffix,figuresize=[8,8],cmin=[],cmax=[], cmapspec='hot'):
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
    fig.savefig(savepath+suffix)

###math sections
def classifymultiSVM(cvfolds, dataavgs, datalabels):
    '''takes list of cv fold #s, list of dimvects for each fold and list list of labels for eachfold, returns classification results: details of the model, list of accuracies in each fold, chance'''
    accuracies=[]
    classdeets=[]
    for i in cvfolds:
        testlabels=np.array([label for label in [fold for foldnum, fold in enumerate(datalabels) if foldnum==i]]).flatten() #get relevant test indices
        trainlabels=np.array([label for label in [fold for foldnum, fold in enumerate(datalabels) if foldnum !=i]]).flatten() #get relevant train indices
        testdata=[d for d in [fold for foldnum,fold in enumerate(dataavgs) if foldnum==i]]
        traindata=np.array([d for d in [fold for foldnum,fold in enumerate(alldata) if foldnum !=i]])
        chance=1.0/len(set(trainlabels))
        testset=[]
        trainset=[]
        for test in testdata:
            testset.extend(test) #confused about this
        for train in traindata:
            trainset.extend(train) #confused aboutthis
        #actual classification
        clf = svm.SVC(gamma=0.001, C=100.) #define model
        clf.fit(trainset, trainlabels) #train model
        predictions=clf.predict(testset) #predict
        corrects=[float(prediction==testlabels[pn]) for pn, prediction in enumerate(predictions)] #assess predictions
        if any(np.isnan(x) for x in corrects):
            print "oops, there were non numerical correctness values..." #shouldn't happen
        accuracy=np.sum(corrects)/len(corrects) #compute accuracy
        accuracies.append(accuracy)
        classdeets.append(clf)
    return classdeets, accuracies, chance
def plotscree(pcs_var, title,figuresize=bigfig):
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
    
#stolen or slightly modified functions    
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

def myPCA(thresh, data,title,columnlabels, figuresize=medfig):
    ''' performs pca '''
    pca = decomposition.PCA()
    [eigenvectors,score,latent]=princomp(data) #this is mostly redundant but scikit-learn's decomposition.PCA, but that doesn't provide easy access to the eigenvectors? eigenvectors canbe used to find top and bottom 3 dimensions for each PC, for example
    #latent maps onto pcs_var, and score maps onto dims_reduced (though unreduced), though these are not identical.... unclear why?
    score=score.T #get back to dimensions of data
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
    '''writes out some details about the PCA''' 
    thresh=0
    num=0
    string='eigenvector #'
    passedvals=[]
    passednames=[]
    #find the eigenvectors that pass the threshold/are in top number 
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
    
def reorderdims(newdimordering, excludecols, alldims)
    '''take user specified ordering and remove excludedcols. also check against what is derived from appraisals.csv '''
    newdimordering=[el for el in newdimordering if el not in excludecols]
    if len(newdimordering) not = len(alldims):
        print "warning, your specified newdimensions don't match what is in appraisals.csv'
    mismatches=[dim for dim in newdimordering if dim not in alldims]
    if mismatches:
        print "warning, your ordered dims don't match your appraisal.csv file"

def uniquifyordered(list):
    '''take a list and return it's unique elements, maintaining their order'''
    mynewset=sorted(set(mylist), key=mylist.index)
    return list(mynewset)
    return newdimordering

def reduce2subset(subset,itavgs, ilabels, iemos, emavgs, elabels):
    reduceditavgs=[item for itemn,item in enumerate(itavgs) if iemos[itemn] in subset]
    reducedilabels=[item for itemn,item in enumerate(ilabels) if iemos[itemn] in subset]
    reducediemos=[item for item in iemos if item in subset]
    reducedemavgs=[item for itemn,item in enumerate(emavgs) if elabels[itemn] in subset]
    reducedelabels=[item for item in elabels if item in subset]
    return reduceditavgs,reducedilabels,reducediemos, reducedemavgs, reducedelabels
