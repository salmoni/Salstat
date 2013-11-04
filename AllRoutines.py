"""
Stats routines

A complete list of statistics routine for the 'Computational Statistics' book

The routines are:

VSort - sort a vector
MSort - sort a numpy.matrix
CalculateRanks - for calculating the ranks of a numpy.matrix
GetSSCP_M - calculates the sum of squares and cross-products numpy.matrix
GetVarsCovars_M - calculates the variances and covariances numpy.matrix
GetVariances - calculates the variances of a numpy.matrix of variables
GetStdDevs - calculates the standard deviations of a numpy.matrix of variables
GetCorrelationMatrix - calculates the correlation numpy.matrix
Count - returns the number of non-missing data
sum - returns the sum of non-missing data
minimum - returns the minimum of non-missing data
maximum - returns the maximum of non-missing data
Range - maximum minus the minimum
proportions - 
relfreqmode - 
cumsum - 
cumproduct - 
cumpercent - 
frequencies - 
trimmeddata - 
trimmedmean - 
bitrimmedmean - 
mean - 
median - 
mode - 
moment - 
TukeyQuartiles - returns Tukey's hinges
MooreQuartiles - returns Moore & McCabe's hinges
SPQuantile - quantile used by S-Plus
TradQuantile - quantile used by SPSS
MidstepQuantile - mid-step qua
Q1 - Q1 quantile from Hyndnumpy.man & Fan
Q2 - Q2 quantile from Hyndnumpy.man & Fan
Q3 - Q3 quantile from Hyndnumpy.man & Fan
Q4 - Q4 quantile from Hyndnumpy.man & Fan
Q5 - Q5 quantile from Hyndnumpy.man & Fan
Q6 - Q6 quantile from Hyndnumpy.man & Fan
Q7 - Q7 quantile from Hyndnumpy.man & Fan
Q8 - Q8 quantile from Hyndnumpy.man & Fan
Q9 - Q9 quantile from Hyndnumpy.man & Fan 
InterquartileRange - 
SS - sum of squares
SSDevs - sum of squared deviations from the mean
SampVar - sample variance
PopVar - population variance
SampStdDev - sample standard deviation
PopStdDev - population standard deviation
StdErr - standard error
CoeffVar - coefficient of variation
ConfidenceIntervals - returns the confidence intervals
numpy.maD - Median absolute deviation
GeometricMean - the geometric mean
HarmonicMean - the harmonic mean
MSSD - mean square of successive differences
Skewness - returns the skewness
Kurtosis - returns the kurtosis
StandardScore - transforms a vector into a standard (ie, z-) score
EffectSizeControl - returns an effect size if a control condition is present
EffectSize - returns an effect size if no control is present
FiveNumber - Tukey's five number sumnumpy.mary (minimum, lower quartile, median, upper quartile, maximum)
OutliersSQR - returns two arrays, one of outliers defined by 1.5 * IQR, and the other without these outliers

"""
import math
import numpy 
import numpy.ma


def GetMostUsedTests():
    return ['Count','Sum','Mean','Median','Variance (sample)', \
            'Standard deviation (sample)', 'Standard error', \
            "Tukey's hinges", "Skewness","Kurtosis"]

