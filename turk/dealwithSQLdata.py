# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 11:08:35 2013

@author: amyskerry
"""
import csv
import aeslazy as asl
import numpy as np
from itertools import *
import matplotlib.pyplot as plt
import seaborn as sns

#define these once for the study/database
global ratingvects_list,timingvects_list,subIDs_list,run_list,cb_list,dim_list,final_list,err_list,cutshort_list,allmyvars,vardict,labeldict,inclusioncol,timingcol,datacols

datafile='/Users/amyskerry/tempdl.csv'
writedir='/Users/amyskerry/Dropbox/fsfcsvs/'
writename='turkdata.csv'
base='FSF'
ratingvects_list=[]#make one for each var of interest
timingvects_list=[]#make one for each var of interest
subIDs_list=[]
run_list=[] #what batch/run?
cb_list=[] #counterbalancing condition
dim_list=[] #what dimension were they rating?
final_list=[] # last value (how late in movie did they get? should be close to 500s)
err_list=[] # had negative values (obvious code fuckup)
cutshort_list=[] # didn't watch whole thing (could be code ore laziness)
allmyvars=[subIDs_list,ratingvects_list, timingvects_list, run_list, cb_list, dim_list, final_list, err_list, cutshort_list]
vardict=dict(subIDs=subIDs_list, ratingvects=ratingvects_list, timingvects=timingvects_list, batch=run_list, cb=cb_list, dim=dim_list, err=err_list, final=final_list, cutshort=cutshort_list)# perhaps confusingly using same names for list vars and for dict keywords...
labeldict=dict(subIDs='subjid', ratingvects='rating1', timingvects='timing1', batch='run', cb='counterbalance', dim='dimension')# perhaps confusingly using same names for list vars and for dict keywords...
inclusioncol='submitdate'
timingcol='timing1'
datacols={'rate':'rating1','time':'timing1'}
videodict={'r1a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r1b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r2a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r2b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r3a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r3b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r4a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r4b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r5a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r5b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r6a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r6b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r7a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r7b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r8a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r8b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130]}
videonames={'r1':['a1.mp4','b1.mp4','c1.mp4','d1.mp4'], 'r2':['a2.mp4','b2.mp4','c2.mp4','d2.mp4'], 'r3':['a3.mp4','b3.mp4','c3.mp4','d3.mp4'], 'r4':['a4.mp4','b4.mp4','c4.mp4','d4.mp4']}

## the stuff
def extractdata(thefile):
    count=0
    returnvars=[]
    returnheadings=[]
    with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                sqlnames=row
                ratenum=sqlnames.index(datacols['rate'])
                print 'varnames in sql: '+str(sqlnames)
                incindex=sqlnames.index(inclusioncol)
            else:
                subjdata=row
                if subjdata[incindex] != 'NULL':
                    sqlvarname=datacols['rate']
                    thisline=subjdata[ratenum]  
                    thisline=thisline.replace('!!', '!')
                    thisline=thisline.split('!')
                    reducedline=[] 
                    removedindices=[]
                        #thisline=map(lambda x:asl.makeint(x), thisline)
                    for nel,el in enumerate(thisline):
                        try:
                            reducedline.append(float(el))
                        except:
                            removedindices.append(nel)
                            pass
                    thisline=reducedline
                    vardict['ratingvects'].append(thisline)
                    for vnum,sqlvarname in enumerate(sqlnames):
                        #print sqlvarname
                        varlabel=[]
                        for var in labeldict:
                            if sqlvarname==labeldict[var]:
                                varlabel=var
                                #print varlabel
                        #find key corresponding to sqlvarname value in labeldict (call it varabel)
                        if varlabel and sqlvarname!=datacols['rate']: # if you found this sql variable in labeldict
                            thisline=subjdata[vnum]
                            thisline=thisline.replace('!!', '!')
                            thisline=thisline.split('!')
                        
                            if sqlvarname==datacols['time']:
                                for tp in removedindices:                                    
                                    try:
                                        thisline.pop(tp)
                                    except:
                                        pass
                                try:
                                    final=float(thisline[-1])
                                except:
                                    final= float(thisline[-2])   
                                final_list.append(final)
                                cutshort_list.append(int(final>400 and final<512)) #1 if full length, 0 if cut short
                                check=sum(map(lambda x:x<0, thisline))                             
                                if check:
                                    err_list.append(0) #err_list=1 if keeper, 0 if has negatives
                                else:
                                    err_list.append(1)
                            vardict[varlabel].append(thisline)
                    count +=1               
    return vardict, removedindices
    
def checkmatches(times,rates):
    match=[] 
    for n,t in enumerate(times): 
        if len(t)!=len(rates[n]):
            #print str(n)+': mismatch'
            match.append(0)
        else:
            #print str(n)+': match'
            match.append(1)
    return match
    
def timecourseit(timingdata,ratingdata,datadict):
    newtiming=[]
    newrating=[]
    for nt,t in enumerate(timingdata):
        newrating.append([])
        newtiming.append([])
        if datadict['use'][nt]:
            tdataindex=0
            ctv=0
            crv=0
            for tp in asl.floatrange(0,513,.1):
                if tp<=ctv:
                    newtiming[nt].append(tp)
                    newrating[nt].append(crv)
                else:
                    crv=int(ratingdata[nt][tdataindex]) #crv is one behind because value shouldn't change until next timepoint (crt)                
                    if tdataindex<len(t)-1:
                        tdataindex+=1
                    ctv=float(t[tdataindex]) 
                    newtiming[nt].append(tp)
                    newrating[nt].append(crv)
        else:
            newtiming[nt].append(0.0)
            newrating[nt].append(0)
        #print len(newrating[n])
        #print len(newtiming[n])
    #if len(newrating[nt])!=5131:
        #print 'error'
    return newtiming, newrating
    
def getintervalratings(begin,end, time,rate):
    #print time
    startindex=time.index(begin)
    stopindex=time.index(stop)
    #print startindex, stopindex
    ratings=rate[startindex:stopindex]
    return ratings
    
#do the stuff
[data,excludedtps]=extractdata(datafile)

timings=data['timingvects']
ratings=data['ratingvects']

data['match']=checkmatches(timings,ratings)
data['use']=list(np.array(data['err'])*np.array(data['match'])*np.array(data['cutshort']))
[data['REALTIME'],data['REALRATE']]=timecourseit(timings,ratings,data)


goods=asl.allindices(data['use'], 'element>0')
dimlist=list(np.unique(np.array(data['dim'])))
cblist=list(np.unique(np.array(data['cb'])))
runlist=list(np.unique(np.array(data['batch'])))
gr=[]
gt=[]
cbblank=[]
for cb in cblist:
    cbblank.append([])
rblank=[]
for r in runlist:
    rblank.append(cbblank)
dblank=[]
for d in dimlist:
    dblank.append(rblank)
gr=dblank
gt=dblank
numver=len(cblist)*len(runlist)*len(dimlist)


###
names=data['subIDs']
stimtypes=map(lambda x:x[0][0:10], names)
stims=[]
for s in stimtypes:
    new_s=s.replace('a_','x_')
    new_s=new_s.replace('b_','x_')
    #print new_s
    stims.append(new_s)
data['stimtypes']=stims
stimlist=set(stims)
stimlist=list(stimlist)
#print stimlist
#print len(stimlist)
useratings=[]
for s in stimlist:
    useratings.append([[],[],[],[]]) #for the 4 videos
#print useratings
###

#print users
for subject,keep in enumerate(data['use']):
    if keep:
        run=data['batch'][subject][0]
        dim=data['dim'][subject][0]
        cb=data['cb'][subject][0]
        key='r'+run+cb+'_timing'
        stimname=base+'_r'+run+'x_'+dim
        stimindex=stimlist.index(stimname)
        ##print stimindex
        #print len(useratings)
        times=videodict[key]
        #print times
        interval=[]
        ratingsininterval=[]
        for i in range(0,8,2):
            interval=[]
            start=round(times[i],1)
            stop=round(times[i+1],1)
            interval=getintervalratings(start,stop, data['REALTIME'][subject],data['REALRATE'][subject])
            useratings[stimindex][i/2].append(interval)            
            ratingsininterval.append(interval)
        #useratings[stimindex].append(ratingsininterval)
        thisrow=[data['subIDs'][subject],data['batch'][subject],data['cb'][subject],data['dim'][subject],ratingsininterval[0],ratingsininterval[1],ratingsininterval[2],ratingsininterval[3]]
        df=writedir+writename
        with open(df, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(thisrow)
            
#to make some plots     
for movnum,movset in enumerate(useratings):
    if movnum<10:
        #f, axarr= plt.subplots(4, 1)
        temp=1        
        for i in range(4):
            #ax=axarr[i]
            y=[]
            if len(movset[i])>1:
                #f=plt.figure()
                #sns.tsplot(movset[i])
                temp=1
            for ny,y in enumerate(movset[i]):
                x=arange(len(y))
                #ax.plot(x,y)
        plt.show()
#colors=['indianred', 'darkseagreen', 'stealblue', 'cornflowerblue', ]
colors= sns.color_palette("Dark2", len(dimlist))        
for run in runlist:
    rundata=[]
    thestring='element==[\''+run+'\']'
    runindices=asl.allindices(data['batch'], thestring)  
    f, axarr= plt.subplots(4, 1, sharex='all', figsize=[17,10]) 
    for i in range(0,8,2):   
        plt.subplot(axarr[i/2])
        plotdata=[]
        dimlabels=[]
        for dn, dimension in enumerate(dimlist):
            thestring='element==[\''+dimension +'\']'
            dimindices=asl.allindices(data['dim'], thestring)
            subjintervals=[]
            plotcolor=colors[dn]
            subjcount=0
            for subjn, goodsubj in enumerate(data['use']): 
                if subjn in runindices and subjn in dimindices and subjn in goods:
                    subjcount+=1
                    start=round(times[i],1)
                    stop=round(times[i+1],1)
                    thisinterval=getintervalratings(start,stop, data['REALTIME'][subjn],data['REALRATE'][subjn])
                    #print len(thisinterval)
                    subjintervals.append(thisinterval)
                    sns.tsplot(subjintervals, color=plotcolor)
            dimlabels.append(dimension +' : '+ str(subjcount)+ 'subjs')
        dimboxes=[]
        current_palette = sns.color_palette()
        for nd, d in enumerate(dimlist):
            rec=Rectangle((0, 0), 1, 1, color=current_palette[nd])
            dimboxes.append(rec)
        if i==0:
            plt.title('Timecourses: Run '+str(run))
            figlegend(dimboxes, dimlabels, loc='upper right')
    figname=writedir+'fig_run'+str(run)+'_'+str(subjcount)+'subjs.pdf'            
    plt.savefig(figname)
    sns.axlabel('time (seconds)', '')
        
                    
            
        
        
#ll=[]
#ll=[goods,[],[],[]]
#for dn, dimension in enumerate(dimlist):
#    ll.pop(1)
#    dimindices=asl.allindices(data['dim'], 'element==[\''+dimension+'\']')
#    ll.insert(1,dimindices)
#    #print dimindices
#    for rn, r in enumerate(runlist):
#        ll.pop(2)
#        rindices=asl.allindices(data['batch'], 'element==[\''+r+'\']')
#        ll.insert(2,rindices)
#        for cbvn, cbv in enumerate(cblist):
#            ll.pop(3)
#            cbindices=asl.allindices(data['cb'], 'element==[\''+cbv+'\']')
#            ll.insert(3,cbindices)
#            intset=set(ll[0])
#            for nl,l in enumerate(ll):
#                intset=intset.intersection(l)            
#            print dimension + ', '+r+', '+ cbv
#            print intset
#            #print s=list(s)
#            thisgr=[]
#            thisgt=[]
#            if intset:
#                for subj in intset:
#                    thisgr.append(data['REALRATE'][subj])
#                    thisgt.append(data['REALTIME'][subj])
#
#                gr[dn][rn][cbvn]=thisgr
#                #print thisgr
#                #gt[dn][rn][cbvn]=thisgt
#   
#    #f, axarr= plt.subplots(len(cblist), len(runlist), sharex=True, sharey=True)
#    #figsubs=plt.figure() 
#    #fig=plt.figure()
#    thisdimension=gr[dn]
#    #sns.tsplot([1,2,3,4,5,4,3,2,3,4,5,6,5,4,3,23,4,5,6,7,8,9,8,7])
#    count=0
#    for nr,r in enumerate(thisdimension):
#        for nc, c in enumerate(r):
#            thesedata=thisdimension[nr][nc]
#            count=count+1
#            #y=[1,2,3,4,5,4,3,2,3]
#            #x=arange(len(y))
#            #axarr[nc,rn].plot(x,y)
#            if thesedata:
#                print '!'       
#                #axarr[nc,nr]=plot(range(len(thesedata)),thesedata)
#                #ax=fig.add_subplot(111)
#                #ax.sns.tsplot(np.array([1,2,3,4,5,4,3,2,3,4,5,6,5,4,3,23,4,5,6,7,8,9,8,7])*2)
#    #plt.savefig(dimension+'.pdf')
#            
    
                        

                
    
