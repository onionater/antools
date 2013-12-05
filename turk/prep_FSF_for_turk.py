# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 10:49:24 2013

@author: amyskerry
"""

from prepforturk import *

### set parameters for constructing subjIDs (this should be all you need to chance)
rootdir='/Users/amyskerry/Dropbox/fsfcsvs/'
slistfile='slist.py'
slistnames=['subjects', 'keycodes']#list of the variables you want in .py file 
variablenames=['subjID', 'keycode']# list of the variables you want in turk columns
completed=[] # if you already have subjects in this batch (e.g. are reposting), enter them here 
base='FSF'
conds=['fa', 'ob', 'sc', 'me', 'so', 'ph'] #rating condiions
numhitpercond=4 # number of hits you want for each individal counterbalancing/condition combo
batchlabels4turk=['BLUE', 'GREEN', 'YELLOW', 'ORANGE', 'RED', 'PURPLE', 'TEAL', 'GRAY']
# these are the distinct batches (corresponding to runs in FSF)
cbvers=2
#####


# make csv file for each batch, and one list list for each variable to post to server
varlist=[]
for var in variablenames:
    varlist.append([])
for batchnum,batch in enumerate(batchlabels4turk):
    batchfile=rootdir+base+'_'+str(batchnum+1)+batch+'.csv'
    variables=makethestuff(base,conds,numhitpercond,cbvers,batchnum)
    maketurkcsv(completed,variablenames,variables,batchfile)
    for n,var in enumerate(variables):
        for v in var:
            varlist[n].append(v)

#make the .py to post to server  
pyfile = open(slistfile, 'wb')
for n,names in enumerate(slistnames):
    thevarstring=names+'='+ str(varlist[n])
    pyfile.write(thevarstring)
    pyfile.write('\n')
pyfile.close()