# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 07:21:19 2014

@author: amyskerry
"""
import os
import scipy.io
import csv
import numpy as np

conditionmapping={'1':'sh', '2':'su','3':'nh','4':'nu','5':'fh','6':'fu','7':'mh','8':'mu', '999':'ECI2'}
rootdir='/Users/amyskerry/Desktop/eci2data/'
files=os.listdir(rootdir)
with open (rootdir + 'ECI_kid_output.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    toprow=['subjid', 'stimset', 'counterbalance_cond', 'stimfile', 'condition','condition_name', 'response', 'RT']
    writer.writerow(toprow)
    alldata=[]
    for myfile in files:
        if myfile[-3:]=='mat':
            subject = scipy.io.loadmat(rootdir + myfile)
            subjid=list(subject['subjID'])[0]
            stimnames=[stim.rsplit('/',1)[1] for stim in subject['stimList']]
            stimset=list(subject['stimset'])[0]
            cbcond=list(subject['cbcond'])[0]
            conditionlist=[list(element)[0] for element in list(subject['conditionList'])]
            conditionnames=[conditionmapping[str(element)] for element in conditionlist]
            response=[list(element)[0] for element in list(subject['key'])]
            RT=[list(element)[0] for element in list(subject['RT'])]
            for stimn, stim in enumerate(stimnames):            
                thisrow=[subjid, stimset, cbcond, stim, conditionlist[stimn], conditionnames[stimn], response[stimn], RT[stimn]]
                alldata.append(thisrow)
                writer.writerow(thisrow)

with open (rootdir + 'ECI_kid_output_summary.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    toprow=['subjid', 'counterbalance_cond', 'stimfile','sh','su','nh','nu','fh','fu','mh','mu']
    writer.writerow(toprow)
    subjectlist=[row[0] for row in alldata]
    subjectlist=list(set(subjectlist))
    print subjectlist
    allsubjects=[]
    allsubjectsdeets=[]
    for subjectn,subject in enumerate(subjectlist):
        deets=0
        subjectvals=[[],[],[],[],[],[],[],[]]
        for row in alldata:
            cond=row[4]
            if cond !=999:
                if row[0]==subject:
                    subjectdeets=[row[0], row[2], row[3]]
                    subjectvals[int(cond)-1].append(row[6])
                    if deets==0:
                        allsubjectsdeets.append(subjectdeets)
                        print allsubjectsdeets
                        deets=1
        allsubjects.append([np.mean(val) for val in subjectvals])
        
        row=list(allsubjectsdeets[subjectn])
        row.extend(allsubjects[subjectn])
        print row
        writer.writerow(row)
            
                
                    
    
    
#6 different trial scores
#3differenc scores
#1general score
#4 eci trial scores
#age
#gender                
