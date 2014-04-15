# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 20:02:25 2014

@author: amyskerry
"""
import numpy as np
import scipy.stats

def diffcorrcoeftest(rvalue1, rvalue2, N1, N2):
    ''' tests for difference between 2 r values by performing fishers transformation and performing t-test on the z values. returns z and two tailed p '''
    r_z1=np.arctanh(rvalue1) #equivalent to 0.5 * np.log((1 + rvalue1)/(1 - rvalue1))
    r_z2=np.arctanh(rvalue2)
    se_diff_r = np.sqrt(1.0/(N1 - 3.0) + 1.0/(N2 - 3.0))
    diff = r_z1 - r_z2
    z = abs(diff / se_diff_r)
    p = (1 - scipy.stats.norm.cdf(z))*2
    return round(z,3), round(p,3)
    
def nancorr(vector1,vector2):
    '''takes two vectors and reduces to vectors corresponding only to indices where both vectors are nonnan. returns correlation'''
    x=[val for valn, val in enumerate(vector1) if not np.isnan(val) and not np.isnan(vector2[valn])]
    y=[val for valn, val in enumerate(vector2) if not np.isnan(val) and not np.isnan(vector1[valn])]
    if len(y) != len(x) or len(y)<2:
        print "warning: vector lengths don't make sense"
    rvalue, pvalue=scipy.stats.pearsonr(x,y)
    return rvalue, pvalue, len(x)
    

def tests():
    z,p=diffcorrcoeftest(.7, .5, 20, 20)
    predicted_z1=0.927
    predicted_p1=0.354
    if z==predicted_z1 and p ==predicted_p1:
        print 'passed'
        print z,p
    else:
        print 'failed'
        print z,p
    z,p=diffcorrcoeftest(-.4, .1, 20, 20)
    predicted_z2=1.528
    predicted_p2=0.127
    if z==predicted_z2 and p ==predicted_p2:
        print 'passed'
        print z,p
    else:
        print 'failed'
        print z,p
    z,p=diffcorrcoeftest(.7, .5, 40, 20)
    predicted_z3=1.085
    predicted_p3=0.278
    if z==predicted_z3 and p ==predicted_p3:
        print 'passed'
        print z,p
    else:
        print 'failed'
        print z,p
        