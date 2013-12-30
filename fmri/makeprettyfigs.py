# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 14:29:03 2013

@author: amyskerry
"""
#makes all the figures for EIB
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec

preferredgrid='darkgrid'
dotsize=12
global scaleplot2range
adjustratios2scale=1
global figargs
figargs=dict(elinewidth=3, markersize=dotsize, fmt='o')
pvalargs=dict(markersize=dotsize/2, marker='$*$', ls='none')
global chance
chance=.5
global alphathresh
alphathresh=.05

#main analysis data
discs=['facial expressions', 'situations', 'abstract']
disccolors=['green', 'blue', 'red']
mainregions=['mmPFC','dmPFC','vmPFC','rpSTC','lpSTC']
accuracies=[[0.532357143,0.528486667,0.520030769,0.517975,0.51840625],[0.548928571,0.562813333,0.527061538,0.5091,0.5051],[0.522762906,0.534813254,0.525217904,0.501570172,0.497651404]]
errors=[[0.013100917,0.017320216,0.012017313,0.006576166,0.009590892],[0.014108179,0.012662039,0.014719486,0.011,0.0132],[0.007245141,0.009919109,0.007965256,0.007063568,0.006624171]]
pvalue=[[0.014071642,0.061144416,0.060707514,0.007696409,0.037098591],[0.002080517,0.000104609,0.045428829,0.2111,0.3513],[0.003896727,0.001733804,0.004064978,0.413542607,0.636068794]]
main_scaler=1.3
mainfigxy=[5,10]
main_const=0

#sec analysis data
discs=['facial  \n expressions', 'situations', 'abstract']
otherregions=['rTPJ', 'PC', 'rTATL']
regiondata=[[0.4949, 0.519125, 0.510275666], [0.5046, 0.5176875, 0.491411979], [0.5094, 0.49396875, 0.510275666]]
regionerr=[[0.0113, 0.016743084, 0.007061238], [0.0128, 0.013888208, 0.009593776], [0.013, 0.012686324, 0.007061238]]
regionpvalue=[[1,1,1],[1,1,1],[1,1,1]]
sec_scaler=1.3
sec_const=0
secfigxy=[5,10]

def makeMainFig(mainfig,ratio,intscale):
    #mainratio=findratio(main_scaler,main_const,accuracies,errors)
    maings = gridspec.GridSpec(3, 1, height_ratios=ratio)
    axisrange=[]
    interval=1 # will be autoadjusted to match across plots
    for sub,d in enumerate(discs):
        plotcolor=disccolors[discs.index(d)]
        i=discs.index(d)
        #mainax=mainaxs[i]
        data=accuracies[i]
        err=errors[i]
        pval=pvalue[i]
        ymax=max(data)+max(err)*main_scaler+ main_const
        ymin=min(data)-max(err)*main_scaler +main_const
        [thisax, axrange,interval,actmax]=makeplot(maings,sub, data,err, mainregions, plotcolor, ymax, ymin, interval, intscale)       
        axisrange.append(axrange)
        thisax.set_title(d)
        pvalarray=check_pvals(actmax-interval*.8, pval,thisax)              
    sns.set(style="nogrid")
    mainax = mainfig.add_subplot(111)
    add_hidden_axis(mainax)
    mainax.set_ylabel('classification accuracy') 
    return mainfig,maings,axisrange

def makeSecFig(secfig,ratio, intscale):
    #secratio=findratio(sec_scaler,sec_const,regiondata,regionerr)
    #print secratio
    #secgs = gridspec.GridSpec(3, 1, height_ratios=secratio)
    secgs = gridspec.GridSpec(3, 1,height_ratios=ratio)
    axisrange=[]
    interval=1 # will be autoadjusted to match across plots
    for sub,region in enumerate(otherregions):
        i=otherregions.index(region)
        data=regiondata[i]
        err=regionerr[i]
        pval=regionpvalue[i]
        #secax = secaxs[i]
        #ax.errorbar(np.arange(len(data)), data, yerr=err, fmt='o', ecolor='g', capthick=2)
        #ymax=max(data)+max(err)+max(err)*2    
        ymax=.55    
        ymin=min(data)-max(err)*sec_scaler+sec_const
        [anotherax,axrange,interval,actmax]=makeplot(secgs, sub, data, err, discs, disccolors, ymax, ymin, interval, intscale)
        #anotherax=output[0]        
        axisrange.append(axrange)
        anotherax.set_title(region)
        pvalarray=check_pvals(actmax-interval*.2, pval,anotherax)
    #hidden plot to get single label    
    sns.set(style="nogrid")
    big_ax = secfig.add_subplot(111)
    add_hidden_axis(big_ax)
    big_ax.set_ylabel('classification accuracy')  
    return secfig,secgs,axisrange

def makeplot(grid,subplot, datavals,errorvals, labels, plotcolor, ymax, ymin, tickinterval, intervalscale):
    
    sizedata=len(datavals)  
    datamatrix=[[0]*sizedata]
    errormatrix=[[0]*sizedata]
    if type(plotcolor)==list:
        #do the things to plot seperate color for each dot
        count=0       
        for el in datavals:
            datamatrix.append([0]*sizedata)
            datamatrix[count][count]=el
            errormatrix.append([0]*sizedata)
            errormatrix[count][count]=errorvals[count]
            count=count+1
        datamatrix=datamatrix[0:-1]
        datavals=datamatrix
        errorvals=errormatrix
    else:
        datavals=[datavals]
        errorvals=[errorvals]
    #axis.errorbar(np.arange(sizedata), datavals, yerr=errorvals, fmt='o', ecolor='g', capthick=2)
    #print datavals
    count=0
    axis = plt.subplot(grid[subplot]) 
    while count<len(datamatrix):
        thisdata=datavals[count]
        thiserror=errorvals[count]
        #print thisdata
        #print thiserror
        axis.errorbar(np.arange(sizedata), thisdata, yerr=thiserror, color=plotcolor[count], **figargs)    
        count=count+1
    axis.locator_params(nbins=sizedata+2)
    xlim_deets=[-.25, sizedata-.75]
    axis.set_xlim(xlim_deets)
    axis.set_ylim([ymin, ymax])
    ticklist=axis.get_yticks()
    tempmin=min(ticklist)
    tempmax=max(ticklist)
    if subplot==0:
        tickinterval=(ticklist[1]-ticklist[0])
    #print tempmin, tempmax
    #print tickinterval/8
    if tempmax-ymax <tickinterval*intervalscale/12:
        tempmax=tempmax+tickinterval*intervalscale
    if ymin-tempmin <tickinterval*intervalscale/12:
        ymin=tempmin-tickinterval*intervalscale
    roundup=mod(round(tempmax,5)/round(tickinterval*intervalscale,5),1)
    ymax=tempmax+roundup*(tickinterval*intervalscale)
    roundup=mod(round(tempmin,5)/round(tickinterval*intervalscale,5),1)
    ymin=tempmin-roundup*(tickinterval*intervalscale)
    axis.set_ylim(ymin,ymax)#so that it always goes above the tick line
    axisrange=ymax-ymin
    axis.set_yticks(np.arange(ymin, ymax*1.01, tickinterval*intervalscale))
    numInGrid=grid.get_geometry()[0]
    #axis.set_xticklabels('none')  
    vis=False
    if subplot==numInGrid-1:
        vis=True
    axis.set_xticklabels(labels, visible=vis)
    axis.plot(xlim_deets, [chance,chance], ls='dashed', color='orange')
    return axis, axisrange, tickinterval, ymax
    
def add_hidden_axis(hidax):
    sns.set(style="nogrid")
    hidax.set_axis_bgcolor('none')
    hidax.spines['bottom'].set_color('none')
    hidax.spines['top'].set_color('none') 
    hidax.spines['right'].set_color('none')
    hidax.spines['left'].set_color('none')
    hidax.locator_params(color='none')
    hidax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    sns.set(style=preferredgrid)
    return hidax

def define_axis_limits(data,err,scaler,const):
    ymax=max(data)+max(err)*scaler+const
    ymin=min(data)-max(err)*scaler+const
    return ymax, ymin
    
def check_pvals(height,pvals,axis):
    pvalsymbol=[]
    pvalx=[]
    pvalheight=[]
    for i, pv in enumerate(pvals):
        if pv<alphathresh:
            pvalsymbol.append('*')
            pvalx.append(i)
            pvalheight.append(height)
    axis.errorbar(pvalx, pvalheight, **pvalargs)          
    print pvalheight
    return pvalx, pvalsymbol, pvalheight

def findratio(scaler, constant, acc, errors):
    numel=len(acc)    
    thesemaxes=[]
    thesemins=[]  
    thesedifs=[]
    for i,data in enumerate(acc):
        err=errors[i]
        thesemaxes.append(define_axis_limits(data,err,scaler,constant)[0])
        thesemins.append(define_axis_limits(data,err,scaler,constant)[1])
        thesedifs.append(define_axis_limits(data,err,scaler,constant)[0]-define_axis_limits(data,err,scaler,constant)[1])
    #print thesemaxes, thesemins, thesedifs
    if scaleplot2range:    
        dif=np.array(thesedifs)
        total=sum(dif)    
        ratio=dif/total
    else: 
        ratio=dif/dif
    return ratio
    
###Main Analysis    
mainfig = plt.figure(figsize=mainfigxy)
mainregions.insert(0,'0')
intscale=2
[mainfig,maings,axisrange]=makeMainFig(mainfig,[1,1,1], intscale)
if adjustratios2scale:
    plt.close(mainfig)
    mainfig = plt.figure(figsize=mainfigxy)
    [mainfig,maings,axisrange]=makeMainFig(mainfig,axisrange, intscale)
    #print maings.get_height_ratios()
plt.savefig('mainrois.pdf')

###Other region analysis
secfig = plt.figure(figsize=secfigxy)
discs.insert(0,'0')
intscale=1
[secfig,secgs,axisrange]=makeSecFig(secfig,[1,1,1], intscale)
if adjustratios2scale:
    plt.close(secfig)
    secfig = plt.figure(figsize=secfigxy)
    [secfig,secgs,axisrange]=makeSecFig(secfig,axisrange, intscale)
    #print secgs.get_height_ratios()

plt.savefig('otherrois.pdf')
#plt.close('all')


##otheranals
#tom
means=[[0.0416875,-0.15301875,	0.10955,	-0.127971875	,-0.162084375],[0.052053125,	-0.1816625,	0.12475,	-0.170734375	,-0.15685625],[0.22218125,	-0.00178125,	-0.023484375,	-0.21669375,	-0.04264375],[0.316271875,	0.02769375,	0.00544375,	-0.193390625,	0.003353125]]
