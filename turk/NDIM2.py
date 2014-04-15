# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>
##formatted for ipython notebook usage
# <codecell>

#pylab inline

# <codecell>

import sys 
sys.path.append('/Users/amyskerry/Dropbox/antools/utilities')
import aesbasicfunctions as abf
import analyzeNDIM as ndim
import NDIM_analysiswrappers as ndaw
import analyzeNDE as nde_data
from analyzeNDIM import checkthresh as ct
from analyzeNDIM import subjavgcheckthresh as sact
import json
import datetime

#checkthresh=5 #threshold for considering each entry a check passer or not (don't include any entry < this value)
#subjavgcheckthresh=8 #threshold for avgcheckscore for a subject to be included (if a subject on average rated the check below this value, exclude all their responses)


# <codecell>

##set whether you are analyzing pilot study or real, and specify files accordingly (setfiles has hardcoded features)
version='ver2'#or 'pilot' or 'ver2_control' or 'ver2asd'
classifynormeddimvects=1 #0 to use raw dim vects, 1 to use zscores
removeintendedemo=0
exclusioncriteria={'badsubjects':True, 'weirdlines':False, 'passedcheck':True, 'correctemotion':False}
rootdir, nderesultsfile, ndimresultsfile, stimfile, appraisalfile, savepath=ndim.setfiles(version)

# <codecell>

## set values for nde and ndim (setndevals and setndimvals has hardcoded but potentally relevant features)
ndecheckquestions, ndeexpectedanswers, ndeinclusioncols, orderedemos=ndim.setndevals(version)
suffix='basicemoset'#'basicemoset'#'valencearousalset'#'allvars' #to restrict analysis use 'vonly' or 'nv'
eliminateemos=('Disgusted', 'Surprised') #emos to eliminate from the entry set
orderedemos, appraisalnames, appraisaldata, stims, item2emomapping, alldims, defaultdimordering, explicit, othercols,valenceddims, columndict, suffixmappings, excludecols=ndim.setndimvals(version, suffix, appraisalfile, stimfile)

# <codecell>

## run nde analyses and create figs
NDE_accuracy, NDE_confusions=nde_data.main(nderesultsfile, ndecheckquestions,ndeexpectedanswers,ndeinclusioncols,orderedemos,eliminateemos)
#print nderesultsfile
# <codecell>

#specify an intuitive ordering for dimensions (relevant when visualizing)
mydimordering=[] #fill this in with own ordering if desired
if mydimordering:
    newdimordering= ndim.reorderdims(mydimordering, excludecols, othercols, alldims) #will limit to dims in mydimordering
else: 
    newdimordering=defaultdimordering
newdimordering=[dim for dim in newdimordering if dim not in suffixmappings[suffix]]

# <codecell>
##find useable subejcts and define vectors of labels for all items and all emotions
[subjects, entries, dimlabels]=ndim.extractndimdata(ndimresultsfile, excludecols, othercols, columndict, item2emomapping, explicit, version, exclusioncriteria, newdimordering)

# <codecell>
#assess data quality and limit accordingly
badsubjectnames, allcheckscoreavgs =ndim.checkforbadsubjects(subjects, ndim.subjavgcheckthresh)
print str(len(entries)) +" functional entries"
keepers=entries
if exclusioncriteria['passedcheck']:
    keepers=[entry for entry in keepers if entry.passedcheck] #previous exclusions were unusable data collection. this is limiting to those entries that pass the manipulation check (main character)
    print str(len(keepers)) +" passed main character check"
if exclusioncriteria['correctemotion']:
    keepers=[entry for entry in keepers if entry.maxemopass] #limiting to those who rated the predicted emo class as one of their top explictly rated emos
    print str(len(keepers)) +" rated emotions correctly"
if exclusioncriteria['badsubjects']:
    keepers=[entry for entry in keepers if entry.subjid not in badsubjectnames] #limiting to those who pass the subject-level checks specified in checkforbadsubjects (including timing and overall accuracy on manipulation checks: if subjects are guessing randomly on manipulation checks, we want to exlude all their responses, not just the items where they fail)
    print str(len(keepers)) +" retained after removing bad subjects"