def GetAllTests():
    Alltests = ['Count','Sum','Minimum','Maximum','Range','Frequencies',\
            'Proportions','Percentages','Relative frequency of the mode',\
            'Cumulative sum', \
            'Cumulative product','Cumulative percent', \
            'Trimmed mean','Bi-trimmed mean','Winsorised mean','Mean','Median',\
            'Mode','Moment',"Tukey's hinges","Moore & McCabe's hinges", \
            'S-Plus quantiles','SPSS quantiles','Mid-step quantiles', \
            'Quantile 1 (Hyndman & Fan)','Quantile 2 (Hyndman & Fan)', \
            'Quantile 3 (Hyndman & Fan)','Quantile 4 (Hyndman & Fan)', \
            'Quantile 5 (Hyndman & Fan)','Quantile 6 (Hyndman & Fan)', \
            'Quantile 7 (Hyndman & Fan)','Quantile 8 (Hyndman & Fan)', \
            'Quantile 9 (Hyndman & Fan)','Interquartile range', \
            'Sum of squares','Sum of squared deviations','Variance (sample)', \
            'Variance (population)','Standard deviation (sample)', \
            'Standard deviation (population)','Standard error', \
            'Coefficient of variation','Median absolute deviation', \
            'Geometric mean','Harmonic mean', \
            'Mean of successive squared differences',\
            'Skewness','Kurtosis']
    return Alltests

def Vsort(data):
    # check that 'data' is a vector
    return numpy.ma.sort(data)

def Msort(data):
    # check that 'data' is a numpy.matrix
    dims = numpy.ma.shape(data)
    length = dims[0] * dims[1]
    return numpy.ma.reshape(numpy.ma.sort(numpy.ma.reshape(data, length)), dims)

def UniqueVals3(data):
    """
    All unique values. Currently, only numeric values.
    """
    try:
        data = numpy.ma.array(data)
        uniques = numpy.ma.sort(list(set(data.compressed())))
        numbers = numpy.zeros((len(uniques)))
        for idx, unique in enumerate(uniques):
            number = numpy.ma.equal(data, unique).sum()
            numbers[idx] = number
    except AttributeError:
        uniques = set(list(data))
        numbers = []
        for value in uniques:
            freq = 0
            for cell in data:
                if cell == value:
                    freq = freq + 1
            numbers.append(freq)
    return uniques, numbers

def IndexMatches(value, data):
    indices = []
    for idx, item in enumerate(data):
        if value == item:
            indices.append(idx)
    return indices

def UniqueVals(data):
    """
    Returns unique values + frequencies
    """
    try:
        uniques = list(set(data))
    except TypeError:
        data = [data]
        uniques = data
    length = len(uniques)
    freqs = []
    # now find frequencies
    for item in uniques:
        nummatches = IndexMatches(item, data)
        freqs.append(Count(numpy.array(nummatches)))
    return uniques, freqs

def CalculateRanks(data, start = 1):
    data = numpy.ma.array(data)
    vals = sort(list(set(data.compressed())))
    rank = start - 0.5
    ranks = numpy.ma.zeros(numpy.ma.shape(data), 'f')
    for i in vals:
        numpy.match = numpy.ma.equal(data, i)
        incr = numpy.ma.sum(numpy.ma.sum(numpy.match))
        numpy.match = array(numpy.match)
        ranks[numpy.match] = rank + (incr / 2.0)
        rank = rank + incr
    return numpy.ma.numpy.masked_where(numpy.ma.equal(ranks, 0), ranks)

def GetSSCP_M(data):
    Xd = data - numpy.ma.average(data)
    Xdp = numpy.ma.transpose(Xd)
    return numpy.ma.dot(Xdp, Xd)

def GetVarsCovars_M(data):
    SSCP = GetSSCP_M(data)
    return SSCP / len(data[1]) # is the len(data[1]) correct?

def GetVariances(data):
    return numpy.ma.diagonal(GetVarsCovars_M(data))

def GetStdDevs(data):
    return numpy.ma.sqrt(GetVariances(data))
    
def GetCorrelationnMatrix(data):
    VCV = GetVarsCovars_M(data)
    return VCV / numpy.ma.sqrt(numpy.ma.diagonal(VCV))

def Count(data):
    """
    Count
    """
    data = numpy.ma.array(data)
    return int(numpy.ma.count(data))

