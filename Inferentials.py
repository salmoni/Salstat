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

def PairwiseDeletion2(data):
    """
    Takes a matrix and turns any row that has a missing value into a row of all missing values
    """
    shape = data.shape
    k = shape[0] # number of conditions / variables
    n = shape[1] # number of cases per variable
    for col in range(k):
        for item in range(n):
            if data[col][item] is ma.masked:
                data[:,item] = ma.masked
                break
    return data

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
    print ("rankvals = ",rankvals)
    print ("sorted   = ",sorted)
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
        data.append(ma.array(vector))
    return data

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
        prob = -1.0
        d = 0.0
    else:
        df = Count(data) - 1
        svar = (df * SampVar(data)) / float(df)
        t_diff = Mean(data) - usermean
        t = t_diff / math.sqrt(svar*(1.0/Count(data)))
        d = t_diff / float(SampStdDev(data))
        prob = betai(0.5*df, 0.5, float(df)/(df+(t*t)))
    result = {}
    result['df'] = df
    result['t'] = t
    result['prob'] = prob
    result['d'] = d
    result["help"] = """T-test (one sample). Requires 1 variable, an independent
                        variable of observations, and also a user hypothesised mean to be compared against"""
    result['quote'] = "<b>Quote: </b> <i>t</i> (%d) = %.3f, <i>p</i> = %1.4f, d = %.3f<br />"%(df, t, prob, d)
    result['quotetxt'] = "Quote: t (%d) = %.3f, p = %1.4f, d = %.3f\n"%(df, t, prob, d)
    return result

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
    result = {}
    result['nplus'] = nplus
    result['nminus'] = nminus
    result['nequal'] = nequal
    result['z'] = z
    result['probability'] = prob
    result["help"] = """One sample sign test. This requires 1 variable (an independent
                        variable of observations) and a user hypothesised mean to be compared against"""
    result['quote'] = "<b>Quote: </b> <i>z</i> = %.3f, <i>p</i> = %1.4f<br />"%(z, prob)
    result['quotetxt'] = "Quote: z = %.3f, p = %1.4f\n"%(z, prob)
    return result

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
    result = {}
    result['df'] = df
    result['chisquare'] = chisquare
    result['probability'] = prob
    result["help"] = """T-test (one sample). Requires 1 variable, an independent
                        variable of observations, and also a user hypothesised mean to be compared against"""
    result['quote'] = "<b>Quote: </b> <i>Chi</i> (%d) = %.3f, <i>p</i> = %1.4f<br />"%(chisquare, df, prob)
    result['quotetxt'] = "Quote: Chi (%d) = %.3f, p = %1.4f\n"%(chisquare, df, prob)
    return result


#########################################################################
# Two sample tests
#########################################################################


def TTestUnpaired(data1, data2):
    """
    Returns df, t, prob, d
    """
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
    result = {}
    result["t"] = t
    result["df"] = df
    result["prob"] = prob
    result["d"] = d
    result["help"] = """T-test (unpaired). Requires 2 variables, the first an independent
                        variable to define the groups, and the second the dependent variable"""
    result['quote'] = "<b>Quote: </b> <i>t</i> (%d) = %.3f, <i>p</i> = %1.4f, d = %.3f<br />"
    result['quotetxt'] = "Quote: t (%d) = %.3f, p = %1.4f, d = %.3f\n"
    return result

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
    result = {}
    result['t'] = t
    result['df'] = df
    result['prob'] = prob
    result['d'] = d
    result['quote'] = "<b>Quote: </b> <i>t</i> (%d) = %.3f, <i>p</i> = %1.4f, d = %.3f<br />"
    result['quotetxt'] = "Quote: t (%d) = %.3f, p = %1.4f, d = %.3f\n"
    return result

