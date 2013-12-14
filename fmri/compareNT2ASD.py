# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import csv

datafile='/Users/amyskerry/Dropbox/EIB/tempASDcompare.csv'
chance=.5
global figargs
figargs=dict(elinewidth=3, markersize=14, fmt='o')

with open(datafile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        subjdata=[]
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                roinames=row
            elif subjnum==1:
                discnames=row
            elif subjnum==2:
                    fullnames=row
            else:
                subjdata.append(row)

discs=set(discnames[2:])
discs=list(discs)
roins=[]
for roi in roinames:
    roins.append(roi[1:-1])
roinames=roins
rois=set(roinames[2:])
rois=list(rois)
#print discs
#print rois
#print fullnames[2:]
palette = sns.color_palette("coolwarm", 12, desat=.5)
NTcolormean=palette[0]
NTcolor=palette[2]
PTcolor=palette[3]
ASDcolor=palette[11]
markervect=["d", "v", "s", "^", "*"]
#ASDcolorpal=sns.color_palette("YlOrRd_r", 5)
#ASDcolorpal=ASDcolorpal[2:]

#f,axar=plt.subplots(len(discs), sharex=True, figsize=[17,10])
for dn,disc in enumerate(discs):
    f,ax=plt.subplots(1,figsize=[5,10])
    #plt.subplot(axar[dn])
    plt.subplot(ax)
    xlim_deets=[-.2, len(rois)-.8]
    plt.xlim(xlim_deets)
    plt.xticks(range(len(rois)), rois, rotation='45') #rotation='vertical'
    #plt.margins(0.2) # Pad margins so that markers don't get clipped by the axes
    plt.subplots_adjust(bottom=0.15) # Tweak spacing to prevent clipping of tick-labels
    NT_disc=[]
    PT_disc=[]
    ASD_disc=[]
    for rn, region in enumerate(rois):
        full=region+'_'+disc
        colindex=fullnames.index(full)
        NT=[]
        PT=[]
        ASD=[]
        for subj in subjdata:
            if subj[1]=='0':
                PT.append(float(subj[colindex]))
            elif subj[1]=='1':
                NT.append(float(subj[colindex]))
            elif subj[1]=='2':
                ASD.append(float(subj[colindex]))
        NT=np.array(NT)
        PT=np.array(PT)
        ASD=np.array(ASD)
        NT=NT[~np.isnan(NT)]
        PT=PT[~np.isnan(PT)]
        ASD=ASD[~np.isnan(ASD)]
        max_data = np.r_[NT, ASD, PT].max()
        min_data = np.r_[NT, ASD, PT].min()
        NT_disc.append(NT)      
        PT_disc.append(PT)
        ASD_disc.append(ASD)
        plt.ylim(.40, .65)
        #plt.ylim(min_data-.005, max_data+.005)
        #bins = np.linspace(min_data-.02, max_data)
        #print bins
        #plt.figure()
        #plt.hist(NT, bins, normed=True, color="#6495ED", alpha=.5)
        #plt.hist(ASD, bins, normed=True, color="#F08080", alpha=.5);
        #NT_disc=np.dstack(NT_disc)
        #ASD_disc=np.dstack(ASD_disc)
        plt.title(disc)
        plt.plot(xlim_deets, [chance,chance], ls='dashed', color='orange')
        plt.plot([rn for i in NT],NT, 'd', color=NTcolor, markersize=6, alpha=.7)
        thiserror=np.std(NT)/np.sqrt(len(NT))
        #plt.plot([rn for i in PT],PT, 'd', color=PTcolor, markersize=6, alpha=.7)
        plt.errorbar(rn,np.mean(NT),yerr=thiserror, color=NTcolormean, **figargs) 
        for asd_num, asd_ind in enumerate(ASD):
            #plt.plot(rn,asd_ind, 'd', color=ASDcolorpal[asd_num], markersize=9)#, alpha=.7)
            plt.plot(rn,asd_ind, markervect[asd_num], color=ASDcolor, markersize=8, alpha=.9)

    #sns.violin(NT_disc, "points", color="#F08080")
    #sns.violin(ASD_disc, "points", color="#6495ED")

    #print NT_disc
    #plt.bar(range(len(NT_disc)), NT_disc)
    #plt.bar(range(len(ASD_disc)), ASD_disc);
        
#plt.close('all')


