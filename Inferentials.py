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

def ConfidenceIntervals(data, alpha=0.95):
    n  = Count(data)
    mean  = Mean(data)
    delta  = StdErr(data) * scipy.stats.t._ppf((1+alpha)/2.0, n-1)
    return mean, mean-delta, mean+delta

def tiecorrect(rankvals):
    """
    Corrects for ties in Mann Whitney U and Kruskal Wallis H tests.  See
    Siegel, S. (1956) Nonparametric Statistics for the Behavioral Sciences.
    New York: McGraw-Hill.  Code adapted from |Stat rankind.c code.
    
    Usage:   tiecorrect(rankvals)
    Returns: T correction factor for U or H
    """
    sorted = rankvals.sort()
    print "rankvals = ",rankvals
    print "sorted   = ",sorted
    n = len(sorted)
    T = 0.0
    i = 0
    while (i<n-1):
        if sorted[i] == sorted[i+1]:
            nties = 1
            while (i<n-1) and (sorted[i] == sorted[i+1]):
                nties = nties +1
                i = i +1
            T = T + nties**3 - nties
        i = i+1
    T = T / float(n**3-n)
    return 1.0 - T

def GroupData(x, y):
    """
    This function takes 2 variables, x (a grouping / dummy variable), and 
    y (the actual data). Returned are a list of vectors for each condition.
    """
    uniques, freqs = UniqueVals(x)
    data = []
    for idx in zip(uniques, freqs):
        indices = ma.equal(x, idx[0])
        data.append(y[indices])
    return data

def GroupData2(x, y):
    """
    This function takes 2 variables, x (a grouping / dummy variable), and 
    y (the actual data). Returned are a list of vectors for each condition.
    """
    uniques, freqs = UniqueVals(x)
    data = []
    for idx in zip(uniques, freqs):
        vector = []
        for idy in zip(x,y):
            if idy[0] == idx[0]:
                vector.append(idy[1])
        data.append(vector)
    print data

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
# Two sample tests
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

def ChiSquare(x):
    vals, freqs = UniqueVals(x)
    expctd = Mean(freqs)
    df = Count(freqs) - 1
    num = (freqs - expctd)**2
    chisq = Sum(num/float(expctd))
    prob = chisqprob(chisq, df)
    return Count(freqs), chisq, df, prob

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



def KruskalWallisH(args):
    """
    This method performs a Kruskal Wallis test (like a nonparametric 
    between subjects anova) on a list of lists.
    Usage: KruskalWallisH(args).
    Returns: h, prob.
    """
    args = list(args)
    n = [0]*len(args)
    n = map(len,args)
    ranked = CalculateRanks(args).tolist()
    #T = tiecorrect(ranked)
    T = 0
    for i in range(len(args)):
        args[i] = ranked[0:n[i]]
        del ranked[0:n[i]]
    rsums = []
    for i in range(len(args)):
        rsums.append(sum(args[i])**2)
        rsums[i] = rsums[i] / float(n[i])
    ssbn = sum(rsums)
    totaln = sum(n)
    h = 12.0 / (totaln*(totaln+1)) * ssbn - 3*(totaln+1)
    df = len(args) - 1
    if T == 0:
        h = 0.0
        prob = 1.0
    else:
        h = h / float(T)
        prob = 0.5 #chisqprob(h,df)
    return h, prob

def KruskalWallis2 ( data ):
    """
    Kruskal-Wallis test for 2+ samples of independent nonparametric data.\n
    Data are passed as a matrix, first dimension the variables, second the cases
    """
    k = len ( data )
    df = k - 1
    N = Count ( data )
    ns = Count ( data[0] )
    print k, df, N, ns
    ranks = CalculateRanks ( data )
    print ranks
    Rj = sum ( numpy.transpose ( ranks ) )
    RjM = Mean ( numpy.transpose ( ranks ) )
    R = ( N + 1 ) / 2.0
    pre = 12 / float ( N * ( N + 1 ) )
    print RjM
    mid = ns * ( RjM ** 2 )
    post = 3 * ( N + 1 )
    num = pre * mid - post
    un, nu = tiecorrect ( data )
    den = 1 - ( ( sum ( nu ** 2 ) - nu ) ) / float ( ( N ** 3 ) - N )
    KW = num / float ( den )
    return KW