def TwoSampleSignTest(data1, data2):
    """
    This method performs a 2 sample sign test for matched samples on 2
    supplied data vectors.
    Usage: TwoSampleSignTest(data1, data2)
    Returns: nplus, nminus, ntotal, z, prob
    """
    c1 = Count(data1)
    c2 = Count(data2)
    nplus  = 0
    nminus = 0
    ntotal = 0
    if c1 != c2:
        prob   = -1.0
        z      = 0.0
        nplus  = 0
        nminus = 0
        ntotal = 0
    else:
        #data1, data2 = PairwiseDeletion(data1, data2)
        #nplus  = Count(map(higher,data1,data2))
        #nminus = Count(map(lower,data1,data2))
        for row in data1:
            ntotal += 1
            if data1[row] > data2[row]:
                nplus += 1
            elif data1[row] < data2[row]:
                nminus += 1

        #ntotal = nplus-nminus
        mean   = c1 / 2
        sd     = math.sqrt(mean)
        z      = (nplus-mean)/sd
        prob   = erfcc(abs(z)/1.4142136)
    result = {'z':z, 'prob':prob,'sd':sd,'mean':mean}
    result['quote'] = "<b>Quote: </b> <i>Z</i> = %.3f, <i>p</i> = %1.4f, \
            <i>mean</i> = %.3f, <i>standard deviation</i> = %.3f<br />"%\
            (result['z'],result['prob'], result['mean'], result['sd'])
    result['quotetxt'] = "Quote: Z = %.3f, p = %1.4f, mean = %.3f, \
            standard deviation = %.3f"%\
            (result['z'],result['prob'], result['mean'], result['sd'])
    return result

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
    result = {'d':d, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>d</i> = %.3f, <i>p</i> = %1.4f<br />"%\
            (result['d'],result['prob'])
    result['quotetxt'] = "Quote: d = %.3f, p = %1.4f"%\
            (result['d'],result['prob'])
    return result

def MannWhitneyU(x, y):
    u, prob = stats.mannwhitneyu(x, y)
    result = {'u':u, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>U</i> = %.3f, <i>p</i> = %1.4f<br />"%\
            (result['u'],result['prob'])
    result['quotetxt'] = "Quote: U = %.3f, p = %1.4f"%\
            (result['u'],result['prob'])
    return result

def linregress(x,y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, intercept, r_value, p_value, std_err

def SignedRanks(x, y):
    T, prob = scipy.stats.wilcoxon(x, y)
    result = {'t':T, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>T</i> = %.3f, <i>p</i> = %1.4f<br />"%\
            (result['t'],result['prob'])
    result['quotetxt'] = "Quote: T = %.3f, p = %1.4f"%\
            (result['t'],result['prob'])
    return result

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
    x, y = PairwiseDeletion(x,y)
    tau, prob = stats.kendalltau(x,y)
    df = Count(x)-1
    result = {'tau':tau, 'df':df, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>tau</i> (%d) = %.3f, <i>p</i> = %1.4f<br />"
    result['quotetxt'] = "Quote: tau (%d) = %.3f, p = %1.4f\n"
    return result

def PearsonR(x, y):
    x, y = PairwiseDeletion(x,y)
    r, prob = stats.pearsonr(x, y)
    df = Count(x)-1
    result = {'r':r, 'df':df, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>r</i> (%d) = %.3f, <i>p</i> = %1.4f<br />"
    result['quotetxt'] = "Quote: r (%d) = %.3f, p = %1.4f\n"
    return result

def PointBiserial(x, y):
    x, y = PairwiseDeletion(x,y)
    r, prob = stats.pointbiserialr(x, y)
    df = Count(x)-1
    result = {'r':r, 'df':df, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>r</i> (%d) = %.3f, <i>p</i> = %1.4f<br />"
    result['quotetxt'] = "Quote: r (%d) = %.3f, p = %1.4f\n"
    return result

def SpearmanR(x, y):
    x, y = PairwiseDeletion(x,y)
    r, prob = stats.spearmanr(x, y)
    df = Count(x)-1
    result = {'r':r, 'df':df, 'prob':prob}
    result['quote'] = "<b>Quote: </b> <i>r</i> (%d) = %.3f, <i>p</i> = %1.4f<br />"
    result['quotetxt'] = "Quote: r (%d) = %.3f, p = %1.4f\n"
    return result

#########################################################################
# Three sample tests
#########################################################################

def KruskalWallis (data):
    """
    Kruskal-Wallis H test. Taken from Siegel's Nonparametric Statistics
    """
    shape = data.shape
    k = shape[0]
    ranked = CalculateRanks ( data )
    ns = ranked.count ( 1 )
    N = Count ( ranked )
    ranked_sums = ranked.sum ( 1 )
    p1 = 12 / float( N * ( N + 1 ) )
    p2 = Sum ( ranked_sums ** 2 / ns )
    p3 = 3 * ( N + 1 )
    H = ( p1 * p2 )  - p3
    df = k - 1
    prob = chisqprob( H , df )
    result = { 'h' : H , 'df' : df , 'prob' : prob }
    return result

def Friedman (data):
    """
    Friedman's two-way ANOVA for nonparametric data
    """
    data = PairwiseDeletion2 ( data )
    shape = data.shape
    k = shape[0]
    n = shape[1]
    N = k * n
    ranked = numpy.zeros([k,n])
    for idx in range(n):
        row = data[:, idx]
        ranked_row = CalculateRanks ( row )
        ranked[:, idx] = ranked_row
    #ranked = CalculateRanks ( data )
    ranked_sums = ranked.sum ( 1 )
    p1 = 12 / float ( n * k * ( k + 1 ) )
    p2 = Sum ( ranked_sums ** 2 )
    p3 = 3 * n * ( k + 1 )
    chi = ( p1 * p2 ) - p3
    df = k - 1
    prob = chisqprob( chi , df )
    results = { 'chi' : chi , 'k' : k , 'n' : n , 'df' : df , 'prob' : prob }
    return results

def anovaBetween(data):
    """
    This function performs a univariate single factor between-subjects
    analysis of variance on a list of lists (or a Numeric matrix). It is
    specialised for SalStat and best left alone.
    Usage: anovaBetween(data). data are 2 variables, 1st being grouping, 2nd being
    the actual data
    Returns dictionary with: SSbet, SSwit, SStot, dfbet, dferr, dftot, MSbet, MSerr, F, prob.
    """
    results = {}
    k = len(data)
    GN = 0
    GM = 0.0
    SSwit = 0.0
    SSbet = 0.0
    SStot = 0.0
    means = []
    Ns = []
    SSdevs = []
    for variable in data:
        SSwit = SSwit + SSDevs(variable)
        Ns.append(Count(variable))
        means.append(Mean(variable))
        SSdevs.append(SampStdDev(variable))
        GN = GN + Ns[-1]
    GM = data.ravel().mean()
    for i in range(k):
        SSbet = SSbet + (((means[i] - GM) **2) * Ns[i])
    SStot = SSwit + SSbet
    DFbet = k - 1
    DFerr = GN - k
    DFtot = DFbet + DFerr
    MSbet = SSbet / float(DFbet)
    MSerr = SSwit / float(DFerr)
    try:
        F = MSbet / MSerr
    except ZeroDivisionError:
        F = 1.0
    prob = fprob(DFbet, DFerr, F)
    results["SSwit"] = SSwit
    results["SSbet"] = SSbet
    results["SStot"] = SStot
    results["DFbet"] = DFbet
    results["DFerr"] = DFerr
    results["DFtot"] = DFtot
    results["MSbet"] = MSbet
    results["MSerr"] = MSerr
    results["F"] = F
    results["p"] = prob
    return results

def anovaWithin(data):
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
    k = len(data)
    meanlist = []
    Nlist = []
    for variable in data:
        GN = GN + Count(variable)
        GS = GS + Sum(variable)
        Nlist.append(Count(variable))
        meanlist.append(Mean(variable))
    GM = GS / float(GN)
    SSwit = 0.0
    SSbet = 0.0
    SStot = 0.0
    for i in range(k):
        for j in range(Nlist[i]):
            diff = data[i][j] - meanlist[i]
            SSwit = SSwit + (diff ** 2)
            diff = data[i][j] - GM
            SStot = SStot + (diff ** 2)
        diff = meanlist[i] - GM
        SSbet = SSbet + (diff ** 2)
    SSbet = SSbet * float(GN / k)
    SSint = 0.0
    SSint = ma.sum((ma.mean(data,0)-ma.mean(data))** 2)
    SSint = SSint * k
    SSres = SSwit - SSint
    dfbet = k - 1
    dfwit = Nlist[0] - (k - 1)
    dfres = (Nlist[0] - 1) * (k - 1)
    dftot = dfbet + dfwit + dfres
    MSbet = SSbet / float(dfbet)
    MSwit = SSwit / float(dfwit)
    MSres = SSres / float(dfres)
    F = MSbet / MSres
    prob = fprob(dfbet, dfres, F)
    results = {}
    results["SSbet"] = SSbet
    results["DFbet"] = dfbet
    results["MSbet"] = MSbet
    results["F"] = F
    results["p"] = prob

    results["SSwit"] = SSwit
    results["DFwit"] = dfwit
    results["MSwit"] = MSwit

    results["SSres"] = SSres
    results["DFres"] = dfres
    results["MSres"] = MSres

    results["SSint"] = SSint

    results["SStot"] = SStot
    results["DFtot"] = dftot
    return results

if __name__ == '__main__':
    """"
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
                    [4,3,2,9,3,2]],
                   mask=[[0,0,0,1,0,0],
                    [1,0,0,0,0,0],
                    [0,0,0,0,0,0]])
    a4 = ma.array( [[ 96,128, 83, 61,101],
                    [ 82,124,132,135,109],
                    [115,149,166,147,1]],
                    mask=[[0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,1]])
    a5 = ma.array( [[18,21,24,28],[26,32,34,36],[18,21,23,24]] )
    #print KruskalWallis(a5)
    data = numpy.ma.array([[9,9.5,5,7.5,9.5,7.5,8,7,8.5,6],
                           [7,6.5,7,7.5,5,8,6,6.5,7,7],
                           [6,8,4,6,7,6.5,6,4,6.5,3]])
    print (Friedman (data))
    """
    res = anovaBetween(a2, a1)
    print "SS = ",res.SSbet, res.SSwit, res.SStot
    print "DF = ",res.DFbet, res.DFerr, res.DFtot
    print "MS = ",res.MSbet, res.MSerr
    print "F, p = ",res.F, res.prob
    """