def Sum(data):
    """
    Sum
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return None# is string
    elif "int" in t:
        return int(numpy.ma.sum(data))
    elif 'float' in t:
        return float(numpy.ma.sum(data))
    else: 
        return None

def Minimum(data):
    """
    Minimum
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return data.sort[0] # is string
    elif "int" in t:
        return int(numpy.ma.minimum(data))
    elif 'float' in t:
        return float(numpy.ma.minimum(data))
    else: 
        return None

def Maximum(data):
    """
    Maximum
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return sort(a)[-1] # is string
    elif "int" in t:
        return int(numpy.ma.maximum(data))
    elif 'float' in t:
        return float(numpy.ma.maximum(data))
    else: 
        return None

def Range(data):
    """
    Range
    """
    return Maximum(data) - Minimum(data)

def Midrange(data):
    """
    Mid-range
    """
    maximum = Maximum(data)
    minimum = Minimum(data)
    midrange = (maximum + minimum) / 2.0
    return midrange

def Proportions(data):
    """
    Proportions
    """
    un, nu = Frequencies(data)
    nu = numpy.ma.array((nu),numpy.float)
    props = nu / nu.sum()
    return un, props
    #CumPercent(numbers) / 100.0

def Percentages(data):
    """
    Percentages
    """
    un, nu = Proportions(data)
    return un, nu * 100

def RelFreqMode(data):
    """
    Relative frequency of mode
    """
    vals, nums = UniqueVals(data)
    m = Maximum(nums)
    total = numpy.ma.sum(nums)
    modes = numpy.ma.equal(data, m)
    return modes, (m / float(total)) * 100.0
    
def sum(data):
    """
    Sum
    """
    return data.sum()

def CumSum(data):
    """
    Cumulative sum
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return None
    elif "int" in t:
        return int(cumsum(data)[-1])
    elif 'float' in t:
        return float(CumSum(data)[-1])
    else: 
        return None

def CumProduct(data):
    """
    Cumulative product
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return None
    elif "int" in t:
        return int(numpy.ma.cumprod(data)[-1])
    elif 'float' in t:
        return float(numpy.ma.cumprod(data)[-1])
    else: 
        return None

def CumPercent(data):
    """
    Cumulative percent
    """
    # assumes numbers of frequencies are sent
    return data / float(numpy.ma.sum(data)) * 100.0

def Frequencies(data):
    """
    Frequencies
    """
    uniques, numbers = UniqueVals(data)
    return uniques, numbers #, nu, nu / CumPercent(nu)

def TrimmedData(Data, Lsplit, Usplit = None):
    """
    Trim data
    """
    if (Usplit == None) or (Usplit < 0.5):
        Usplit = 1.0 - Lsplit
    Data = numpy.ma.sort(Data)
    LB = Q7(Data, Lsplit)
    UB = Q7(Data, Usplit)
    print LB, UB
    Data = Data[numpy.ma.greater(Data, LB)]
    Data = Data[numpy.ma.less(Data,UB)]
    return Data

def TrimmedMean(data, trim):
    """
    Trimmed mean
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return None
    else:
        data = TrimmedData(data, trim)
        return float(Mean(data))

def BiTrimmedMean(data, Ltrim, Utrim):
    """
    Bi-trimmed mean
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return None
    else:
        Lsplit = Ltrim / 100.0
        Usplit = Utrim / 100.0
        data = TrimmedData(data, Lsplit, Usplit)
        if "int" in t:
            return int(numpy.ma.average(data))
        elif 'float' in t:
            return float(numpy.ma.average(data))
        else:
            return None

def WinsorisedMean(Data, trim):
    """
    Winsorised mean
    """
    t = str(Data.dtype.type)
    if 'string' in t:
        return None
    else:
        try:
            if trim > 0.5:
                return None
            else:
                Data = numpy.ma.sort(Data)
                LB = Q7(Data, trim)
                UB = Q7(Data, 1.0-trim)
                idx_lower = numpy.ma.less(Data, LB)
                idx_upper = numpy.ma.greater(Data, UB)
                val_min = Data[-idx_lower][0]
                val_max = Data[-idx_upper][-1]
                Data[idx_lower] = LB 
                Data[idx_upper] = UB
                return Mean(Data)
        except:
            return

def Mean(data):
    """
    Mean
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return None
    else:
        try:
            return float(numpy.ma.average(data))
        except:
            return

