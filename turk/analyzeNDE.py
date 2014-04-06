# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 09:23:47 2014

@author: amyskerry
"""
import sys
sys.path.append('/users/amyskerry/dropbox/antools/utilities/')
import csv
import numpy as np
import matplotlib.pyplot as plt
import aesbasicfunctions as abf


def findqlabels(sqlnames):
    itemlabels=[label for label in sqlnames if label[0]=='q' and abf.is_string_a_number(label[1:])]
    return itemlabels
    
def extractdata(datafile):
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        subjdata=[]
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                sqlnames=row
            else:
                subjdata.append(row)
    return sqlnames, subjdata

def findcheckfailers(datamatrix, varnames, checkqs, expectedans):
    badsubjs=[0 for subj in datamatrix]
    for subjnum,subjdata in enumerate(datamatrix):
        for eansn, eans in enumerate(expectedans):
            questionlabel='q'+str(checkqs[eansn])
            answer='correctA'+str(checkqs[eansn])
            checkindex=varnames.index(questionlabel)
            answerindex=varnames.index(answer)
        if subjdata[checkindex]!=eans:
            badsubjs[subjnum]+=1
    return badsubjs

def testinclusioncrit(datamatrix, varnames, inclusions):
    badsubjs=[0 for subj in datamatrix]
    for subjnum,subjdata in enumerate(datamatrix):
        for criteria in inclusions:
            colindex=varnames.index(criteria)
            match=inclusions[criteria](subjdata[colindex])
        if not match:
            badsubjs[subjnum]+=1
    return badsubjs
    
def scoreitems(sqlnames,datamatrix,checkqs,*args):
    if args:
        excludes=args[0]
    itemlabels=findqlabels(sqlnames)
    for check in checkqs:
        item='q'+str(check)
        itemlabels.remove(item)
    numitems=len(itemlabels)
    num_responses_per_item=[0 for i in range(numitems)]
    actual_responses_per_item=[]
    allanswers_per_item=[]
    accuracy_per_item=[]
    correct_ans_per_item=['NULL' for i in range(numitems)]
    for subjn,subj in enumerate(datamatrix):
        if not excludes[subjn]:
            itemresponses=[subj[sqlnames.index(item)] for item in itemlabels]
            itemanswers=[subj[sqlnames.index('correctA'+item[1:])] for item in itemlabels]
            accuracy_per_item.append(np.array([int(itemr==itemanswers[itemn]) if itemr !='NULL' else np.nan for itemn,itemr in enumerate(itemresponses)]))
            actual_responses_per_item.append(itemresponses) 
            allanswers_per_item.append(itemanswers)
    itemwiseans=zip(*allanswers_per_item)
    num_responses_per_item=[[int(not response=='NULL') for response in item] for item in itemwiseans]
    num_responses_per_item=[sum(item) for item in num_responses_per_item]
    for iteman, itema in enumerate(itemwiseans):
        itema=[i for i in itema if not i == 'NULL']
        if itema:
            correct_ans_per_item[iteman]=itema[0]
    return itemlabels, correct_ans_per_item, accuracy_per_item, actual_responses_per_item, num_responses_per_item
    
def condenseaccuracies(sqlnames,stimavgs,answers,checkqs, responses, *args):
    if args:
        emos=args[0]
    else:
        emos=list(set(answers)).remove('NULL')
    itemlabels=findqlabels(sqlnames)
    for check in checkqs:
        item='q'+str(check)
        itemlabels.remove(item)
    #accuracies
    emoaccs=[]
    print emos     
    for emo in emos:
        theseindices=[ansind for ansind,ans in enumerate(answers) if ans==emo]
        thesevalues=[stimavgs[i] for i in theseindices]
        emoaccs.append(np.nanmean(thesevalues))
    #confusions
    emomatrixcounts=[[0 for e in emos] for e in emos] 
    for respnum,resp in enumerate(responses):
        for itemn,item in enumerate(itemlabels):
            correct=answers[itemn]
            if correct not in ('NULL',):
                correctindex=emos.index(correct)
            try:
                respindex=emos.index(resp[itemn])
                emomatrixcounts[correctindex][respindex]+=1#not normalized
            except:
                pass
    sums=np.sum(emomatrixcounts,1) #how many times that row recieved any answer
    emomatrixcounts=np.array(emomatrixcounts)
    # convert from raw values to percentage correct
    emomatrixpercent=[map(lambda x:float(x)/sums[ln], line) for ln,line in enumerate(emomatrixcounts)]
    emomatrixpercent=np.array(emomatrixpercent)
    #plot them
    f=plt.figure()
    f.suptitle('raw counts')
    ax=plt.subplot()
    im=plt.pcolor(emomatrixcounts, cmap='hot')
    plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(emos))),emos, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(emos))),emos)
    ax.set_ylabel('correct emotion')
    ax.set_xlabel('guessed emotion')
    #plot it
    f=plt.figure()
    ax=plt.subplot()
    f.suptitle('percentages')
    im=plt.pcolor(emomatrixpercent, cmap='hot')
    plt.colorbar(im)
    plt.xticks(map(lambda x:x+.5, range(len(emos))),emos, rotation='vertical')
    plt.yticks(map(lambda x:x+.5, range(len(emos))),emos)
    ax.set_ylabel('correct emotion')
    ax.set_xlabel('guessed emotion')
    plt.show()
    return emos, emoaccs, emomatrixcounts, emomatrixpercent

def printdeets(qlabels, counts, stimmeans, blacklist, maxN):
    pstring=[q+': '+str(counts[qn])+', ' for qn,q in enumerate(qlabels)]
    avgaccuracy=np.nanmean(stimmeans)
    nextstring=''.join(pstring)
    #print nextstring[:-2]
    nextstring= 'blacklist the following items (have>'+str(maxN)+' responses): ' + ''.join(["'"+str(b)+"'"+', ' for b in blacklist])
    print nextstring[:-2]
    print 'average accuracy across items: '+str(avgaccuracy)+'%'

def displaybestitems(labels, answers, stimmeans):
    accthresh=.8
    print "****best NDE items*****"
    bestitems=[l for ln,l in enumerate(labels) if stimmeans[ln]>accthresh]
    print bestitems
    return bestitems

def main(resultsfile, checkquestions,expectedanswers,inclusioncols, orderedemos, maxN=12, showblacklist=0):
    [varnames,datamatrix]=extractdata(resultsfile)
    checkfailers=findcheckfailers(datamatrix, varnames, checkquestions, expectedanswers)
    incfailers=testinclusioncrit(datamatrix, varnames, inclusioncols)
    excl_list=[cf*incfailers[cfn] for cfn,cf in enumerate(checkfailers)]
    [labels,answers,correctness,responses,counts]=scoreitems(varnames,datamatrix,checkquestions,excl_list)
    stimmeans=list(np.nanmean(correctness,0))
    #bestitems=displaybestitems(labels, answers, stimmeans)
    f,axes=plt.subplots(2)
    axes[0].bar(range(len(stimmeans)), stimmeans)
    axes[0].set_xlim([0,len(stimmeans)])
    axes[0].set_title('accuracies')
    axes[1].bar(range(len(stimmeans)), counts)
    axes[1].set_xlim([0,len(stimmeans)])
    axes[1].set_title('counts')
    [emonames, emoaccuracies, emoerrorcounts, emoerrors]=condenseaccuracies(varnames, stimmeans,answers,checkquestions, responses,orderedemos)
    blacklist=[l for ln, l in enumerate(labels) if counts[ln]>maxN]
    if showblacklist:    
        printdeets(labels, counts, stimmeans, blacklist, maxN)
    
        
if __name__=='__main__':
    #hardcoding
    checkquestions=(201,202)
    #checkquestions=(86,87)
    expectedanswers=('Neutral', 'Neutral')
    resultsfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/NDE_data/sqldata/NDEdl_combined.csv' #contains NDEdl.csv and the first row of the two woops (with checks manually corrected since these subjects didn't have Neutral option)
    orderedemos=['Grateful', 'Joyful','Hopeful','Excited','Proud','Impressed','Content','Nostalgic', 'Surprised','Lonely', 'Furious','Terrified','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Devastated', 'Disappointed', 'Jealous']
    #orderedemos=['Grateful', 'Joyful','Hopeful','Proud','Impressed','Content','Nostalgic', 'Surprise','Lonely', 'Angry','Afraid','Apprehensive','Annoyed', 'Guilty', 'Disgusted','Embarrassed','Sad', 'Disappointed']
    maxN=12 #blacklist questions with this many or more
    inclusioncols={'submission_date': (lambda inputval: inputval not in ('NULL',))} #key=column, value=function returning whether given item is a keeper
    main(resultsfile, checkquestions,expectedanswers,inclusioncols, orderedemos)
    
