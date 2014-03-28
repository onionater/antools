# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 16:11:48 2013

@author: amyskerry
"""
import csv
import numpy as np
import matplotlib.pyplot as plt

#checkremoves=(86,87)
global checkremoves
checkremoves=(201,202)

resultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/NDE_data/sqldata/NDEdl.csv'
global numquestions
numquestions=202

def extractdata(datafile):
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        subjdata=[]
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                sqlnames=row
                #print 'varnames in sql: '+str(sqlnames)
                incindex=sqlnames.index('submission_date')
            else:
                subjdata.append(row)
    return sqlnames, subjdata
                
def findbads(datamatrix, varnames):
    badsubjs=[0 for subj in datamatrix]
    for subjnum,subj in enumerate(datamatrix):
        c1='q'+str(checkremoves[0])
        c2='q'+str(checkremoves[1])
        a1='correctA'+str(checkremoves[0])
        a2='correctA'+str(checkremoves[1])
        checkindex=varnames.index(c1)
        answerindex=varnames.index(a1)
        if subj[checkindex]!='Neutral':
            #print subj[answerindex]+ ': ' + subj[checkindex]
            badsubjs[subjnum]=badsubjs[subjnum]+1
        checkindex=varnames.index(c2)
        answerindex=varnames.index(a2)
        if subj[checkindex]!='Neutral':
            #print subj[answerindex]+ ': ' + subj[checkindex]
            badsubjs[subjnum]=badsubjs[subjnum]+1
    return badsubjs

def scoreitems(sqlnames,datamatrix,numitems,*args):
    if args:
        excludes=args[0]
    groupscores=[]
    groupresponses=[]
    qs=range(1,numquestions+1)
    qs.remove(checkremoves[0])
    qs.remove(checkremoves[1])
    groupjudgecount=[0 for i in qs]
    groupanswers=['NULL' for i in range(numquestions)]
    itemlabels=['q'+str(q) for q in qs]
    for subjn,subj in enumerate(datamatrix):
        itemresponses=[]
        itemanswers=[]
        itemacc=[]
        if excludes[subjn]==0:
            for qn, q in enumerate(qs):
                anscol=sqlnames.index('correctA'+str(q))
                respcol=sqlnames.index('q'+str(q))
                if subj[anscol]!='NULL':
                    groupanswers[q-1]=subj[anscol]
                itemresponses.append(subj[respcol])
                if subj[respcol]!='NULL':
                    itemacc.append(int(subj[respcol]==subj[anscol]))
                    groupjudgecount[qn]=groupjudgecount[qn]+1
                else:
                    itemacc.append(np.nan)
            groupscores.append(np.array(itemacc))
            groupresponses.append(itemresponses)
    #groupacc=groupscores(np.mean(groupscores))
    return itemlabels, groupanswers, groupscores, groupresponses, groupjudgecount

def condenseaccuracies(sqlnames,stimavgs,answers,responses, *args):
    if orderedemos in args:
        emos=orderedemos
    else:
        emos=list(set(answers))
        emos.remove('NULL')
    #answers=[ans for ans in answers if ans !='NULL']
    emoaccs=[]
    emomatrix=[]        
    for emo in emos:
        emomatrix.append([0 for e in emos])
        #print critstring
        theseindices=[xn for xn,x in enumerate(answers) if x==emo]
        thesevalues=[]
        for i in theseindices:
            thesevalues.append(stimavgs[i])
        emoaccs.append(np.nanmean(thesevalues))
    for respnum,resp in enumerate(responses):
        qs=range(1,numquestions+1)
        qs.remove(checkremoves[0])
        qs.remove(checkremoves[1])
        for q in qs:
            correct=answers[q-1]
            if correct not in ('NULL'):
                correctindex=emos.index(correct)
            try:
                respindex=emos.index(resp[q-1])
                emomatrix[correctindex][respindex]=emomatrix[correctindex][respindex]+1#not normalized
            except:
                pass
    sums=np.sum(emomatrix,1)
    newmatrix=[]
    for ln,line in enumerate(emomatrix):
        newmatrix.append(map(lambda x:float(x)/sums[ln], line)) 
    #print newmatrix
    emomatrix=newmatrix #to normalize each row, use newmatrix
    emomatrix=np.array(emomatrix)
    f=plt.figure()
    ax=plt.subplot()
    im=plt.pcolor(emomatrix, cmap='hot')
    plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(emos))),emos, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(emos))),emos)
    ax.set_ylabel('correct emotion')
    ax.set_xlabel('guessed emotion')
    return emos, emoaccs, emomatrix
    
[varnames,data]=extractdata(resultsfile)
excl_list=findbads(data, varnames)
[gl,ga,gs,gr,gjc]=scoreitems(varnames,data,numquestions,excl_list)
counts=calcsubjsperitem(gl,gr)
stimmeans=list(np.nanmean(gs,0))
#orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise','Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed']
orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
[emonames, emoaccuracies, emoerrors]=condenseaccuracies(varnames, stimmeans,ga,gr, orderedemos)
npgjc=np.array(gjc)
maxN=13
blacklist=np.array(gl)[npgjc>maxN]