#hand remove entries if needed
if version=='ver2_control':
    excludes=('120', '365', '1211', '616', '327', '783','1014','918','1225','1567','943','856','1494','1238','418')
elif version=='ver2':
    excludes=('1448', '1774','882','126','29')
elif version=='ver2asd':
    excludes=()
keepers=[k for k in keepers if k.rownum not in excludes]
if len(excludes)>0:
    print str(len(keepers)) +" retained after removing bad entries by hand"
keeperlabels=[keep.label for keep in keepers]
keeperemos=[keep.emo for keep in keepers]

# <codecell>
#look at individual difference data
subjectresults=[]
#subjectresults=ndim.analyzesubjects([subj for subj in subjects if subj.subjid not in badsubjectnames], version)

# <codecell>
#housekeeping
qlabels=set(keeperlabels)
emolabels=set(keeperemos)
orderedlabels, orderedemos=ndim.orderlists(list(emolabels),list(qlabels),keepers,orderedemos,item2emomapping) #molabels are randomly orded, here use manually sorted labels:
keepers, numstimsperemo=ndim.assignCVfolds(keepers,item2emomapping) #add cv relevant indices to keeper entries

# <codecell>
#check hit counts
hitthresh=5
listdict, blacklist, histogramdict, needmores=ndim.checkitemcounts(orderedlabels, keepers, hitthresh)
#print blacklist
#print listdict

# <codecell>
#compute for each dimension, the average and std over the whole dataset, and update entries with this info
keepers=ndim.computegroupavgs(keepers,newdimordering)

# <codecell>
#compute item, emo, and dim avgs:
itemavgs,normalizeditemavgs,itemlabels,itememos,emoavgs,normalizedemoavgs,dimavgs,emosimilarityspace=ndaw.basicdescriptives(keepers,orderedlabels, orderedemos, dimlabels, suffix, eliminateemos, savepath)

# <codecell>
#can limit to a subset of emos
#subset=[e for e in orderedemos if not e in eliminateemos]
#basicsubsetemos=['Afraid', 'Joyful', 'Disgusted', 'Sad', 'Surprise', 'Angry']
#itemavgs, normalizeditemavgs, itemlabels, itememos, emoavgs, normalizedemoavgs, emolabels=ndim.reduce2subset(subset,itemavgs,normalizeditemavgs, itemlabels, itememos, emoavgs, normalizedemoavgs, list(emolabels))
orderedlabels, orderedemos=ndim.orderlists(list(itememos),list(itemlabels),keepers,orderedemos,item2emomapping) #itememos are randomly orded, here use manually sorted labels:

# <codecell>
#get explicit rating data from ndim subjects
labelxemo, emoxemo, selectiveitems=ndim.explicitemosndim(version, keepers, orderedemos, orderedlabels)

# <codecell>

#do clustering analysis with number of emotions imposed:
#print "****** clustering analysis******"
clusterresults=[]
#clusterresults=ndaw.kmeansclustering(itemavgs, itememos, emolabels)

# <codecell>

#do pca with dimensions as columns, display dimensions with highest loadings on top eigenvectors
#print "****** PCA on dimensions******"
pcaondimsresults=[]
#pcaondimsresults=ndaw.pcaanalysis(itemavgs, 'dimensions', dimlabels, item2emomapping, savepath, 'item-wise correlations (of tranformed item vectors in dimension PC space)', orderedlabels, suffix)

# <codecell>

#do pca with items as columns, display items with highest loadings on top eigenvectors
#print "****** PCA on items******"
#pcaonitemsresults=ndaw.pcaanalysis(itemavgs, 'items', orderedlabels, item2emomapping, savepath, 'item-wise correlations (of tranformed dimension vectors in item PC space)', orderedlabels, suffix)

# <codecell>

