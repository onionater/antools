# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 10:49:24 2013

@author: amyskerry
"""

import prepforturk as prep
import csv
import glob

### set parameters for constructing subjIDs (this should be all you need to change)
rootdir='/Users/amyskerry/Documents/projects/turk/NDE_dim2/'
slistfile=rootdir+'task/appdata/slist.csv'
stimfile=rootdir+'task/appdata/NDE_stims.csv'
completeddir=rootdir+'/completedturk/'
version=1

slistnames=['subjects', 'keycodes']#list of the variables you want in .csv file 
variablenames=['subjID', 'keycode']# list of the variables you want in turk csv columns
completed=[] # if you already have subjects in this batch (e.g. are reposting), enter them here 
completeddirfiles=glob.glob(completeddir+'*')
for thisfile in completeddirfiles:
    with open(thisfile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for rown, row in enumerate(reader):
            if rown==0:
                colnames=row
                subjcolindex=colnames.index('Input.subjID')
            else:
                subjectid=row[subjcolindex]
                completed.eappnd(subjectid)
    
base='Ndim2'
possconds=[]
with open(stimfile, 'rU') as csvfile:
    reader = csv.reader(csvfile)
    for rown, row in enumerate(reader):
        if rown > 0 and rown < 10:
            possconds.append('q00'+str(rown))
        elif rown > 9 and rown < 100:
            possconds.append('q0'+str(rown))
        elif rown > 99:
            possconds.append('q'+str(rown))
numhitpercond=2 # number of hits you want for each individal counterbalancing/condition combo
batchlabels4turk=['GREEN']#, 'GREEN', 'YELLOW', 'ORANGE', 'RED', 'PURPLE', 'TEAL', 'PINK']
#####


# make csv file for each batch, and one list list for each variable to post to server
varlist=[]
for var in variablenames:
        varlist.append([])
conds=possconds
for batchnum, batch in enumerate(batchlabels4turk):
    print batch
    batchfile=rootdir+'turkcsvs/'+base+'_'+batch+'.csv'
    variables=prep.makethestuffrand(base,conds,numhitpercond,version,batchnum)
    print variables
    
    prep.maketurkcsv(completed,variablenames,variables,batchfile)
    for n,var in enumerate(variables):
        for v in var:
            varlist[n].append(v)

#make the .py to post to server  
#subjectfile = open(slistfile, 'wb')
#for n,names in enumerate(slistnames):
#    thevarstring=names+'='+ str(varlist[n])
#    subjectfile.write(thevarstring)
#    subjectfile.write('\n')
#subjectfile.close()

with open(slistfile, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(slistnames)
    rows=zip(*varlist)
    for row in rows:
        writer.writerow(row)