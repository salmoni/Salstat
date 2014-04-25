"""
Inferentials.py
A statistics module for Python. Composed of inferential tests.
(c) 2014 Alan James Salmoni
"""

import math
import numpy
import numpy.ma as ma
import scipy
import scipy.stats
import scipy.stats.mstats as stats
from probabilities import *
from AllRoutines import *


#########################################################################
# Support routines
#########################################################################

def PairwiseDeletion(data1, data2):
    for i in range(len(data1)):
        if data1[i] is ma.masked:
            data2[i] = ma.masked
        elif data2[i] is ma.masked:
            data1[i] = ma.masked
    return data1, data2

def higher(a,b):
    if a>b:
        return 1
    else:
        return 0

def lower(a,b):
    if a<b:
        return 1
    else:
        return 0


#########################################################################
# One sample tests (requires a user-hypthesised mean
#########################################################################


def OneSampleTTest(data, usermean):
    """
    OneSampleTTest
    Performs a 1 sample t-test
    Requires: Data (vector) and usermean
    Returns df, t, prob
    """
    data = data.compressed()
    if Count(data) < 2:
        df = 0
        t = 1.0
        prob = 1.0
        d = 0.0
    else:
        df = Count(data) - 1
        svar = (df * SampVar(data)) / float(df)
        t_diff = Mean(data) - usermean
        t = t_diff / math.sqrt(svar*(1.0/Count(data)))
        d = t_diff / float(SampStdDev(data))
        prob = betai(0.5*df, 0.5, float(df)/(df+(t*t)))
    return df, t, prob, d

def OneSampleSignTest(data, usermean):
    """
    OneSampleSignTest
    Performs a 1 sample sign test
    Requires: Data (vector) as user mean
    Returns nplus, nminus, nequal, z, prob
    """
    data = data.compressed()
    nplus = 0
    nminus = 0
    nequal = 0
    for datum in data:
        if datum < usermean:
            nplus += 1
        elif datum > usermean:
            nminus += 1
        else:
            nequal += 1
    ntotal = nplus + nminus
    try:
        z=(nplus-(ntotal/2)/math.sqrt(ntotal/2))
    except ZeroDivisionError:
        z=0
        prob=1.0
    else:
        prob=erfcc(abs(z) / 1.4142136)
    return nplus, nminus, nequal, z, prob

def ChiSquareVariance(data, usermean):
    """
    Returns: df, chisquare, prob
    """
    data = data.compressed()
    df = Count(data) - 1
    try:
        chisquare = (StdErr(data) / usermean) * df
        prob = chisqprob(chisquare, df)
    except ZeroDivisionError:
        chisquare = 0.0
        prob = 1.0
    return df, chisquare, prob


#########################################################################
# One sample tests (requires a user-hypthesised mean
#########################################################################


def TTestUnpaired(data1, data2):
    """
    Returns df, t, prob, d
    """
    # pairwise deletion
    for i in range(len(data1)):
        if data1[i] is ma.masked:
            data2[i] = ma.masked
        elif data2[i] is ma.masked:
            data1[i] = ma.masked
    c1 = Count(data1)
    c2 = Count(data2)
    if c1 < 2:
        df = 0
        t = 1.0
        prob = -1.0
        d = 0.0
    m1 = Mean(data1)
    m2 = Mean(data2)
    s1 = SampStdDev(data1)
    s2 = SampStdDev(data2)
    v1 = SampVar(data1)
    v2 = SampVar(data2)
    df = c1 + c2 - 2
    svar = (c1*SampVar(data1) + c2*SampVar(data2)) / float(df)
    try:
        SDwithin = math.sqrt(((c1-1)*s1)+((c1-1)*s2)/float(c1+c2-2))
        d = (m1-m2)/SDwithin
        t, prob = stats.ttest_ind(data1, data2)
    except ZeroDivisionError:
        t = 0.0
        d = 0.0
        prob = 1.0
    return df, t, prob, d