class anovaBetween(object):
    def __init__(self, x, y):
        """
        This method performs a univariate single factor between-subjects
        analysis of variance on a list of lists (or a Numeric matrix). It is
        specialised for SalStat and best left alone.
        Usage: anovaBetween(data). data are 2 variables, 1st being grouping, 2nd being
        the actual data
        Returns: SSbet, SSwit, SStot, dfbet, dferr, dftot, MSbet, MSerr, F, prob.
        """
        data = GroupData(x, y)
        k = len(data)
        GN = 0
        GM = 0.0
        self.SSwit = 0.0
        self.SSbet = 0.0
        self.SStot = 0.0
        means = []
        Ns = []
        SSdevs = []
        for variable in data:
            self.SSwit = self.SSwit + SSDevs(variable)
            Ns.append(Count(variable))
            means.append(Mean(variable))
            SSdevs.append(SampStdDev(variable))
            GN = GN + Ns[-1]
        GM = Mean(y)
        for i in range(k):
            self.SSbet = self.SSbet + (((means[i] - GM) **2) * Ns[i])
        self.SStot = self.SSwit + self.SSbet
        self.DFbet = k - 1
        self.DFerr = GN - k
        self.DFtot = self.DFbet + self.DFerr
        self.MSbet = self.SSbet / float(self.DFbet)
        self.MSerr = self.SSwit / float(self.DFerr)
        try:
            self.F = self.MSbet / self.MSerr
        except ZeroDivisionError:
            self.F = 1.0
        self.prob = fprob(self.DFbet, self.DFerr, self.F)

class anovaWithin(object):
    def __init__(self, data):
        """
        Produces a within-subjects ANOVA
        For the brave:
        Usage: anovaWithin(inlist, ns, sums, means). ns is a list of the N's, 
        sums is a list of the sums of each condition, and the same for means 
        being a list of means
        Returns: SSint, SSres, SSbet, SStot, dfbet, dfwit, dfres, dftot, MSbet,
        MSwit, MSres, F, prob.
        """
        GN = 0
        GS = 0.0
        GM = 0.0
        k = len(inlist)
        meanlist = []
        Nlist = []
        for variable in data:
            GN = GN + Count[variable]
            GS = GS + Sum[variable]
            Nlist.append(Count[variable])
            meanlist.append(Mean[variable])
        GM = GS / float(GN)
        self.SSwit = 0.0
        self.SSbet = 0.0
        self.SStot = 0.0
        for i in range(k):
            for j in range(Nlist[i]):
                diff = inlist[i][j] - meanlist[i]
                self.SSwit = self.SSwit + (diff ** 2)
                diff = inlist[i][j] - GM
                self.SStot = self.SStot + (diff ** 2)
            diff = meanlist[i] - GM
            self.SSbet = self.SSbet + (diff ** 2)
        self.SSbet = self.SSbet * float(GN / k)
        self.SSint = 0.0
        for j in range(ns[0]):
            rowlist = []
            for i in range(k):
                rowlist.append(inlist[i][j])
            n, sum, mean, SS = minimaldescriptives(rowlist)
            self.SSint = self.SSint + ((mean - GM) ** 2)
        self.SSint = self.SSint * k
        self.SSres = self.SSwit - self.SSint
        self.dfbet = k - 1
        self.dfwit = GN - k
        self.dfres = (ns[0] - 1) * (k - 1)
        self.dftot = self.dfbet + self.dfwit + self.dfres
        self.MSbet = self.SSbet / float(self.dfbet)
        self.MSwit = self.SSwit / float(self.dfwit)
        self.MSres = self.SSres / float(self.dfres)
        self.F = self.MSbet / self.MSres
        self.prob = fprob(self.dfbet, self.dfres, self.F)

if __name__ == '__main__':
    d1 = ma.array([1,2,3,4,3,2], mask=[0,0,1,0,0,0])
    d2 = ma.array([5,4,5,6,7,6])
    d3 = ma.array([1,1,1,1,1,1,1,1,2,2,2,2])
    #d3 = ma.array([1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3])
    print ChiSquare(d3)
    #print KendallsTau(d1, d2)
    #print PearsonR(d1, d2)
    #print SpearmanR(d1, d2)
    #print TTestUnpaired(d1,d2)
    #print OneSampleTTest(d1, 1.8)
    #print ConfidenceIntervals(d1)
    """
    a1 = ma.array([1,2,3,4,3,2,5,4,5,6,5,6,4,3,2,9,3,2],mask=[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    a2 = ma.array([1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3])
    a3 = ma.array( [[1,2,3,4,3,2],
                    [5,4,5,6,5,6],
                    [4,3,2,9,3,2]])
    res = anovaBetween(a2, a1)
    print "SS = ",res.SSbet, res.SSwit, res.SStot
    print "DF = ",res.DFbet, res.DFerr, res.DFtot
    print "MS = ",res.MSbet, res.MSerr
    print "F, p = ",res.F, res.prob
    """