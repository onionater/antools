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
import scipy.io
import time

#define these once for the study/database
### this step shouldn't really matter
global ratingvects_list,timingvects_list,subIDs_list,run_list,cb_list,dim_list,final_list,err_list,cutshort_list,allmyvars,vardict,labeldict,inclusioncol,timingcol,datacols, timemax, countunit,plot,RTlag,shiftforRTlag

#some parameters
plot=1 #we don't need images right now
datafile='/Users/amyskerry/tempdl.csv'
writedir='/Users/amyskerry/Dropbox/fsfcsvs/'
writename='turkdata.csv'
regname='_regressors.mat'
base='FSF'
rawOrnormed_binarized='raw'
rawOrnormed_plot='raw'
binthresh=5
propthresh=.5
TRprop=.5 #more than haf the TR meeting thresh means TR is classified as win
TR=2
shiftforRTlag=1 #shift the timevector back by RTlag to account for RT in human rating of stimuli
RTlag=.75
timemax=513
countunit=.1
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
videodict={'r1a_timing': [10.0,130.0,137.05,257.05,264.1,384.1,391.20,511.20],'r1b_timing': [391.2,511.2,264.0,384.0,137.05,257.05,10.0,130.0],'r2a_timing': [10.0,130.0,137.3,257.3,264.3,384.3,391.5,511.5],'r2b_timing': [391.3,511.3,264.05,384.05,137.12,257.12,10.0,130.0],'r3a_timing': [10.0,130.0,137.12,257.12,264.15,384.15,391.3,511.3],'r3b_timing': [391.2,511.2,264.05,384.05,137.05,257.05,10.0,130.0],'r4a_timing': [10.0,130.0,137.05,257.05,264.0,384.0,391.15,511.15],'r4b_timing': [391.1,511.1,264.0,384.0,137.05,257.05,10.0,130.0],'r5a_timing': [10.0,130.0,137.05,257.05,264.25,384.25,391.5,511.5],'r5b_timing': [391.5,511.5,264.1,384.1,137.05,257.05,10.0,130.0],'r6a_timing': [10.0,130.0,137.05,257.05,264.25,384.25,391.52,511.52],'r6b_timing': [391.45,511.45,264.1,384.1,137.0,257.0,10.0,130.0],'r7a_timing': [10.0,130.0,137.05,257.05,264.05,384.05,390.75,510.75],'r7b_timing': [390.73,510.73,263.75,383.75,137.05,257.05,10.0,130.0],'r8a_timing': [10.0,130.0,137.05,257.05,264.05,384.05,392.23,512.23],'r8b_timing': [389.66,509.66,263.75,383.75,137.05,257.05,10.0,130.0]}
videonames={'r1':['FSF_03','FSF_22','FSF_30','FSF_45'], 'r2':['FSF_10','FSF_28','FSF_40','FSF_41'], 'r3':['FSF_16','FSF_36','FSF_37','FSF_42'], 'r4':['FSF_13','FSF_32','FSF_35','FSF_46'],'r5':['FSF_11','FSF_14','FSF_15','FSF_48'],'r6':['FSF_01','FSF_07','FSF_08','FSF_21'],'r7':['FSF_05','FSF_51','FSF_26','FSF_29'],'r8':['FSF_12','FSF_24','FSF_31','FSF_53']}
#when updating, dont make these be .mp4
numvidsperrun=4

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
                            removedindices.append(nel)#if nota float, assume its a pause and remove
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
        if len(t)!=len(rates[n]) or float(max(rates[n]))==0.0:
            #print str(n)+': mismatch'
            match.append(0)
        else:
            #print str(n)+': match'
            match.append(1)
    return match