def Median(data):
    """
    Median
    """
    t = str(data.dtype.type)
    if 'string' in t:
        l = numpy.ma.count(data)
        if mod(l, 2):
            # odd numbered
            return data[(l/2)+1]
        else:
            return (data[l/2], data[(l/2)+1])
    if 'float' in t or 'int' in t:
        return float(numpy.ma.median(data))
    else: 
        return None

def Mode(data):
    """
    Mode
    """
    # get list of values and frequencies
    vals, nums = Frequencies(data)
    maxes = numpy.ma.max(nums)
    idxs = data[numpy.ma.equal(nums, maxes)]
    return maxes, idxs

def Moment(data, m):
    """
    Moment
    """
    t = str(data.dtype.type)
    if 'string' in t:
        return 
    elif 'float' in t or 'int' in t:
        return (Sum((data - numpy.ma.average(data)) ** m) / Count(data))
    else:
        return 

def TukeyQuartiles(data):
    """
    Tukey's quartiles
    """
    data = numpy.ma.sort(data)
    med = Median(data)
    firstQ = numpy.ma.compress(numpy.ma.less_equal(data, med), data)
    thirdQ = numpy.ma.compress(numpy.ma.greater_equal(data, med), data)
    return Median(data[firstQ]), Median(data[thirdQ])

def MooreQuartiles(data):
    """
    Moore & McCabe's quartiles
    """
    data = numpy.ma.sort(data)
    med = Median(data)
    firstQ = numpy.ma.compress(numpy.ma.less(data, med), data)
    thirdQ = numpy.ma.compress(numpy.ma.greater(data, med), data)
    return Median(data[firstQ]), Median(data[thirdQ])

def QuantileDef(data, k, a):
    return ((1-a)*data[k-1])+(a*data[k])

def SPQuantile(data, alpha):
    """
    SPSS quantile
    """
    data = numpy.ma.sort(data)
    n = numpy.ma.count(data)
    k = int(1+(alpha*(n-1)))
    a = 1+(alpha*(n-1))-k
    Q = QuantileDef(data, k, a)
    return Q

def TradQuantile(data, alpha):
    """
    Traditional quantiles
    """
    data = numpy.ma.sort(data)
    n = numpy.ma.count(data)
    k = int(alpha * (n+1))
    a = (alpha*(n+1))-k
    Q = QuantileDef(data, k, a)
    return Q

def MidstepQuantile(data, alpha):
    """
    Mid-step quantiles
    """
    # has limits up to alpha < 0.98 and alpha > 0.02
    data = numpy.ma.sort(data)
    n = numpy.ma.count(data)
    k = int((alpha * n) + 0.5)
    a = (alpha*n)-k+0.5
    Q = QuantileDef(data, k, a)
    return Q

def Q1(data, alpha):
    """
    Quantile 1 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    k = int(alpha * n)
    g = (alpha * n) - k
    if g == 0:
        a = 0.0
    else:
        a = 1.0
    Q = QuantileDef(data, k, a)
    return Q

def Q2(data, alpha):
    """
    Quantile 2 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    k = int(alpha * n)
    g = (alpha * n) - k
    if g == 0:
        a = 0.5
    else:
        a = 1.0
    Q = QuantileDef(data, k, a)
    return Q

def Q3(data, alpha):
    """
    Quantile 3 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = -0.5
    k = int((alpha * n) + m)
    g = (alpha * n) + m - k
    a = 1.0
    if g == 0 and not k % 2:
        a = 0
    Q = QuantileDef(data, k, a)
    return Q

def Q4(data, alpha):
    """
    Quantile 4 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = 0.0
    k = int((alpha * n) + m)
    a = ((alpha * n) + m) - k
    Q = QuantileDef(data, k, a)
    return Q

