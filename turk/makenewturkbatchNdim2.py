# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 08:41:07 2014

@author: amyskerry
"""
import os
import sys
sys.path.append('/users/amyskerry/dropbox/antools/utilities')
import aesbasicfunctions as abf
import numpy as np

def extract_and_rewrite_remaining(remainingfile, numberofhits):
    '''checks <remainingdir> and extracts values for <numberofhits> hits, rewrites remainingdir without those hits'''
    names,data=abf.extractdata(remainingfile)
    newones=data[0:numberofhits]
    remaining=data[numberofhits:]
    abf.writedata(remainingfile,names,remaining)
    return names, newones
    
def findexisting(dirpath):
    '''searches rootdir and finds existing batches, returns num of next batch'''
    files=[f for f in os.listdir(dirpath) if 'batch' in f]
    filenums=[int(f[11:f.index('.')]) for f in files]
    return np.max(filenums)+1 
    
def createnewbatch(rootdir,newbatchfileroot, names, data):
    '''writes new csv file with new batch'''
    nextnum=findexisting(rootdir)
    newbatchfilename=''.join([rootdir,newbatchfileroot,str(nextnum),'.csv'])
    abf.writedata(newbatchfilename,names,data)
    print ' '.join(['wrote new batch to', newbatchfilename])
    

rootdir='/users/amyskerry/documents/projects/turk/NDE_dim2/turkcsvs/'
remainingfile=rootdir+'Ndim2_remaining.csv'
newbatchfileroot='Ndim2_batch'
numberofhits=10

names, data=extract_and_rewrite_remaining(remainingfile, numberofhits)
createnewbatch(rootdir, newbatchfileroot, names, data)
