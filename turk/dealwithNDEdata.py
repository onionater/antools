# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 16:11:48 2013

@author: amyskerry
"""

import csv
import numpy as np
import aeslazy as asl
import matplotlib.pyplot as plt

resultsfile='/Users/amyskerry/NDEdl.csv'
numquestions=85

def extractdata(datafile):
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        subjdata=[]
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                sqlnames=row
                print 'varnames in sql: '+str(sqlnames)
                incindex=sqlnames.index('submission_date')
            else:
                subjdata.append(row)
    return sqlnames, subjdata
                
def findbads(datamatrix):
    badsubjs=[0 for subj in datamatrix]
    for subjnum,subj in enumerate(datamatrix):
        checkindex=vars.index('q86')
        answerindex=vars.index('correctA86')
        if subj[checkindex]!='Neutral':
            print subj[answerindex]+ ': ' + subj[checkindex]
            badsubjs[subjnum]=badsubjs[subjnum]+1
        checkindex=vars.index('q87')
        answerindex=vars.index('correctA87')
        if subj[checkindex]!='Neutral':
            print subj[answerindex]+ ': ' + subj[checkindex]
            badsubjs[subjnum]=badsubjs[subjnum]+1
    return badsubjs

def scoreitems(sqlnames,datamatrix,numitems,*args):
    if args:
        excludes=args[0]
    groupscores=[]
    groupresponses=[]
    groupjudgecount=[0 for i in range(numitems)]
    groupanswers=['NULL' for i in range(numitems)]
    for subjn,subj in enumerate(datamatrix):
        itemresponses=[]
        itemlabels=[]
        itemanswers=[]
        itemacc=[]
        if excludes[subjn]==0:
            for q in range(1,numitems+1):
                anscol=sqlnames.index('correctA'+str(q))
                respcol=sqlnames.index('q'+str(q))
                itemlabels.append('q'+str(q))
                if subj[anscol]!='NULL':
                    groupanswers[q-1]=subj[anscol]
                itemresponses.append(subj[respcol])
                if subj[respcol]!='NULL':
                    itemacc.append(int(subj[respcol]==subj[anscol]))
                    groupjudgecount[q-1]=groupjudgecount[q-1]+1
                else:
                    itemacc.append(nan)
            print len(itemacc)
            groupscores.append(np.array(itemacc))
            groupresponses.append(itemresponses)
    grouplabels=itemlabels
    #groupacc=groupscores(np.mean(groupscores))
    return grouplabels, groupanswers, groupscores, groupresponses, groupjudgecount

def condenseaccuracies(sqlnames,stimavgs,answers,responses, *args):
    if orderedemos in args:
        emos=orderedemos
    else:
        emos=list(set(answers))
        emos.remove('NULL')
    emoaccs=[]
    emomatrix=[]        
    for emo in emos:
        emomatrix.append([0 for e in emos])
        critstring="element==\'"+emo+"\'"
        #print critstring
        theseindices=asl.allindices(answers, critstring)
        thesevalues=[]
        for i in theseindices:
            thesevalues.append(stimavgs[i])
        emoaccs.append(np.nanmean(thesevalues))
    for respnum,resp in enumerate(responses):
        for q in range(1,numitems+1):
            correct=answers[q-1]
            if correct !='NULL':
                correctindex=emos.index(correct)
            try:
                respindex=emos.index(resp[q-1])
                emomatrix[correctindex][respindex]=emomatrix[correctindex][respindex]+1#not normalized
            except:
                pass
    sums=np.sum(emomatrix,1)
    print sums
    newmatrix=[]
    for ln,line in enumerate(emomatrix):
        newmatrix.append(map(lambda x:float(x)/sums[ln], line)) 
    print newmatrix
    emomatrix=newmatrix
    emomatrix=np.array(emomatrix)
    ax=plt.subplot()
    pcolor(emomatrix, cmap='hot')
    plt.xticks(map(lambda x:x+.5, range(len(emos))),emos, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(emos))),emos)
    ax.set_ylabel('correct emotion')
    ax.set_xlabel('guessed emotion')
    return emos, emoaccs, emomatrix
    
[varnames,data]=extractdata(resultsfile)
excl_list=findbads(data)
[gl,ga,gs,gr,gjc]=scoreitems(vars,data,numquestions,excl_list)
stimmeans=list(np.nanmean(gs,0))
orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed' ]
[emonames, emoaccuracies, emoerrors]=condenseaccuracies(varnames, stimmeans,ga,gr, orderedemos)