def Q5(data, alpha):
    """
    Quantile 5 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = 0.5
    k = int((alpha * n) + m)
    a = ((alpha * n) + m) - k
    Q = QuantileDef(data, k, a)
    return Q

def Q6(data, alpha):
    """
    Quantile 6 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = alpha
    k = int((alpha * n) + m)
    a = ((alpha * n) + m) - k
    Q = QuantileDef(data, k, a)
    return Q

def Q7(data, alpha):
    """
    Quantile 7 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = 1.0 - alpha
    k = int((alpha * n) + m)
    a = ((alpha * n) + m) - k
    Q = QuantileDef(data, k, a)
    return Q

def Q8(data, alpha):
    """
    Quantile 8 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = (alpha + 1) / 3.0
    k = int((alpha * n) + m)
    a = ((alpha * n) + m) - k
    Q = QuantileDef(data, k, a)
    return Q

def Q9(data, alpha):
    """
    Quantile 9 from Hyndmand & Fan
    """
    n = numpy.ma.count(data)
    data = numpy.ma.sort(data)
    m = (0.25 * alpha) + (3 / 8.0)
    k = int((alpha * n) + m)
    a = ((alpha * n) + m) - k
    Q = QuantileDef(data, k, a)
    return Q

def Quartiles(data):
    """
    Quartiles (quantile 8 from Hyndman & Fan)
    """
    q1 = Q8(data, 0.25)
    q2 = Q8(data, 0.50)
    q3 = Q8(data, 0.75)
    return q1, q2, q3

def InterquartileRange(data, Qtype = "8"):
    """
    Interquartile range
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        numpy.ma.sort(data)
        minimum, median, maximum = Quartiles(data)
        return float(maximum - minimum)
    else:
        return

def SS(data):
    """
    Sum of squares
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        return float(numpy.ma.sum(data ** 2))
    else:
        return

def SSDevs(data):
    """
    Sum of squared deviations
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            tmp = data - numpy.ma.average(data)
            return float(numpy.ma.sum(tmp ** 2))
        except:
            return None
    else:
        return

def SampVar(data):
    """
    Sample variance
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            return float(SSDevs(data) / float(numpy.ma.count(data) - 1))
        except:
            return None
    else:
        return

def PopVar(data):
    """
    Population variance
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            return float(SSDevs(data) / float(Count(data)))
        except:
            return None
    else:
        return

def SampStdDev(data):
    """
    Sample standard deviation
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            return float(numpy.ma.sqrt(SampVar(data)))
        except:
            return None
    else:
        return

def PopStdDev(data):
    """
    Population standard deviation
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            return float(numpy.ma.sqrt(PopVar(data)))
        except:
            return None
    else:
        return

def CoeffVar(data):
    """
    Coefficient of variation
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            return float(SampStdDev(data) / numpy.ma.average(data))
        except:
            return None
    else:
        return

def StdErr(data):
    """
    Standard error
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            return float(SampStdDev(data) / float(numpy.math.sqrt(Count(data))))
        except:
            return None
    else:
        return

def ConfidenceIntervals(data, p=0.95):
    """
    Confidence intervals
    """
    p = 1.0 - p
    n = numpy.ma.count(data)
    m = numpy.ma.average(data)
    sd = SampStdDev(data)
    diff = (pstats.inverset(p, n-1) * sd) / numpy.math.sqrt(n)
    lb = m - diff
    ub = m + diff
    return lb, ub

def MAD(data, constant = 1.4826):
    """
    Median absolute deviation
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        med = Median(data)
        return Median(abs((data - med))) * constant
    else:
        return