def buildtimings(t,ratingdata):
    vector=np.arange(0,timemax,countunit)
    v=len(vector)
    rating=np.zeros([v,1])
    timing=np.zeros([v,1])
    normedrating=np.zeros([v,1])
    tdataindex=0
    ctv=0
    crv=0
    stop=len(t)-1
    for tpn, tp in enumerate(np.arange(0,timemax,countunit)):
        tp=round(tp,1)
        if tp<=ctv:
            timing[tpn]=tp
            rating[tpn]=crv
        else:
            crv=float(ratingdata[tdataindex]) #crv is one behind because value shouldn't change until next timepoint (crt)                
            if tdataindex<stop:
                tdataindex+=1
            ctv=float(t[tdataindex]) 
            timing[tpn]=tp
            rating[tpn]=crv
    timing=list(timing.T[0])
    rating=list(rating.T[0])
    return timing, rating 
def normalizerating(rat):
       # rat=np.array(rat)
    ratmean=np.mean(rat)
    ratstd=np.std(rat)
    n=[(x-ratmean)/ratstd for x in rat]
    return n
    
def timecourseit(timingdata,ratingdata,datadict):
    global unit
    unit=countunit
    chop=int(RTlag/countunit)
    newtiming=[]
    newrating=[]
    normednewrating=[]
    for nt,t in enumerate(timingdata):
        if datadict['use'][nt]:
            timing, rating=buildtimings(t, ratingdata[nt])
            rating=reshape(rating,[len(rating),])
            #timing=reshape(timing,[len(timing),])
            if shiftforRTlag:
                extra=np.zeros(chop)+rating[-1] #we will assume that the last RTlag seconds are the same as the last response
                rating=np.concatenate([rating,extra])
                rating=rating[chop:]
            newtiming.append(timing)
            newrating.append(rating)
        else:
            newtiming.append(0)
            newrating.append(0)
    print "raw timecourses made: " + time.strftime("%Y-%m-%d-%h-%m-%s")    
    for rat in newrating:   
        if type(rat)==int:
            normednewrating.append(0)
        else:
            normednewrating.append(normalizerating(rat))  
    print "normed timecourses made: " + time.strftime("%Y-%m-%d-%h-%m-%s")  
    return newtiming, newrating, normednewrating
    
def getintervalratings(begin,end, time,rate):
    startindex=time.index(begin)
    stopindex=time.index(end)
    ratings=rate[startindex:stopindex]
    return ratings
    

