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

# <codecell>

##set whether you are analyzing pilot study or real, and specify files accordingly (setfiles has hardcoded features)
version='ver2'#or 'pilot'
rootdir, nderesultsfile, ndimresultsfile, stimfile, appraisalfile, savepath=ndim.setfiles(version)

# <codecell>

## set values for nde and ndim (setndevals and setndimvals has hardcoded but potentally relevant features)
ndecheckquestions, ndeexpectedanswers, ndeinclusioncols, orderedemos=ndim.setndevals(version)
suffix='allvars' #to restrict analysis use 'vonly' or 'nv'
orderedemos, appraisalnames, appraisaldata, stims, item2emomapping, alldims, defaultdimordering, explicit, othercols,valenceddims, columndict, suffixmappings, excludecols=ndim.setndimvals(version, suffix, appraisalfile, stimfile)

# <codecell>

## run nde analyses and create figs
nde_data.main(nderesultsfile, ndecheckquestions,ndeexpectedanswers,ndeinclusioncols,orderedemos)
print nderesultsfile

# <codecell>

#specify an intuitive ordering for dimensions (relevant when visualizing)
mydimordering=[] #fill this in with own ordering if desired
if mydimordering:
    newdimordering= ndim.reorderdims(mydimordering, excludecols, othercols, alldims) #will limit to dims in mydimordering
else: 
    newdimordering=defaultdimordering

# <codecell>

##find useable subejcts and define vectors of labels for all items and all emotions
[subjects, entries, dimlabels]=ndim.extractndimdata(ndimresultsfile, excludecols, othercols, columndict, item2emomapping, explicit, version, newdimordering)

# <codecell>
#assess data quality and limit accordingly
badsubjectnames, allcheckscoreavgs =ndim.checkforbadsubjects(subjects, ndim.subjavgcheckthresh)
keepers=[entry for entry in entries if entry.passedcheck] #previous exclusions were unusable data collection. this is limiting to those entries that pass the manipulation check (main character)
keepers=[entry for entry in keepers if entry.maxemopass] #limiting to those who rated the predicted emo class as one of their top explictly rated emos
keepers=[entry for entry in keepers if entry.subjid not in badsubjectnames] #limiting to those who pass the subject-level checks specified in checkforbadsubjects (including timing and overall accuracy on manipulation checks: if subjects are guessing randomly on manipulation checks, we want to exlude all their responses, not just the items where they fail)
keeperlabels=[keep.label for keep in keepers]
keeperemos=[keep.emo for keep in keepers]

# <codecell>
#look at individual difference data
ndim.analyzesubjects([subj for subj in subjects if subj.subjid not in badsubjectnames], version)

# <codecell>
#housekeeping
qlabels=set(keeperlabels)
emolabels=set(keeperemos)
orderedlabels, orderedemos=ndim.orderlists(list(emolabels),list(qlabels),keepers,orderedemos,item2emomapping) #molabels are randomly orded, here use manually sorted labels:
keepers, numstimsperemo=ndim.assignCVfolds(keepers,item2emomapping) #add cv relevant indices to keeper entries

# <codecell>

#compute item, emo, and dim avgs:
itemavgs,itemlabels,itememos,emoavgs,dimavgs=ndaw.basicdescriptives(keepers,orderedlabels, orderedemos, dimlabels, suffix, savepath)

# <codecell>

#can limit to a subset of emos
#basicsubset=['Afraid', 'Joyful', 'Disgusted', 'Sad', 'Surprise', 'Angry']
#[itemavgs, itemlabels, itememos, emoavgs, emolabels]=reduce2subset(basicsubset,itemavgs, itemlabels, itememos, emoavgs, emolabels)

# <codecell>

#do clustering analysis with number of emotions imposed:
print "****** clustering analysis******"
clusterresults=ndaw.kmeansclustering(itemavgs, itememos, emolabels)

# <codecell>

#do pca with dimensions as columns, display dimensions with highest loadings on top eigenvectors
print "****** PCA on dimensions******"
pcaondimsresults=ndaw.pcaanalysis(itemavgs, 'dimensions', dimlabels, item2emomapping, savepath, 'item-wise correlations (of tranformed item vectors in dimension PC space)', orderedlabels, suffix)

# <codecell>

#do pca with items as columns, display items with highest loadings on top eigenvectors
print "****** PCA on items******"
pcaonitemsresults=ndaw.pcaanalysis(itemavgs, 'items', orderedlabels, item2emomapping, savepath, 'item-wise correlations (of tranformed dimension vectors in item PC space)', orderedlabels, suffix)

# <codecell>

#classify emo based on all dimensions, cross validate across split halves, display emo similarity space in each fold
classresults={}
print "****** evenodd classifications******"
cvfolds=range(2) # evenodd takes values 0 and 1
cvtype='evenodd'
classresults[cvtype]=ndaw.classifyitemsummaries(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, matrixtitle='emo-wise correlations (across items)', savetitle='emosimilarities_xhalves', suffix=suffix)
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
classresults[cvtype]=ndaw.classifyitemsummaries(cvfolds, cvtype, keepers, orderedlabels, orderedemos, item2emomapping, savepath, matrixtitle='emo-wise correlations (across items)', savetitle='emosimilarities_xhalves', suffix=suffix)
print 'avg accuracy across folds: '+ str(classresults[cvtype]['summaryacc']*100)+'% (chance='+str(classresults[cvtype]['chance'])+')'
# <codecell>

#plot various classification results
ndaw.plotclassresults(classresults)

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


