# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 01:34:45 2014

@author: amyskerry
"""

import base64
import csv
import datetime
import sys

def loadphotocsv(photofile):
    '''full path to csvfile containing photos under column "photo"'''
    allphotos=[]
    csv.field_size_limit(sys.maxsize)
    with open(photofile, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for rown, row in enumerate(reader):
            if rown==0:
                photoindex=row.index('photo')
            else:
                photoentry=row[photoindex]
                #cutstring="MiniFieldStorage('photofield', '"
                cutstring=''
                photo=photoentry[len(cutstring):]
                allphotos.append(photo)
        print str(rown)+ ' lines in csv file'
    return allphotos

def printphotos(photofile, savedir):
    '''full path to csvfile containing photos under column "photo", directory in which to save photos''' 
    allphotos=loadphotocsv(photofile)
    date=datetime.datetime.now()
    datestr=date.strftime("%Y-%m-%d") 
    for photon, photo in enumerate(allphotos):
        if photon<99:
            number='0'+str(photon)
        else:
            number=str(photon)
        g = open(savedir+'photo'+number+'_'+datestr+'.jpg', 'w')
        g.write(base64.decodestring(photo))
        g.close()
    print number + ' photos printed'
    
    