def GeometricMean(data):
    """
    Geometric mean
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        return math.exp(Mean(numpy.ma.log(data))) 
    else:
        return

def HarmonicMean(data):
    """
    Harmonic mean
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        try:
            div1 = numpy.ma.divide(1.0, data)
            m1 = Mean(div1)
            hm = numpy.ma.divide(1.0, m1)
            return hm 
        except ZeroDivisionError:
            return None
    else:
        return

def MSSD(data):
    """
    Mean square of successive differences
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        val = (data[1:] - data[0:-1]) ** 2
        try:
            return float(numpy.ma.average(val) / float(numpy.ma.count(data) - 2))
        except:
            return None
    else:
        return
    
def Skewness(data):
    """
    Skewness
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        m3 = Moment(data, 3)
        m2 = Moment(data, 2)
        try:
            return float(m3 / float(m2 * numpy.math.sqrt(m2)))
        except:
            return None
    else:
        return

def Kurtosis(data):
    """
    Kurtosis
    """
    t = str(data.dtype.type)
    if 'int' in t or 'float' in t:
        m4 = Moment(data, 4)
        m22 = (Moment(data, 2) ** 2)
        try:
            return float((m4 / float(m22)))
        except:
            return None
    else:
        return

def StandardScore(data):
    """
    Standard score
    """
    av = numpy.ma.average(data)
    sd = SampStdDev(data)
    try:
        z = (data - av) / float(sd)
    except:
        z = None
    return z

def calceffectsizescontrol(d1, d2):
    return abs((numpy.ma.average(d1)-numpy.ma.average(d2))/SampStdDev(data.compressed()))

def EffectSizeControl(data):
    # first index is control second on are data
    if numpy.ma.count(numpy.ma.shape(data)) != 2:
        return
    else:
        return CalcEffectSizeControl(data[0], data[1])

def calceffectsize(d1, d2):
    Psd = numpy.math.sqrt((SampStdDev(d1)**2) + (SampStdDev(d2)**2) / 2.0)
    ES = abs((numpy.ma.average(d1)-numpy.ma.average(d2))/Psd)
    return ES

def EffectSize(data):
    s = len(numpy.ma.shape(data))
    if s != 2:
        return
    s = numpy.ma.count(data)
    if s == 2:
        return CalcEffectSize(data[0], data[1])
    else:
        # permute and apply
        n = 0
        for i in range(3, s+1):
            n = n + i
        vals = numpy.ma.zeros((n), numpy.ma.Float)
        count = 0
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                vals[count] = CalcEffectSize(data[i-1], data[j-1])
                count = count + 1
        return vals

def FiveNumber(data):
    """
    Five number summary
    """
    mn = Minimum(data)
    mx = Maximum(data)
    med = Median(data)
    quartiles = (Q8(data, 0.25), Q8(data, 0.75))
    return mn, quartiles[0], med, quartiles[1], mx

def OutliersIQR(data):
    """
    Outliers (via interquartile range)
    """
    IQR = InterquartileRange(data)
    # returns outliers defined as those outside 1.5 * IQR
    # note - this is not finished - needs the 1.5 and the centre point (mean)
    firstQ = numpy.ma.compress(numpy.ma.less(data, IQR[0]), data)
    secondQ = numpy.ma.compress(numpy.ma.greater(data, IQR[1]), data)
    outliers = numpy.ma.concatenate((firstQ, secondQ))
    step1 = numpy.ma.compress(numpy.ma.greater(data, IQR[0]), data)
    step2 = numpy.ma.compress(numpy.ma.less(step1, IQR[1]), data)
    return outliers, step2


if __name__ == '__main__':
    data = numpy.array(([1,2,3,2,1,2,3]))
    data = [1,2,3,2,1,2,3]
    data = ['a','a','b','b','c','c','c','b']
    data = "a"
    data = 2
    data = 3.14
    data = {3: "hi"}
    data = [3,2,5.65464,"hi",2,3,"hi"]
    vals, freqs = UniqueVals3(data)
    print vals
    print freqs

