# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 14:47:40 2014

@author: amyskerry
"""
import sys
sys.path.append('/Users/amyskerry/Dropbox/antools/utilities')

import csv
from collections import Counter,OrderedDict
import aesbasicfunctions as abf
import numpy as np
import itertools
import matplotlib.pyplot as plt
import matplotlib.font_manager as fmnger
from sklearn import svm, cluster, decomposition
import seaborn as sns


#default style parameters
bigfig=[8,10]
medfig=[6,4]
checkthresh=3 #threshold for considering each entry a check passer or not
subjavgcheckthresh=7 #threshold for avgcheckscore for a subject to be included

class Entry():
    def __init__(self, thresh=checkthresh, rownum=[],subjid=[],version=[], label=[], emo=[], dimvect=[], check=[], correctemorating=[], maxemo=[], stimnum=[], subjnum=[], evenodd=[], explicit=[]):
        self.thresh=thresh
        self.rownum=rownum        
        self.subjid=subjid
        self.version=version
        self.label=label #stimlabel
        self.emo=emo
        self.dimvect=dimvect
        self.check=int(check)
        self.correctemorating=correctemorating
        self.evenodd=evenodd #split data for each item into two CV halves
        self.stimnum=stimnum #ind num for each stim item in the emo category
        self.subjnum=subjnum #ind num for each subject in the item (1 through num of hits/item)
        self.maxemo=maxemo
        self.maxemopass=emo in maxemo
        self.explicitpass=correctemorating>thresh
        self.passedcheck=self.check>self.thresh
        self.explicit=explicit
        self.explicitfit=1
        self.dimensionfit=1 #how well does the dimvect align with the group
        
class Stimulus():
    def __init__(self,qlabel=[],emotion=[],	num=[],valence=[],source=[],person=[],contentsummary=[],lengthinwords=[],durationinsecs=[],stimcontent=[]):
        self.qlabel=qlabel        
        self.emotion=emotion
        self.num=num
        self.valence=valence
        self.source=source
        self.person=person
        self.contentsummary=contentsummary
        self.lengthinwords=lengthinwords
        self.durationinsecs=durationinsecs
        self.stimcontent=stimcontent
        
class Subject():
    def __init__(self,subjid=[], finalrownum=[],rownums=[], subdate=[], version=[], checkscores=[], gender=[], age=[], city=[], country=[], thoughts=[], noface=np.nan, nothought=np.nan, needverbal=np.nan, facevoice=np.nan, surprised=np.nan):
        self.subjid=subjid
        self.finalrownum=finalrownum        
        self.rownums=rownums
        self.subdate=subdate
        self.version=version
        self.checkscores=checkscores        
        self.gender=gender
        self.age=age
        self.city=city
        self.country=country
        self.thoughts=thoughts
        self.noface=abf.float_or_nan(noface) 
        self.nothought=10-abf.float_or_nan(nothought) #10 - x for reverse coded items
        self.needverbal=10-abf.float_or_nan(needverbal)
        self.facevoice=10-abf.float_or_nan(facevoice)
        self.surprised=10-abf.float_or_nan(surprised)
        self.specificEIQ=np.mean([float(self.noface), float(self.needverbal), float(self.facevoice), float(self.surprised)])
        self.generalEIQ=self.nothought
        self.allEIQ=np.mean([float(self.specificEIQ), float(self.generalEIQ)])
        self.included=[]
    @property
    def avgcheckscore(self):
        return np.mean(self.checkscores)
    def assessinddff(self,entries):
        relentries=[entry for entry in entries if entry.subjid==self.subjid]
        subjexplicitscore=1
        subjdimensionscore=1 
        return explicitscore, dimensionscore

def makesubject(entries, existingsubjects, colnames, subjdata, nameindex, rowindex, incindex, checkindex, version, subjectthresh=8):
    subjname=subjdata[nameindex]
    existingsubswithname=searchobjects(existingsubjects, {'subjid':subjname})
    if version in ('ver2', 'ver2_control'):
        columns=['submission_date', 'gender', 'age', 'city', 'country', 'thoughts', 'response_noface', 'response_nothought', 'response_needverbal', 'response_facevoice', 'response_surprised']
    elif version=='pilot':
        columns=['submission_date', 'gender', 'age', 'city', 'country', 'thoughts']
    md={}
    for column in columns:
        md[column]=colnames.index(column)
    if len(existingsubswithname)>0:
        subjname=subjname+'duplicate'
    if version in ('ver2', 'ver2_control'):
        subject=Subject(subjid=subjname, finalrownum=subjdata[rowindex], subdate=subjdata[md['submission_date']], version=version, gender=subjdata[md['gender']], age=subjdata[md['age']], city=subjdata[md['city']], country=subjdata[md['country']], thoughts=subjdata[md['thoughts']], noface=subjdata[md['response_noface']], nothought=subjdata[md['response_nothought']], needverbal=subjdata[md['response_needverbal']], facevoice=subjdata[md['response_facevoice']], surprised=subjdata[md['response_surprised']])
    elif version=='pilot':
        subject=Subject(subjid=subjname, finalrownum=subjdata[rowindex], subdate=subjdata[md['submission_date']], version=version, gender=subjdata[md['gender']], age=subjdata[md['age']], city=subjdata[md['city']], country=subjdata[md['country']], thoughts=subjdata[md['thoughts']])
    relevantentries=searchobjects(entries, {'subjid':subjname})
    subject.checkscores=[row.check for row in relevantentries]
    subject.rownums=[row.rownum for row in relevantentries]
    subject.included=np.mean(subject.checkscores)>subjectthresh
    return subject
    
def analyzesubjects(subjects, version):
    if version in ('ver2', 'ver2_control'):
        noface=[subj.noface for subj in subjects]
        facevoice=[subj.facevoice for subj in subjects]
        nothought=[subj.nothought for subj in subjects]
        needverbal=[subj.needverbal for subj in subjects]
        surprised=[subj.surprised for subj in subjects]
        specific=[subj.specificEIQ for subj in subjects]
        general=[subj.generalEIQ for subj in subjects]
        scounts, slabels=np.histogram(specific, bins=20)
        gcounts, glabels=np.histogram(general, bins=20)
        fig, axes=plt.subplots(3)
        axes[0].bar(range(len(scounts)), scounts)
        axes[0].set_xticklabels(slabels)
        axes[1].bar(range(len(gcounts)), gcounts)
        axes[1].set_xticklabels(glabels)
        axes[2].scatter(general,specific)
        axes[2].set_xlabel('general')
        axes[2].set_ylabel('specific')
        fig, axes=plt.subplots(4,3)
        axes[0,0].scatter(noface,facevoice); axes[0,0].set_xlabel('noface'); axes[0,0].set_ylabel('facevoice')
        axes[1,0].scatter(noface,nothought); axes[1,0].set_xlabel('noface'); axes[1,0].set_ylabel('nothought')
        axes[2,0].scatter(noface,needverbal); axes[2,0].set_xlabel('noface'); axes[2,0].set_ylabel('needverbal')
        axes[3,0].scatter(noface,surprised); axes[3,0].set_xlabel('noface'); axes[3,0].set_ylabel('surprised')
        axes[0,1].scatter(facevoice,nothought); axes[0,1].set_xlabel('facevoice'); axes[0,1].set_ylabel('nothought')
        axes[1,1].scatter(facevoice,needverbal); axes[1,1].set_xlabel('facevoice'); axes[1,1].set_ylabel('needverbal')
        axes[2,1].scatter(facevoice,surprised); axes[2,1].set_xlabel('facevoice'); axes[2,1].set_ylabel('surprised')
        axes[3,1].scatter(nothought,needverbal); axes[3,1].set_xlabel('nothought'); axes[3,1].set_ylabel('needverbal')
        axes[0,2].scatter(nothought,surprised); axes[0,2].set_xlabel('nothought'); axes[0,2].set_ylabel('surprised')
        axes[1,2].scatter(needverbal,surprised); axes[1,2].set_xlabel('needverbal'); axes[1,2].set_ylabel('surprised')

def checkselectivity(stimavgs, orderedemos, entry, label):
    selectivitythresh=-2
    accthresh=0
    correctemo=stimavgs[orderedemos.index(entry.emo)]
    stimavgs[orderedemos.index(entry.emo)]=np.nan
    nextmax=max(stimavgs)
    selectivity=correctemo-nextmax
    if selectivity>selectivitythresh and correctemo>accthresh:
        return label

def explicitemosndim(version, keepers, orderedemos, orderedlabels):
    if version in ('ver2', 'ver2_control'):
        labelXemo=[]
        selectiveitems={emo:[] for emo in orderedemos}
        for label in orderedlabels:
            relentries=[keep for keep in keepers if keep.label==label]
            stimvector=[]
            for entry in relentries:
                stimvector.append([abf.float_or_nan(entry.explicit[rowemo+'_extent']) for rowemo in orderedemos])
            if len(stimvector)==1:
                stimavgs=stimvector[0]
            elif len(stimvector)>1:
                stimavgs=np.mean(stimvector, 0)
            selectivity=checkselectivity(stimavgs, orderedemos, entry, label)
            if selectivity:
                selectiveitems[entry.emo].append(selectivity)
            labelXemo.append(np.array(stimavgs))
        fig, ax=plt.subplots(1)
        ax.pcolor(np.array(labelXemo), cmap='hot')
        ax.set_xticklabels(orderedemos)
        ax.set_yticklabels(orderedlabels)
        emoXemo=[]
        for emo in orderedemos:
            relentries=[keep for keep in keepers if keep.emo==emo]
            emovector=[]
            for entry in relentries:
                emovector.append([abf.float_or_nan(entry.explicit[rowemo+'_extent']) for rowemo in orderedemos])
            if len(emovector)==1:
                emoXemo.append(np.array(emovector[0]))
            elif len(emovector)>1:
                emoXemo.append(np.mean(emovector, 0))
        fig, ax=plt.subplots(1)
        ax.pcolor(np.array(emoXemo), cmap='hot')
        ax.set_xticklabels(orderedemos)
        ax.set_yticklabels(orderedemos)
    else:
        labelXemo='not applicable'
        emoXemo='not applicable'
        selectiveitems='not applicable'
    return labelXemo, emoXemo, selectiveitems

def searchobjects(objects, criteria):
    '''takes dict of critera and searches for entries that match''' 
    matches=objects
    try:
        for key in criteria.keys():
            matches=[m for m in matches if getattr(m,key)==criteria[key]]
    except:
        pass
    return matches
    

def extractndimdata(datafile, excludecols, othercols, columndict, item2emomapping, explicit, version, exclusioncriteria, *args):
    '''get the data from an excel file, returns good subject, list of relevant dimensions, and list of stim to emotion category mappings '''
    item2emomappingobsvered={}
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        sqlnames=reader.next()
        data=[row for row in reader]  
        print str(len(data)) +" rows in main csv file"
    rowindex, incindex, checkindex, nameindex, submissionindex, emoindex=[sqlnames.index(thevalue) for thevalue in columndict.values()]  #column dict is ordered
    [labelind, dims, dimind, emoind]=extractndimvardeets(version,sqlnames, checkindex, othercols, excludecols)
    if args[0]:
        newdimorder=args[0]
        dimind=[dimind[dims.index(dim)] for dim in newdimorder if dim in dims] #this will only use dimensions listed in newdimorder
        dims=newdimorder
    keepers=[entry for entry in data if entry[incindex] != 'NULL']
    print str(len(keepers)) +" entries with some non-null responses"
    entries=[]
    print "******checking sanity of responses, making entries for the sane ones******"
    subjects=[]
    for subjdatan,subjdata in enumerate(keepers):
        passed=sanitycheck(subjdata, nameindex, labelind, dimind, emoind)
        if passed:
            try: #this is inside a try since a subject might have completed the inclusioncol but not finished all
                dimvect=[int(subjdata[d]) for d in dimind] #so dimvect is appropriately ordered
                emotions=Counter([subjdata[e] for e in emoind]) # weird hack to deal with the fact that many entries contained one column that misspecified the emotion.
                emotion=[key for key in emotions.keys() if emotions[key]==max(emotions.values())] #deal with this by taking the emotion listed in most columns (e.g. the remaining 38 correct collumns)
                if len(emotion)>1:
                    print "warning something strange"
                maxemo, explicitjudgments=findexplicits(explicit, subjdata, version, sqlnames)
                entry=Entry(rownum=subjdata[rowindex], subjid=subjdata[nameindex], version=version, label=subjdata[labelind[0]], emo=emotion[0], dimvect=dimvect, check=subjdata[checkindex], explicit=explicitjudgments, maxemo=maxemo) #eac subj saw single emo/quest so we can just rovide the value from the first of these columns            
                entries.append(entry)            
                item2emomappingobsvered[subjdata[labelind[0]]]=subjdata[emoind[0]] #okay to do this in each row since it will just rewrite existing ones andthe mapping is the same for all subjects
            except:
                print subjdata[nameindex] + ' had a NaN dimension value for item '+ subjdata[labelind[0]]+ '. Excluding subject.'
    print str(len(entries)) +" entries passed sanity check (completed task, non-null responses)"
    weirddims, weirdsources=checkmappings(keepers,rowindex, item2emomapping, item2emomappingobsvered)
    weirdsources=[s for sublist in weirdsources for s in sublist]
    if exclusioncriteria['weirdlines']:
        entries=[e for e in entries if e.rownum not in weirdsources]
        print str(len(entries)) +" entries that didn't have wacko mislabeling of items"
    for subjdata in keepers:
        if not subjdata[submissionindex]== 'NULL': #if this is the final entry for the subject and where they submitted their demo form...                
            subjects.append(makesubject(entries, subjects, sqlnames, subjdata, nameindex, rowindex, incindex, checkindex, version))
    return subjects, entries, dims

def extractstims(stimfile):
    stims=[]
    item2emomapping={}
    stimnames,stimdata= abf.extractdata(stimfile)
    emoindex,numindex,valenceindex,sourceindex,personindex,contentindex,lengthindex, durationindex, stimindex=[stimnames.index(column) for column in ['emotion','num','valence',	'source','person','content','length_in_words','duration_in_secs','cause']]
    for linen,line in enumerate(stimdata):
        label='q'+str(linen+1)
        stim=Stimulus(qlabel=label, emotion=line[emoindex],num=line[numindex],valence=line[valenceindex],source=line[sourceindex],person=line[personindex],contentsummary=line[contentindex],lengthinwords=line[lengthindex],durationinsecs=line[durationindex],stimcontent=line[stimindex])
        stims.append(stim)
        item2emomapping[label]=line[emoindex]
    return stims, item2emomapping
    
def findexplicits(explicit, subjdata, version, sqlnames):
    explicitindices=[sqlnames.index(e) for e in explicit]
    explicitjudgments={explicit[en]:subjdata[e] for en,e in enumerate(explicitindices)}
    if version in ('ver2', 'ver2_control'):
        maxemo=[key[0:-7] for key in explicitjudgments.keys() if explicitjudgments[key]==str(np.max([int(el) for el in explicitjudgments.values()]))]                
    elif version=='pilot':
        maxemo=subjdata[explicitindices[0]]
    else:
        print "warning: version "+version+" unknown"  
        maxemo=[]
    return maxemo, explicitjudgments  

def checkforbadsubjects(subjects, subjavgcheckthresh):
    avgs=[subject.avgcheckscore for subject in subjects]
    bads=[subject.subjid for subject in subjects if subject.avgcheckscore<subjavgcheckthresh or np.isnan(subject.avgcheckscore)]
    #implement checker that goes into turk csvs and checks' how long turker spent on the task
    return bads, avgs
          
    
def setfiles(version):
    if version=='pilot':
        nderesultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim/data/NDE_data/sqldata/NDEdl_study1.csv'
        rootdir='/Users/amyskerry/documents/projects/turk/NDE_dim/data/DIM_data/'
        ndimresultsfile=rootdir+'sqldata/NDE_dimdl.csv'
        stimfile='/Users/amyskerry/documents/projects/turk/NDE_dim/app/NDE_stims.csv'
        appraisalfile='/Users/amyskerry/documents/projects/turk/NDE_dim/app/appraisals.csv'
    elif version=='ver2':
        nderesultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/NDE_data/sqldata/NDEdl_combined.csv'
        rootdir='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/DIM_data/'
        ndimresultsfile=rootdir+'sqldata/NDE_dimdl2.csv'
        stimfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/task/appdata/NDE_stims.csv'
        appraisalfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/task/appdata/appraisals_main.csv'
    elif version=='ver2_control':
        nderesultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/NDE_data/sqldata/NDEdl_combined.csv'
        rootdir='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/DIM_data/'
        ndimresultsfile=rootdir+'sqldata/NDE_dimdl2_control.csv'
        stimfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/task/appdata/NDE_stims.csv'
        appraisalfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/task/appdata/appraisals_control.csv'
    savepath=rootdir+'outputfigs/'
    return rootdir, nderesultsfile, ndimresultsfile, stimfile, appraisalfile, savepath

def setndevals(version):
    if version=='pilot':
        orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise','Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed']
        checkquestions=(86,87)
        expectedanswers=('Neutral', 'Neutral')
        inclusioncols={'submission_date': (lambda inputval: inputval not in ('NULL',))} #key=column, value=function returning whether given item is a keeper
    elif version in ('ver2', 'ver2_control'):
        orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
        checkquestions=(201,202)#(86,87)
        expectedanswers=('Neutral', 'Neutral') #what do you expect from these two checks
        inclusioncols={'submission_date': (lambda inputval: inputval not in ('NULL',))} #key=column, value=function returning whether given item is a keeper    
    return checkquestions, expectedanswers, inclusioncols, orderedemos

def setndimvals(version, suffix, appraisalfile, stimfile):
    if version=='pilot':
        orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise', 'Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed'] #same as NDE but without surprise
        defaultdimordering=['familiarity','expectedness','certainty','suddenness','pleasantness', 'goal_consistency',  'control', 'fixing','self_cause','agent_cause', 'agent_intention', 'coping','pressure', 'freedom', 'moral','fairness', 'past_present', 'bodily_disease','consequences', 'safety', 'close_others','people','mental_states', 'others_knowledge', 'confidence','relevance', 'self_involvement']
        othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts', 'emotion', 'emotion_qlabel', 'emotion_qemo', 'main_character']    
        valenceddims=['pleasantness', 'goal_consistency', 'safety']
        explicit=['emotion']
        columndict=OrderedDict([('rownum', 'rownum'),('inclusion','pleasantness'), ('check','main_character'),('subjid','subjid'), ('sumbission_date', 'submission_date'), ('emotion', 'pleasantness_qemo')])
    elif version =='ver2':
        orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
        defaultdimordering=['expectedness', 'pleasantness', 'goal_consistency', 'fairness', 'agent_cause', 'agent_intention', 'self_cause', 'close_others', 'control', 'altering', 'moral', 'selfesteem', 'suddenness', 'familiarity', 'future', 'past', 'occurred', 'certainty', 'repetition', 'coping', 'mental_states', 'others_knowledge', 'bodily_disease', 'people', 'relevance', 'freedom', 'pressure', 'consequences', 'danger', 'self_involvement', 'remember', 'self_consistency', 'relationship_influence', 'agent_situation', 'attention', 'psychological_change', 'safey', 'knowledge_change']
        othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts', 'Neutral_extent', 'emotion', 'emotion_qlabel', 'emotion_qemo', 'main_character', 'response_noface', 'response_intune', 'response_nothought', 'response_needverbal', 'response_facevoice', 'response_surprised']
        explicit=[emo+'_extent' for emo in orderedemos]
        for emo in explicit:
            othercols.append(emo)
        valenceddims=['pleasantness', 'goal_consistency', 'safety']
        columndict=OrderedDict([('rownum', 'rownum'),('inclusion','pleasantness'), ('check','main_character'),('subjid','subjid'), ('sumbission_date', 'submission_date'), ('emotion', 'pleasantness_qemo')])
    elif version =='ver2_control':
        orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
        defaultdimordering=['valence', 'arousal', 'afraid_dim', 'angry_dim', 'sad_dim', 'disgusted_dim','surprised_dim','happy_dim']
        othercols=['subjid', 'rownum','submission_date', 'city','country','age','gender','thoughts', 'Neutral_extent', 'emotion', 'emotion_qlabel', 'emotion_qemo', 'main_character', 'response_noface', 'response_intune', 'response_nothought', 'response_needverbal', 'response_facevoice', 'response_surprised']
        explicit=[emo+'_extent' for emo in orderedemos]
        for emo in explicit:
            othercols.append(emo)
        valenceddims=['valence']
        columndict=OrderedDict([('rownum', 'rownum'),('inclusion','valence'), ('check','main_character'),('subjid','subjid'), ('sumbission_date', 'submission_date'), ('emotion', 'valence_qemo')])
    appraisalnames,appraisaldata= abf.extractdata(appraisalfile)
    stims,item2emomapping=extractstims(stimfile)
    alldims=[row[appraisalnames.index('Dqname')] for row in appraisaldata]
    suffixmappings={'allvars':[], 'nv':valenceddims, 'vonly':[i for i in alldims if i not in valenceddims], 'valencearousalset':['happy_dim', 'sad_dim', 'angry_dim', 'afraid_dim', 'surprised_dim', 'disgusted_dim'], 'basicemoset':['valence','arousal']} #dims not included in the suffix version
    excludecols=suffixmappings[suffix]
    return orderedemos, appraisalnames, appraisaldata, stims, item2emomapping, alldims, defaultdimordering, explicit, othercols,valenceddims, columndict, suffixmappings,excludecols

    
def extractndimvardeets(version,names,checkindex,othercols, excludecols):
    ''' returns indices for questions columns, emotion columns, dimension columns, as well as list of dimension c'''
    excl=[othercols, excludecols]
    excludables=[el for sublist in excl for el in sublist]
    labelindices=[sqlnum for sqlnum,sqln in enumerate(names) if 'qlabel' in sqln and sqln not in excludables]
    emoindices=[sqlnum for sqlnum,sqln in enumerate(names) if 'qemo' in sqln and sqln not in excludables]
    dimindices=[sqlnum for sqlnum,sqln in enumerate(names) if not any(substr in sqln for substr in ('qemo', 'qlabel')) and sqln not in excludables]
    dims=[sqln for sqlnum,sqln in enumerate(names) if not any(substr in sqln for substr in ('qemo', 'qlabel')) and sqln not in excludables]
    if version=="ver2_control": #because, confusingly surprised and disgusted are both emos and appraisals in ver2_control
        dims.append('surprised_dim')
        dims.append('disgusted_dim')
        dimindices.append(names.index('Surprised_extent'))
        dimindices.append(names.index('Disgusted_extent'))
    return labelindices, dims, dimindices,emoindices
    
def sanitycheck(subject, nameindex, labelindices, dimindices, emoindices):
    passed=True
    subjitems=[subject[l] for l in labelindices]    
    items=set(subjitems)
    subjresponses=[subject[d] for d in dimindices]
    responses=set(subjresponses)
    subjemos=[subject[e] for e in emoindices]
    emos=set(subjemos)
    maxnumemos=len(emos)
    subjid=subject[nameindex]
    if len(items)>1:
        print subjid+": too many items: " 
        print Counter(subjitems)
        passed=False
    if len(emos)>1:
        if maxnumemos-1 in Counter(subjemos).values():
            pass #if there's just one bad column, don't worry
        else:
            print subjid+": too many emotions: " 
            #print emos
            passed=False
            print Counter(subjemos)
    if 'NULL' in responses:
        print subjid+": contains null responses"
        passed=False
    return passed
    
def orderlists(emos,qlabels,keepers, orderedemos,item2emomapping):
    '''instead of qlabels, make item labels ordered to align with emos above'''
    orderedemos=[e for e in orderedemos if e in emos]
    labelsets=[]
    for emo in orderedemos:
        labelsets.append([item for item in item2emomapping.keys() if item2emomapping[item]==emo])
    orderedlabels=[item for itemlist in labelsets for item in itemlist]
    return orderedlabels,orderedemos
    
def checkmappings(data, rowindex, idealmapping, observedmapping):
    bads=[]
    sources=[]
    print "******checking mappings******"
    for key in observedmapping.keys():
        if idealmapping[key]!=observedmapping[key]:
            print "mistmatch for " +key
            print "expected: "+idealmapping[key]
            print "observed: "+observedmapping[key] 
            bads.append(key)
            sources.append([row[rowindex] for row in data if observedmapping[key] in row and key in row])
    return bads, sources
                
def assignCVfolds(keepers, item2emomapping):
    '''give each item within an emotion category'''
    emolabels=abf.uniquifyordered(item2emomapping.values())
    #get labels and emos matched in ordering
    labelsets=[]
    for emo in emolabels:
        labelsets.append([item for item in item2emomapping.keys() if item2emomapping[item]==emo])
    qlabels=[item for itemlist in labelsets for item in itemlist]
    #assign within item cv labels
    for qlabel in qlabels:
        entries=[keep for keep in keepers if keep.label==qlabel]
        for entryn,entry in enumerate(entries):
            entry.subjnum=entryn #index up through # of hits per item
            entry.evenodd= int(entryn % 2 ==1)
    #assign item-based cv labels
    itemcounts=[]
    for emon, emo in enumerate(emolabels):
        entries=[keep for keep in keepers if keep.emo==emo]
        relevantlabels=labelsets[emon]
        numitemsperemo=len(relevantlabels)
        relnums=range(numitemsperemo)
        itemcounts.append(numitemsperemo)
        for entry in entries:
            entry.stimnum=relnums[relevantlabels.index(entry.label)]+1
    return keepers, max(itemcounts)
    
def getitemavgs(keepers, items,**kwargs):
    ''' prints vector of avg dimension scores (avg across subjects) for each item, as well as vector of item labels and their corresponding emotions'''
    for condition in kwargs:
        #print "eliminating if " +condition+ ' not equal to ' + str(kwargs[condition])
        keepers=[keep for keep in keepers if getattr(keep,condition)==kwargs[condition]] # continues to eliminate for each kwarg (mainly for selecting cv based on hitnum)
    itemvects=[]
    newitems=[]
    itememos=[]
    foundatleast1=0
    for lan, la in enumerate(items):
        subset=np.array([keep.dimvect for keep in keepers if keep.label==la]) #datavectors for the stimulus
        keeps=[keep for keep in keepers if keep.label==la] #full entries for the stimulus
        try:
            emo=keeps[0].emo
            try:
                dimavg=np.mean(subset,0)
            except:
                print 'warning: there were some nans in your dimension vectors for stim ' + la +' (emo=' + emo + ')'
                dimavg=np.nanmean(subset,0)
            if not any([np.isnan(val) for val in dimavg]):
                itemvects.append(dimavg)
                newitems.append(la) #limited to labels for which there are keepers
                itememos.append(emo)
                foundatleast1=1
            else:
                print "warning: some dimensions had nan avgs"
        except:
            #print "warning: no entries for item " + la
            pass
    try: 
        append= " (fold " + kwargs.items()[0][0]+', '+kwargs.items()[0][1] +")"
    except:
        append=""
    if foundatleast1==0:
        print "warning: fold contains no items"+append
    else:
        print "found "+str(len(itemvects)) +append
    return itemvects, newitems, itememos

def getemoavgs(keepers, emolabels, **kwargs):
    numdims=len(keepers[0].dimvect) #assumes all subjects have same number of dimensions and pulls from first
    for condition in kwargs:
        keepers=[keep for keep in keepers if getattr(keep,condition)==kwargs[condition]]
    emovects=[]
    newemolabels=[]
    foundatleast1=0
    for la in emolabels:
        subset=np.array([keep.dimvect for keep in keepers if keep.emo==la])
        if len(subset)>0:
            dimavg=np.mean(subset,0)
            if not any([np.isnan(val) for val in dimavg]):
                emovects.append(dimavg)
                newemolabels.append(la)
        else: 
            emovects.append(np.array([5 for el in range(numdims)])) #temp hack, if no vecter set all to 5
            newemolabels.append(la)
    return emovects, newemolabels  
    
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
        dataA=data[c[0]]
        dataB=data[c[1]]
        corrmatrix=[np.array([np.corrcoef(rowA,rowB)[0,1] for rowB in dataB]) for rowA in dataA]
        corrmatrices.append(corrmatrix)
    corrmeans=np.nanmean(np.array(corrmatrices),0)
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
    for inum,i in enumerate(cvfolds):
        testlabels=np.array([label for foldnum, fold in enumerate(datalabels) for label in fold if foldnum==inum]) #get relevant test indices
        trainlabels=np.array([label for foldnum, fold in enumerate(datalabels) for label in fold if foldnum!=inum]) #get relevant train indices
        testset=np.array([d for foldnum,fold in enumerate(dataavgs) for d in fold if foldnum==inum])
        trainset=np.array([d for foldnum,fold in enumerate(dataavgs) for d in fold if foldnum !=inum])
        chance=1.0/len(set(trainlabels))
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
    
def reorderdims(newdimordering, excludecols, othercols, alldims):
    '''take user specified ordering and remove excludedcols. also check against what is derived from appraisals.csv '''
    newdimordering=[el for el in newdimordering if el not in excludecols and el not in othercols]
    alldims=[el for el in alldims if el not in excludecols and el not in othercols]
    if len(newdimordering) != len(alldims):
        print "warning, your number of specified new dimensions ("+str(len(newdimordering))+") don't match what is in appraisals.csv ("+str(len(alldims))+")"
    mismatches=[dim for dim in newdimordering if dim not in alldims]
    mismatches2=[dim for dim in alldims if dim not in newdimordering]
    if any([mismatches, mismatches2]):
        print "warning, your ordered dims don't match your appraisal.csv file"
        print mismatches
        print mismatches2
    return newdimordering

def reduce2subset(subset,itavgs, ilabels, iemos, emavgs, elabels):
    reduceditavgs=[item for itemn,item in enumerate(itavgs) if iemos[itemn] in subset]
    reducedilabels=[item for itemn,item in enumerate(ilabels) if iemos[itemn] in subset]
    reducediemos=[item for item in iemos if item in subset]
    reducedemavgs=[item for itemn,item in enumerate(emavgs) if elabels[itemn] in subset]
    reducedelabels=[item for item in elabels if item in subset]
    return reduceditavgs,reducedilabels,reducediemos, reducedemavgs, reducedelabels
