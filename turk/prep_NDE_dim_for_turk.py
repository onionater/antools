# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 10:49:24 2013

@author: amyskerry
"""

from prepforturk import *

### set parameters for constructing subjIDs (this should be all you need to chance)
#rootdir='/Users/amyskerry/Dropbox/fsfcsvs/'
rootdir='/Users/amyskerry/Documents/projects/turk/NDE_dim/'
slistfile='slist.py'
slistnames=['subjects', 'keycodes']#list of the variables you want in .py file 
variablenames=['subjID', 'keycode']# list of the variables you want in turk columns
completed=[] # if you already have subjects in this batch (e.g. are reposting), enter them here 
base='Ndim'
possconds=['q'+str(i) for i in range(1,93)]
possconds.remove('q86')
possconds.remove('q87')
numhitpercond=5 # number of hits you want for each individal counterbalancing/condition combo
batchlabels4turk=['BLUE']#, 'GREEN', 'YELLOW', 'ORANGE', 'RED', 'PURPLE', 'TEAL', 'PINK']
# these are the distinct batches (corresponding to runs in FSF)
cbvers=1
#####


# make csv file for each batch, and one list list for each variable to post to server
varlist=[]
for var in variablenames:
        varlist.append([])
conds=possconds
for batchnum,batch in enumerate(batchlabels4turk):
    print batch
    print batchnum+1
    batchfile=rootdir+'turkcsvs/'+base+'_'+str(batchnum+1)+batch+'.csv'
    variables=makethestuff(base,conds,numhitpercond,cbvers,batchnum)
    print variables
    
    maketurkcsv(completed,variablenames,variables,batchfile)
    for n,var in enumerate(variables):
        for v in var:
            varlist[n].append(v)

conds=possconds

#make the .py to post to server  
pyfile = open(rootdir+slistfile, 'wb')
for n,names in enumerate(slistnames):
    thevarstring=names+'='+ str(varlist[n])
    pyfile.write(thevarstring)
    pyfile.write('\n')
pyfile.close()