def writeRatings2csv(filename,stims,datadict):
    #write data to csv file in appropriate format
    ## this is where we will store the timecourese for each video in each run/dimension
    useratings=[]
    normeduseratings=[]
    for s in stims:
        useratings.append([[],[],[],[]]) #for the 4 videos
        normeduseratings.append([[],[],[],[]]) #for the 4 videos
    df=writedir+filename
    with open(df, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for subject,keep in enumerate(datadict['use']):
            if keep:
                run=datadict['batch'][subject][0]
                dim=datadict['dim'][subject][0]
                cb=datadict['cb'][subject][0]
                key='r'+run+cb+'_timing'
                stimname=base+'_r'+run+'x_'+dim
                stimindex=stims.index(stimname)
                times=videodict[key]
                interval=[]
                normedinterval=[]
                ratingsininterval=[]
                normedratingsininterval=[]
                for i in range(0,8,2):
                    interval=[]
                    start=round(times[i],1)
                    stop=round(times[i+1],1)
                    interval=getintervalratings(start,stop, datadict['REALTIME'][subject],datadict['REALRATE'][subject])
                    normedinterval=getintervalratings(start,stop, datadict['REALTIME'][subject],datadict['NORMEDRATE'][subject])
                    useratings[stimindex][i/2].append(interval)   
                    normeduseratings[stimindex][i/2].append(normedinterval)
                    ratingsininterval.append(interval)
                    normedratingsininterval.append(normedinterval)
                #useratings[stimindex].append(ratingsininterval)
                thisrow=[datadict['subIDs'][subject][0],datadict['batch'][subject][0],datadict['cb'][subject][0],datadict['dim'][subject][0],ratingsininterval[0], ratingsininterval[1],ratingsininterval[2], ratingsininterval[3],normedratingsininterval[0], normedratingsininterval[1],normedratingsininterval[2],normedratingsininterval[3]]
                writer.writerow(thisrow)

def makeplots(datadict,useablesubjects,dimensionlist,*args, **kwargs):
    #to make some plots (one fig per run, 4 subplots-- one for each video. all dimensions on single plot)
    #colors=['indianred', 'darkseagreen', 'stealblue', 'cornflowerblue', ]  
    colors= sns.color_palette("hls", len(dimensionlist)) #default color scheme
    raw=1 # default to raw ratings
    if 'colors' in kwargs.keys():
        colors= sns.color_palette(kwargs['colors'], len(dimensionlist))
    if 'normed' in args:
        raw=0
    subtally={}
    avgR={}
   # subtally={'cbblindkey':[]}
    #avgRsq={'cbblindkey':[]}                 
    for run in runlist:
        thestring='element==[\''+run+'\']'
        runindices=asl.allindices(datadict['batch'], thestring) 
        if plot:
            f, axarr= plt.subplots(4, 1, sharex='all', figsize=[17,10])  #seperate fig foreach run
        for i in range(0,8,2): 
            if plot:
                plt.subplot(axarr[i/2])
            dimlabels=[]
            dimboxes=[]
            for dn, dimension in enumerate(dimensionlist):
                thestring='element==[\''+dimension +'\']'
                dimindices=asl.allindices(datadict['dim'], thestring)
                subjintervals=[]
                plotcolor=colors[dn]
                subjcount=0
                for subjn, goodsubj in enumerate(datadict['use']): 
                    cb=datadict['cb'][subjn][0]
                    key='r'+run+cb+'_timing'
                    cbblindkey='r'+run+'x_v'+str(i/2+1)+'_'+ dimension+'_timing'
                    times=videodict[key]
                    if subjn in runindices and subjn in dimindices and goodsubj:
                        subjcount+=1
                        start=round(times[i],1)
                        stop=round(times[i+1],1)
                        if raw:
                            thisinterval=getintervalratings(start,stop, datadict['REALTIME'][subjn],datadict['REALRATE'][subjn])
                            label='raw'
                        else:
                            thisinterval=getintervalratings(start,stop, datadict['REALTIME'][subjn],datadict['NORMEDRATE'][subjn])
                            label='normed'
#                        if np.mean(thisinterval)==0.0:
#                            print str(subjn)
#                            print "subjs: "+str(np.mean(thisinterval))
                        subjintervals.append(thisinterval)
                if plot:
                    rec=plt.Rectangle((0, 0), 1, 1, color=plotcolor)
                    dimboxes.append(rec)
                dimlabels.append(dimension +' : '+ str(subjcount)+ 'subjs')
                subtally[cbblindkey]=subjcount
                avgR[cbblindkey]=asl.pairwisecorrel(subjintervals,1)
                #print [len(x) for x in subjintervals]
                if subjintervals and plot:
                    sns.tsplot(subjintervals, color=plotcolor)
                    rec=plt.Rectangle((0, 0), 1, 1, color=plotcolor)
            if i==0 and plot:
                plt.title('Timecourses: Run '+str(run))
                plt.figlegend(dimboxes, dimlabels, loc='upper right')
        if plot:
            figname=writedir+'fig_run'+str(run)+'_'+label+'.pdf'            
            sns.axlabel('time (.1 sec increments)', '')
            plt.savefig(figname)
    return subtally, avgR
        
def makestimaverages(datadict,useablesubjects,dimensionlist,stims, *args):
    allavgs=[]
    for s in stims:
        allavgs.append([])
    raw=1 # default to raw ratings
    if 'normed' in args:
        raw=0                   
    for run in runlist:
        thestring='element==[\''+run+'\']'
        runindices=asl.allindices(datadict['batch'], thestring)  
        for i in range(0,8,2):   
            for dn, dimension in enumerate(dimensionlist):
                thestring='element==[\''+dimension +'\']'
                dimindices=asl.allindices(datadict['dim'], thestring)
                stimname=base+'_r'+run+'x_'+dimension+'_vid'+str(i/2+1)
                try:
                    vidindex=stims.index(stimname)
                except:
                    pass
                theseintervals=[]
                for subjn, goodsubj in enumerate(datadict['use']): 
                    cb=datadict['cb'][subjn][0]
                    key='r'+run+cb+'_timing'
                    times=videodict[key]
                    if subjn in runindices and subjn in dimindices and subjn in useablesubjects:
                        start=round(times[i],1)
                        stop=round(times[i+1],1)
                        if raw:
                            thisinterval=getintervalratings(start,stop, datadict['REALTIME'][subjn],datadict['REALRATE'][subjn])
                        else:
                            thisinterval=getintervalratings(start,stop, datadict['REALTIME'][subjn],datadict['NORMEDRATE'][subjn])
                        theseintervals.append(thisinterval)
                if theseintervals:        
                    average=list(np.mean(theseintervals,0))
                    allavgs[vidindex].append(average)
    return allavgs

#this function needs to be written
def condenseregressors(reg,countT,tr, TRprop, binary):
    allcondensed=[]    
    for thisreg in reg:
        condensefactor=tr/countT
        condensed=[]
        if len(thisreg)>0:
            for stepi in asl.floatrange(0,len(thisreg),condensefactor):
                #print i
                stepi=int(stepi)
                thisbit=thisreg[stepi:int(stepi+condensefactor)]
                winners=[i for i, element in enumerate(thisbit) if element>0]
                if len(thisbit)>0:
                    if binary:
                        if len(winners)/len(thisbit):
                            condensed.append(1)
                        else:
                            condensed.append(0)
                    else:
                        condensed.append(np.mean(thisbit))
            if len(thisreg)-int(stepi+condensefactor) !=0:
                print 'error: video/TR mismatch'
            allcondensed.append(condensed)
        else:
            allcondensed.append([])
            
    return allcondensed
    
def binarizeregs(stimdata, **kwargs):
    if len(stimdata)>0:
        stimdata=stimdata[0]
    thresh=5
    if 'thresh' in kwargs.keys():
        thresh=kwargs['thresh']
    binarized=[]
    for rating in stimdata:
        binrate=int(rating>thresh)
        binarized.append(binrate)
    return binarized

def printvismatrix(dims, condensed):
    sns.set(style="nogrid")
    allvectors=[]
    for dim in dims:
        print dim
        dimvector=[]
        for batch in runlist:
            for ii in range(4):
                video=videonames['r'+batch][ii]
                filekey=dim+'_'+video
                stimindex=filenamelist.index(filekey)
                vector=condensed[stimindex]
                #print len(vector)
                if len(vector)==60:
                    for x in vector:
                        dimvector.append(float(x))
                else:
                    for x in range(60):
                        dimvector.append(0.0)
        for xx in range(100):                
            allvectors.append(dimvector)
    f,ax=plt.subplots(1)
    imshow(allvectors)
    #dims.insert(0,'')
    yticks=range(50,len(dims)*100+50,100)
    print yticks
    ax.set_yticks(yticks)
    ax.set_yticklabels(dims)
    plt.sca(ax)
    plt.savefig([writedir+'visualizetimecourse.pdf'])

print "start: " + time.strftime("%Y-%m-%d-%h-%m-%s")

### do the thingss    
##get your data dict
[data,excludedtps]=extractdata(datafile)
print "data extracted: " + time.strftime("%Y-%m-%d-%h-%m-%s")
##reorganize to be in binned timecourses rather than lists of rate changes
timings=data['timingvects']
ratings=data['ratingvects']
data['match']=checkmatches(timings,ratings)
data['use']=list(np.array(data['err'])*np.array(data['match'])*np.array(data['cutshort'])) #find the good ones
print "data filtered: " + time.strftime("%Y-%m-%d-%h-%m-%s")
[data['REALTIME'],data['REALRATE'],data['NORMEDRATE']]=timecourseit(timings,ratings,data)
print "timecourses made: " + time.strftime("%Y-%m-%d-%h-%m-%s")
#for vidn, vid in enumerate(data['REALRATE']):
#    if data['use'][vidn]:
#        print 'data: ' + str(np.mean(vid))

goods=asl.allindices(data['use'], 'element>0') #indices of your good subjects
print "goods defined: " + time.strftime("%Y-%m-%d-%h-%m-%s")
dimlist=list(np.unique(np.array(data['dim'])))
cblist=list(np.unique(np.array(data['cb'])))
runlist=list(np.unique(np.array(data['batch'])))

### write now the naming of subjs contains information about cb order, but that becomes irrelevant in reatime and real rate
names=data['subIDs']
stimtypes=map(lambda x:x[0][0:10], names)
stims=[]
for s in stimtypes:
    new_s=s.replace('a_','x_')
    new_s=new_s.replace('b_','x_')
    stims.append(new_s)
data['stimtypes']=stims ## stimtypes is like subjIDs but only contains condition relevant information (run and dimension)
stimlist=set(stims)
stimlist=list(stimlist)
vidlist=[]
filenamelist=[]
for st in stimlist:
    key=st[len(base)+1:len(base)+3]
    for i in range(4):
        vidlist.append(st+'_vid'+str(i+1))
        filenamelist.append(st[-2:]+ '_'+videonames[key][i])
print "namingdone: " + time.strftime("%Y-%m-%d-%h-%m-%s")

#write data to csv file in appropriate format            
writeRatings2csv(writename,stimlist,data)
print "csv written: " + time.strftime("%Y-%m-%d-%h-%m-%s")
 
#for each video, get average across subjects 
vid_averages=makestimaverages(data,goods,dimlist, vidlist, rawOrnormed_binarized)
print "stims averaged: " + time.strftime("%Y-%m-%d-%h-%m-%s")
binarized=map(binarizeregs, vid_averages)
print "stims binarized: " + time.strftime("%Y-%m-%d-%h-%m-%s")
#vid avgs in weird list of list form. make matrix like for matlab export
currshape=shape(np.array(vid_averages))
newshape=[currshape[0],currshape[2]]
vid_averages=reshape(np.array(vid_averages),newshape)
#condense to TR units
binary_condensed=condenseregressors(binarized, countunit, TR, TRprop, 1) #find length of one of the useable realtimes and condense to TR    
param_condensed=condenseregressors(vid_averages, countunit, TR, TRprop, 0) #find length of one of the useable realtimes and condense to TR
print "stims condensed: " + time.strftime("%Y-%m-%d-%h-%m-%s")
#to make some plots (one fig per run, 4 subplots-- one for each video. all dimensions on single plot)
[numsubjs, reliabilitycorrs]=makeplots(data,goods,dimlist, rawOrnormed_plot,thresh=binthresh)
print "stims plotsmade: " + time.strftime("%Y-%m-%d-%h-%m-%s")

readme='binarization based threshold of 5, no normalization, shifted by RTlag of .75'
scipy.io.savemat(writedir+rawOrnormed_binarized+regname,{'binarized':binarized,'binary_condensed':binary_condensed, 'param_condensed':param_condensed, 'vidavgs': vid_averages, 'stimnames':vidlist, 'videonames': filenamelist, 'normedOrRaw':rawOrnormed_binarized, 'numsubjsPerStim':numsubjs, 'reliabilityRvals':reliabilitycorrs, 'readme':readme})
print ".mat written: " + time.strftime("%Y-%m-%d-%h-%m-%s")
#param not param and reliablity wrong...

plt.close('all')
if plot:
    printvismatrix(dimlist, binary_condensed)
    print "matrix visualized: " + time.strftime("%Y-%m-%d-%h-%m-%s")

plt.close('all')
           
                    
            