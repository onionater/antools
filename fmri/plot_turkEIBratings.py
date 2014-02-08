# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 17:10:28 2014

@author: amyskerry
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv

#general paramteres
legendvals=('facial expressions: pos','facial expressions: neg','situations: pos','situations: neg')
#colorscheme= sns.color_palette('hls', len(rows))
colorscheme=sns.color_palette(['#3E7C10','#96CE80','#010199','#6666C2'],4)
xaxis='ROI'
yaxis='Beta value'
font = {'family' : 'Gill Sans',
        'weight':'regular',
        'size'   : 50}

matplotlib.rc('font', **font)

conds={'mh': 'facial expressions: pos','mu': 'facial expressions: neg', 'fh': 'facial expressions: pos', 'fu': 'facial expressions: neg','sh': 'situations: pos','su': 'situations: neg','nh': 'situations: pos','nu': 'situations: neg'}

datafile='/Users/amyskerry/Dropbox/EIB/stimnormingforgraph.csv'
with open(datafile, 'rU') as csvfile:
     inreader = csv.reader(csvfile)
     reader=[x for x in inreader]
     stims=reader[0]
     count=reader[1]
     means=reader[2]
     sems=reader[4]
cond_means=[[],[],[],[]]
cond_sems=[[],[],[],[]]
cond_color=[[],[],[],[]]
for stimn,stim in enumerate(stims):
    c=stim[3:5]
    cond=conds[c]
    index=legendvals.index(cond)
    cond_means[index].append(float(means[stimn]))
    cond_sems[index].append(float(sems[stimn]))
    cond_color[index].append(colorscheme[index])

mean_vect=[]
sem_vect=[]
color_vect=[]
for rown, row in enumerate(cond_means):
    mean_vect.extend(row)
    sem_vect.extend(cond_sems[rown])
    color_vect.extend(cond_color[rown])
plt.bar(range(len(mean_vect)), mean_vect, yerr=sem_vect, color=color_vect)  
plt.ylabel('valence (negative to positive)')  
plt.xlabel('stimuli') 
plt.xticks([23,72,120,167], legendvals)
