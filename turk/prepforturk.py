# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 15:01:23 2013

@author: amyskerry
"""
import string
import random as rand
import csv

def makekeycode(n,c):
    rand.seed(n)
    key=str(rand.random())
    key=key[4:-1]
    keystr='x'+key+c+str(n)+'0x'
    return keystr

def makethestuff(base,conds,numhitpercond,cbvers,batch):
    names=[]
    keys=[]    
    blacklist=[0, 5, 10, 15, 30, 40, 45, 48, 51, 55, 66, 70, 77, 79, 81, 82, 83, 85, 87, 88, 89, 92, 95, 118, 125, 126, 134, 154, 160, 163, 169, 172, 179, 182]
    cblabels=list(string.ascii_lowercase[0:cbvers])
    for c in conds:
        if int(c[1:]) not in blacklist:
            for cb in cblabels: 
                
                for n in range(numhitpercond):
                    if n<9:
                        num='0'+str(n+1)
                    else:
                        num=str(n+1)
                    namest=base+str(batch+1)+cb+'_'+c+'_'+num
                    names.append(namest)
                    keys.append(makekeycode(n,c))
                    #do the other things
    return names, keys
def makethestuffrand(base,conds,numhitpercond,cbvers,batch):
    names, keys=makethestuff(base,conds,numhitpercond,cbvers,batch)
    newnames=[name+'_'+str(rand.randint(100,999)) for name in names]
    return newnames, keys

def maketurkcsv(ignore,names,vals,filename):
    print filename
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(names)
        for n,v in enumerate(vals[0]):
            writestr=[]
            if v not in ignore:
                for variable in vals:
                    writestr.append(variable[n])
            writer.writerow(writestr)
    f.close()
        
