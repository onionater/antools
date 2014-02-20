# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:20:00 2014

@author: amyskerry
"""
import seaborn as sns
import csv
import numpy as np
import h5py
import scipy.io


filename='/users/amyskerry/documents/analysis2/NTASD_motioncompare.csv' #(made from output of build_motion_report.m on the server)
column_names=['mean translation/timepoint','mean rotation/ time point','mean artifacts per run','ASD']
#plt.bar(x, d, bar_width,color=colors[nd],yerr=sems[nd],error_kw=error_config,label=rowlabels[nd])
data=[]
indices={}
colorscheme=sns.color_palette(['#010199','#6666C2','#3E7C10','#96CE80'],4)
with open(filename, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        trans=[]
        rot=[]
        art=[]
        asd=[]
        colors=[]
        for subjnum, row in enumerate(reader):
            if subjnum==0:
                colnames=row
                indices['trans']=colnames.index('mean translation/timepoint') #mm
                indices['rot']=colnames.index('mean rotation/ time point') #degrees
                indices['art']=colnames.index('mean artifacts per run')# number
                indices['asd']=colnames.index('ASD')
            else:
                data.append(row)
                trans.append(row[indices['trans']])
                rot.append(row[indices['rot']])
                art.append(row[indices['art']])
                asd.append(row[indices['asd']])
                if row[indices['asd']]=='0':
                    colors.append(colorscheme[0])
                if row[indices['asd']]=='1':
                    colors.append(colorscheme[1])
trans=[float(el) for el in trans]
rot=[float(el) for el in rot]
art=[float(el) for el in art]
asd=[float(el) for el in asd]
f,ax=plt.subplots(3,1)
ax[0].bar(range(len(trans)), trans, 1,color=colors)
ax[0].set_ylabel('translation\n/timepoint (mm)')
ax[0].get_xaxis().set_visible(False)
ax[0].set_ylim([0,.3])
ax[1].bar(range(len(rot)), rot, 1,color=colors)
ax[1].set_ylabel('rotation\n/timepoint (mm)')
ax[1].get_xaxis().set_visible(False)
ax[1].set_ylim([0,.3])
ax[2].bar(range(len(art)), art, 1,color=colors)
ax[2].set_ylabel('# artifacts\n/run')
ax[2].get_xaxis().set_visible(False)
ax[2].set_ylim([0,100])
ax[0].set_xlabel('subjects')
f.suptitle('motion NT and ASD')

roifilename='/users/amyskerry/documents/analysis2/NTASD_roidetails.mat'
f = h5py.File(roifilename,'r') 
#f=scipy.io.loadmat(roifilename)
roidetails = f.get('report')
numrois=size(roidetails['name'])
asdkey=f[roidetails['ASD'][0][0]].value[0]
NT=asds==0
numNT=np.sum(NT)
ASD=asds==1
numASD=np.sum(ASD)
for roin, roi in enumerate(roidetails['name']):
    peakTref=roidetails['peakT'][roin][0]
    peakT=f[peakTref]
    #print peakT.value[0]
    nvoxref=roidetails['numvoxels'][roin][0]
    nvox=f[nvoxref]
    nvoxels=nvox.value[0]
    NTnvox=[el for el in nvoxels[NT] if not np.isnan(el)]
    ASDnvox=[el for el in nvoxels[ASD] if not np.isnan(el)]
    NTcount=len(NTnvox)
    NTmean=np.mean(NTnvox)
    ASDcount=len(ASDnvox)
    ASDmean=np.mean(ASDnvox)
    nameref=roidetails['name'][roin][0]
    name=f[nameref]
    roistr = ''.join(unichr(c) for c in name.value)
    print roistr+'... '+'NT: '+str(NTmean)+' voxels, ('+str(NTcount)+'/'+str(numNT)+' found)'
    print roistr+'... '+'ASD: '+str(ASDmean)+' voxels, ('+str(ASDcount)+'/'+str(numASD)+' found)'