def TTestPaired(data1, data2):
    for i in range(len(data1)):
        if data1[i] is ma.masked:
            data2[i] = ma.masked
        elif data2[i] is ma.masked:
            data1[i] = ma.masked
    c1 = Count(data1)
    c2 = Count(data2)
    if c1 != c2:
        df = 0
        t = 1.0
        prob = -1.0
        d = 0.0
    else:
        cov = 0.0
        df = c1 - 1
        cov = Sum((data1-Mean(data1))*(data2-Mean(data2))) / df
        sd = math.sqrt((SampVar(data1)+SampVar(data2)-2.0 * cov)/float(c1))
        diff = data1 - data2
        try:
            t, prob = stats.ttest_rel(data1, data2)
            d = Mean(diff) / SampStdDev(diff)
        except ZeroDivisionError:
            t = 0.0
            prob = 1.0
    return df, t, prob, d

def TwoSampleSignTest(data1, data2):
    """
    This method performs a 2 sample sign test for matched samples on 2 
    supplied data vectors.
    Usage: TwoSampleSignTest(data1, data2)
    Returns: nplus, nminus, ntotal, z, prob
    """
    c1 = Count(data1)
    c2 = Count(data2)
    if c1 != c2:
        prob   = -1.0
        z      = 0.0
        nplus  = 0
        nminus = 0
        ntotal = 0
    else:
        data1, data2 = PairwiseDeletion(data1, data2)
        nplus  = Count(map(higher,data1,data2))
        nminus = Count(map(lower,data1,data2))
        ntotal = nplus-nminus
        mean   = c1 / 2
        sd     = math.sqrt(mean)
        z      = (nplus-mean)/sd
        prob   = erfcc(abs(z)/1.4142136)
    return nplus, nminus, ntotal, z, prob

def FTest(data1, data2, uservar):
    """
    This method performs a F test for variance and needs a user 
    hypothesised variance to be supplied.
    Usage: FTest(uservar)
    Returns: f, df1, df2, prob
    """
    v1 = SampVar(data1)
    v2 = SampVar(data2)
    c1 = Count(data1)
    c2 = Count(data2)
    try:
        f = (v1 / v2) / uservar
    except ZeroDivisionError:
        f = 1.0
    df1 = c1 - 1
    df2 = c2 - 1
    prob=fprob(df1, df2, f)
    return df1, df2, f, prob

def KolmogorovSmirnov(x, y):
    d, prob = stats.ks_twosamp(x, y)
    return d, prob

def MannWhitneyU(x, y):
    u, prob = stats.mannwhitneyu(x, y)
    return u, prob

def linregress(x,y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, intercept, r_value, p_value, std_err

def SignedRanks(x, y):
    T, p = scipy.stats.wilcoxon(x, y)
    return T, p

def RankSums(x, y):
    z, prob = scipy.stats.ranksums(x, y)
    return z, prob

def KendallsTau(x, y):
    tau, prob = stats.kendalltau(x,y)
    adj = PairwiseDeletion(x,y)
    df = Count(adj[0])-1
    return tau, df, prob

def PearsonR(x, y):
    r, prob = stats.pearsonr(x, y)
    adj = PairwiseDeletion(x,y)
    df = Count(adj[0])-1
    return r, df, prob

def PointBiserial(x, y):
    r, prob = stats.pointbiserialr(x, y)
    adj = PairwiseDeletion(x,y)
    df = Count(adj[0])-1
    return r, df, prob

def SpearmanR(x, y):
    r, prob = stats.spearmanr(x, y)
    adj = PairwiseDeletion(x,y)
    df = Count(adj[0])-1
    return r, df, prob

def ConfidenceIntervals(data, alpha=0.95):
    n  = Count(data)
    mean  = Mean(data)
    delta  = StdErr(data) * scipy.stats.t._ppf((1+alpha)/2.0, n-1)
    return mean, mean-delta, mean+delta




if __name__ == '__main__':
    d1 = ma.array([1,2,3,4,3,2], mask=[0,0,1,0,0,0])
    d2 = ma.array([5,4,5,6,7,6])
    print KendallsTau(d1, d2)
    #print PearsonR(d1, d2)
    #print SpearmanR(d1, d2)
    #print TTestUnpaired(d1,d2)
    #print OneSampleTTest(d1, 1.8)
    #print ConfidenceIntervals(d1)


