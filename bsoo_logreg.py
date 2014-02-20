# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 23:11:31 2014

@author: amyskerry
"""

import csv
datafiles=['/users/amyskerry/dropbox/bsoo_study3.csv','/users/amyskerry/dropbox/bsoo_study4.csv']
studyids=['s3', 's4']
for datafile in datafiles:
    with open(datafile, 'rU') as csvfile:
        reader=csv.reader(csvfile)
        for rown, row in enumerate(reader):
            if rown==0:
                names=row
            else:
                print row