#classify emo based on all dimensions, cross validate across split halves, display emo similarity space in each fold
classresults={}
print "****** evenodd classifications******"
cvfolds=range(2) # evenodd takes values 0 and 1
cvtype='evenodd'
classresults[cvtype]=ndaw.classifysummaries(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, usenormed=classifynormeddimvects, matrixtitle='emo-wise correlations (across items)', savetitle='emosimilarities_xhalves', suffix=suffix)
print 'avg accuracy across folds: '+ str(classresults[cvtype]['summaryacc']*100)+'% (chance='+str(classresults[cvtype]['chance'])+')'
# <codecell>

#Classify emo based on dimensions...do things seperately for different subsets of the items.
#note: do randomized permutations rather than fixed folds based on hitnum...put the following inside a permutation loop and set hitnum=indices[i]
#display similarity matrices for different folds (comment out the plotting if doing permutation)
#indices=range(5)
#shuffle(indices)
print "****** stimnum classifications******"
cvfolds=range(1,numstimsperemo+1) #stimnums start at 1
cvtype='stimnum'
classresults[cvtype]=ndaw.classifysummaries(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, usenormed=classifynormeddimvects, matrixtitle='emo-wise correlations (across items)', savetitle='emosimilarities_xhalves', suffix=suffix)
print 'avg accuracy across folds: '+ str(classresults[cvtype]['summaryacc']*100)+'% (chance='+str(classresults[cvtype]['chance'])+')'

# <codecell>
#Classify emo based on dimensions...do things seperately for different subsets of the items.
print "****** single item stimnum classifications******"
cvfolds=range(1,numstimsperemo+1) #stimnums start at 1
cvtype='stimnum'
classresults[cvtype+'_singleitem']=ndaw.classifyindividualitems(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, matrixtitle='emo-wise correlations (across items)', savetitle='emosimilarities_xhalves', suffix=suffix)
print 'avg accuracy across folds: '+ str(classresults[cvtype+'_singleitem']['summaryacc']*100)+'% (chance='+str(classresults[cvtype+'_singleitem']['chance'])+')'

# <codecell>
#regress all explicit emos based on dimensions...do things seperately for different subsets of the items.
print "****** single item stimnum regression******"
cvfolds=range(1,numstimsperemo+1) #stimnums start at 1
cvtype='stimnum'
classresults[cvtype+'_regression']=ndaw.regresstemsummaries(cvfolds, cvtype, keepers, newdimordering, orderedlabels,labelxemo, orderedemos, item2emomapping, savepath, removeintendedemo=removeintendedemo, matrixtitle='emo-wise correlations (across items)', savetitle='emosimilarities_xhalves', suffix=suffix)


# <codecell>

#plot various classification results
ndaw.plotclassresults(classresults)

# <codecell>

#save results of this analysis & make other script that specifically does comparisons across analysis
analysisdeets=ndim.Analysis(version=version, usenormed=classifynormeddimvects, checkthresh=ct, subjavgcheckthresh=sact, exclusioncriteria=exclusioncriteria, suffix=suffix, savepath=item2emomapping, eliminateemos=eliminateemos, item2emomapping=item2emomapping, alldims=alldims, allemos=orderedemos, allitems=orderedlabels)
confusioncorrs=ndim.corr2similarityspaces(NDE_confusions, classresults['stimnum_singleitem']['confusionavg'])
similaritycorrs=ndim.corr2similarityspaces(NDE_confusions, emosimilarityspace)
# should save classresults,NDE_confusions,NDE_accuracy, confussioncorrs, clusterresults, pcaondimsresults, analysisdeets, subjectresults
d=datetime.datetime.now().strftime("%Y-%m-%d")
outputdata={'classresults':classresults,'NDE_confusions':NDE_confusions,'NDE_accuracy':NDE_accuracy, 'confusioncorrs':confusioncorrs, 'similaritycorrs':similaritycorrs,'dimbasedsimilarityspace':emosimilarityspace,'clusterresults':clusterresults, 'pcaondimsresults':pcaondimsresults, 'analysisdeets':analysisdeets, 'subjectresults':subjectresults}
outputdatafile=savepath+'analysis_'+d+'_'+version+'.txt'
abf.pickletheseobjects(outputdatafile, [outputdata])

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


