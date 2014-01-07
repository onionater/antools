# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 13:51:00 2014

@author: amyskerry
"""
#simple stats operating on pd dataframes

def oneway_anova(data):
    """
    Calculates one-way ANOVA on a pandas.DataFrame.
 
    Args:
        data (pandas.DataFrame): rows contain groups (e.g., different
        conditions), while columns have samples (e.g., participants)
 
    Returns:
        F (float): F-value
        p (float): p-value
        k-1 (int): Between Group degrees of freedom
        N-k (int): Within Group degrees of freedom
 
    """
    F, p = scipy.stats.f_oneway(*[d[1] for d in data.iterrows()])
    k = len(data)  # number of conditions
    N = k*len(data.columns)  # conditions times participants
    return F, p, k-1, N-k

def p_corr(df1, df2):
    """
    Computes Pearson correlation and its significance (using a t
    distribution) on a pandas.DataFrame.
 
    Ignores null values when computing significance. Based on
    http://en.wikipedia.org/wiki/Pearson_productmoment_correlation_coefficient#Testing_using_Student.27s_t-distribution
 
    Args:
        df1 (pandas.DataFrame): one dataset
        df2 (pandas.DataFrame): another dataset
 
    Returns:
        corr (float): correlation between the two datasets
        t (float): an associated t-value
        p (float): one-tailed p-value that the two datasets differ
    """
    corr = df1.corr(df2)
    N = np.sum(df1.notnull())
    t = corr*np.sqrt((N-2)/(1-corr**2))
    p = 1-scipy.stats.t.cdf(abs(t),N-2)  # one-tailed
    return corr, t, p
    
def ttest_pairedsample(data1, data2):
    t,p =  scipy.stats.ttest_rel(data1, data2, axis=0)
    return t,p
    
def linearregrression(x,y):
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)
    return slope, intercept, r_value, p_value, std_err
    
def ttest_onesample(data, prop):
    t,p= scipy.stats.ttest_1samp(data, popmean, axis=0)
    return t,p