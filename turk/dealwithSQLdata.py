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

#define these once for the study/database
### this step shouldn't really matter
global ratingvects_list,timingvects_list,subIDs_list,run_list,cb_list,dim_list,final_list,err_list,cutshort_list,allmyvars,vardict,labeldict,inclusioncol,timingcol,datacols, timemax, countunit

#some parameters
datafile='/Users/amyskerry/tempdl.csv'
writedir='/Users/amyskerry/Dropbox/fsfcsvs/'
writename='turkdata.csv'
regname='_regressors.mat'
base='FSF'
rawOrnormed_binarized='raw'
rawOrnormed_plot='raw'
binthresh=5
propthresh=.5
condensethresh=.9 #using binarized, so anything >0 is a win
TRprop=.5 #more than haf the TR meeting thresh means TR is classified as win
TR=2
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
videodict={'r1a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r1b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r2a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r2b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r3a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r3b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r4a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r4b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r5a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r5b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r6a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r6b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r7a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r7b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130],'r8a_timing': [10.1,130.1,137.05,257.05,264.05,384.05,391.2,511.2],'r8b_timing': [391.2,511.2,263.75,383.75,136.75,256.75,10,130]}
videonames={'r1':['a1.mp4','b1.mp4','c1.mp4','d1.mp4'], 'r2':['a2.mp4','b2.mp4','c2.mp4','d2.mp4'], 'r3':['a3.mp4','b3.mp4','c3.mp4','d3.mp4'], 'r4':['a4.mp4','b4.mp4','c4.mp4','d4.mp4'],'r5':['a5.mp4','b5.mp4','c5.mp4','d5.mp4'],'r6':['a6.mp4','b6.mp4','c6.mp4','d6.mp4'],'r7':['a7.mp4','b7.mp4','c7.mp4','d7.mp4'],'r8':['a8.mp4','b8.mp4','c8.mp4','d8.mp4']}
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
    normednewrating=[]
    for nt,t in enumerate(timingdata):
        newrating.append([])
        newtiming.append([])
        normednewrating.append([])
        if datadict['use'][nt]:
            tdataindex=0
            ctv=0
            crv=0
            for tp in asl.floatrange(0,timemax,countunit):
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
        normalized=map(lambda x:(x-np.mean(newrating[nt]))/np.std(newrating[nt]), np.array(newrating[nt]))
        normednewrating[nt]=normalized      
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
    avgRsq={}
   # subtally={'cbblindkey':[]}
    #avgRsq={'cbblindkey':[]}                 
    for run in runlist:
        thestring='element==[\''+run+'\']'
        runindices=asl.allindices(datadict['batch'], thestring)  
        f, axarr= plt.subplots(4, 1, sharex='all', figsize=[17,10])  #seperate fig foreach run
        for i in range(0,8,2):   
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
                    if subjn in runindices and subjn in dimindices and subjn in useablesubjects:
                        subjcount+=1
                        start=round(times[i],1)
                        stop=round(times[i+1],1)
                        if raw:
                            thisinterval=getintervalratings(start,stop, datadict['REALTIME'][subjn],datadict['REALRATE'][subjn])
                            label='raw'
                        else:
                            thisinterval=getintervalratings(start,stop, datadict['REALTIME'][subjn],datadict['NORMEDRATE'][subjn])
                            label='normed'
                        subjintervals.append(thisinterval)
                rec=plt.Rectangle((0, 0), 1, 1, color=plotcolor)
                dimboxes.append(rec)
                dimlabels.append(dimension +' : '+ str(subjcount)+ 'subjs')
                subtally[cbblindkey]=subjcount
                avgRsq[cbblindkey]=asl.pairwisecorrel(subjintervals)
                if subjintervals:
                    sns.tsplot(subjintervals, color=plotcolor)
                    rec=plt.Rectangle((0, 0), 1, 1, color=plotcolor)
            if i==0:
                plt.title('Timecourses: Run '+str(run))
                plt.figlegend(dimboxes, dimlabels, loc='upper right')
        figname=writedir+'fig_run'+str(run)+'_'+label+'.pdf'            
        sns.axlabel('time (seconds)', '')
        plt.savefig(figname)
    return subtally, avgRsq
        
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
def condenseregressors(reg,countT,tr, condensethresh, TRprop):
    allcondensed=[]    
    for thisreg in reg:
        condensefactor=tr/countT
        condensed=[]
        if thisreg:
            for stepi in asl.floatrange(0,len(thisreg),condensefactor):
                #print i
                stepi=int(stepi)
                thisbit=thisreg[stepi:int(stepi+condensefactor)]
                winners=[i for i, element in enumerate(thisbit) if element>condensethresh]
                if thisbit:
                    if len(winners)/len(thisbit):
                        condensed.append(1)
                    else:
                        condensed.append(0)
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

def printvismatrix(dims):
    sns.set(style="nogrid")
    allvectors=[]
    breakvect=[0, 0, 0, 0, 0, ]
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

### do the things
    
##get your data dict
[data,excludedtps]=extractdata(datafile)

##reorganize to be in binned timecourses rather than lists of rate changes
timings=data['timingvects']
ratings=data['ratingvects']
data['match']=checkmatches(timings,ratings)
data['use']=list(np.array(data['err'])*np.array(data['match'])*np.array(data['cutshort'])) #find the good ones
[data['REALTIME'],data['REALRATE'],data['NORMEDRATE']]=timecourseit(timings,ratings,data)



goods=asl.allindices(data['use'], 'element>0') #indices of your good subjects
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

#write data to csv file in appropriate format            
writeRatings2csv(writename,stimlist,data)
 
#for each video, get average across subjects 
vid_averages=makestimaverages(data,goods,dimlist, vidlist, rawOrnormed_binarized)
binarized=map(binarizeregs, vid_averages)
condensed=condenseregressors(binarized, countunit, TR, condensethresh, TRprop) #find length of one of the useable realtimes and condense to TR    

#to make some plots (one fig per run, 4 subplots-- one for each video. all dimensions on single plot)
[numsubjs, reliablitycorrs]=makeplots(data,goods,dimlist, rawOrnormed_plot,thresh=binthresh)

scipy.io.savemat(writedir+rawOrnormed_binarized+regname,{'binarized':binarized,'condensed':condensed,'vidavgs': vid_averages, 'stimnames':vidlist, 'videonames': filenamelist, 'normedOrRaw':rawOrnormed_binarized, 'numsubjsPerStim':numsubjs, 'reliabilityRsq':reliablitycorrs})

printvismatrix(dimlist)

plt.close('all')
           
                    
            