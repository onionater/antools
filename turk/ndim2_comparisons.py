# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 19:26:13 2014

@author: amyskerry
"""
import sys 
sys.path.append('/Users/amyskerry/Dropbox/antools/utilities')
import matplotlib.pyplot as plt
import aesbasicfunctions as abf
import aesstats as astat

# should produce dicts with the following keys 'pcaondimsresults', 'clusterresults', 'confusioncorrs', 'subjectresults', 'classresults', 'analysisdeets', 'NDE_accuracy', 'NDE_confusions'
ver2file='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/DIM_data/outputfigs/analysis_2014-04-12_ver2.txt'
ver2output=abf.loadpickledobjects(ver2file)[0]
ver2controlfile='/Users/amyskerry/documents/projects/turk/NDE_dim2/data/DIM_data/outputfigs/analysis_2014-04-12_ver2_control.txt'
ver2controloutput=abf.loadpickledobjects(ver2controlfile)[0]
print ver2controloutput['confusioncorrs']
print ver2output['confusioncorrs']
z,p=astat.diffcorrcoeftest(ver2controloutput['confusioncorrs']['pearsonr'], ver2output['confusioncorrs']['pearsonr'], ver2controloutput['confusioncorrs']['N'], ver2output['confusioncorrs']['N'])