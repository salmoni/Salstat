"""
probabilities.py
A set of probability functions for Salstat

"""

import math

###########################
## Probability functions ##
###########################

def chisqprob(chisq,df):
    """
    Returns the (1-tailed) probability value associated with the provided
    chi-square value and df.  Adapted from chisq.c in Gary Perlman's |Stat.
    
    Usage:   chisqprob(chisq,df)
    """
    BIG = 20.0
    def ex(x):
	BIG = 20.0
	if x < -BIG:
	    return 0.0
	else:
	    return math.exp(x)

    if chisq <=0 or df < 1:
	return 1.0
    a = 0.5 * chisq
    if df%2 == 0:
	even = 1
    else:
	even = 0
    if df > 1:
	y = ex(-a)
    if even:
	s = y
    else:
	s = 2.0 * zprob(-math.sqrt(chisq))
    if (df > 2):
	chisq = 0.5 * (df - 1.0)
	if even:
	    z = 1.0
	else:
	    z = 0.5
	if a > BIG:
	    if even:
		e = 0.0
	    else:
		e = math.log(math.sqrt(math.pi))
	    c = math.log(a)
	    while (z <= chisq):
		e = math.log(z) + e
		s = s + ex(c*z-a-e)
		z = z + 1.0
	    return s
	else:
	    if even:
		e = 1.0
	    else:
		e = 1.0 / math.sqrt(math.pi) / math.sqrt(a)
		c = 0.0
		while (z <= chisq):
		    e = e * (a/float(z))
		    c = c + e
		    z = z + 1.0
		return (c*y+s)
    else:
	return s

def inversechi(prob, df):
    """This function calculates the inverse of the chi square function. Given
    a p-value and a df, it should approximate the critical value needed to 
    achieve these functions. Adapted from Gary Perlmans critchi function in
    C. Apologies if this breaks copyright, but no copyright notice was 
    attached to the relevant file."""
    minchisq = 0.0
    maxchisq = 99999.0
    chi_epsilon = 0.000001
    if (prob <= 0.0):
        return maxchisq
    elif (prob >= 1.0):
        return 0.0
    chisqval = df / math.sqrt(prob)
    while ((maxchisq - minchisq) > chi_epsilon):
        if (chisqprob(chisqval, df) < prob):
            maxchisq = chisqval
        else:
            minchisq = chisqval
        chisqval = (maxchisq + minchisq) * 0.5
    return chisqval

def erfcc(x):
    """
    Returns the complementary error function erfc(x) with fractional
    error everywhere less than 1.2e-7.  Adapted from Numerical Recipies.
    
    Usage:   erfcc(x)
    """
    z = abs(x)
    t = 1.0 / (1.0+0.5*z)
    ans = t * math.exp(-z*z-1.26551223 + t*(1.00002368+t*(0.37409196+t* \
                                    (0.09678418+t*(-0.18628806+t* \
                                    (0.27886807+t*(-1.13520398+t* \
                                    (1.48851587+t*(-0.82215223+t* \
                                    0.17087277)))))))))
    if x >= 0:
        return ans
    else:
        return 2.0 - ans

def zprob(z):
    """
    Returns the area under the normal curve 'to the left of' the given z value.
    Thus, 
    for z<0, zprob(z) = 1-tail probability
    for z>0, 1.0-zprob(z) = 1-tail probability
    for any z, 2.0*(1.0-zprob(abs(z))) = 2-tail probability
    Adapted from z.c in Gary Perlman's |Stat.
    
    Usage:   zprob(z)
    """
    Z_MAX = 6.0    # maximum meaningful z-value
    if z == 0.0:
	x = 0.0
    else:
	y = 0.5 * math.fabs(z)
	if y >= (Z_MAX*0.5):
	    x = 1.0
	elif (y < 1.0):
	    w = y*y
	    x = ((((((((0.000124818987 * w
			-0.001075204047) * w +0.005198775019) * w
		      -0.019198292004) * w +0.059054035642) * w
		    -0.151968751364) * w +0.319152932694) * w
		  -0.531923007300) * w +0.797884560593) * y * 2.0
	else:
	    y = y - 2.0
	    x = (((((((((((((-0.000045255659 * y
			     +0.000152529290) * y -0.000019538132) * y
			   -0.000676904986) * y +0.001390604284) * y
			 -0.000794620820) * y -0.002034254874) * y
		       +0.006549791214) * y -0.010557625006) * y
		     +0.011630447319) * y -0.009279453341) * y
		   +0.005353579108) * y -0.002141268741) * y
		 +0.000535310849) * y +0.999936657524
    if z > 0.0:
	prob = ((x+1.0)*0.5)
    else:
	prob = ((1.0-x)*0.5)
    return prob


def ksprob(alam):
    """
    Computes a Kolmolgorov-Smirnov t-test significance level.  Adapted from
    Numerical Recipies.

    Usage:   ksprob(alam)
    """
    fac = 2.0
    sum = 0.0
    termbf = 0.0
    a2 = -2.0*alam*alam
    for j in range(1,201):
	term = fac*math.exp(a2*j*j)
	sum = sum + term
	if math.fabs(term)<=(0.001*termbf) or math.fabs(term)<(1.0e-8*sum):
	    return sum
	fac = -fac
	termbf = math.fabs(term)
    return 1.0             # Get here only if fails to converge; was 0.0!!


def fprob (dfnum, dfden, F):
    """
    Returns the (1-tailed) significance level (p-value) of an F
    statistic given the degrees of freedom for the numerator (dfR-dfF) and
    the degrees of freedom for the denominator (dfF).
    
    Usage:   fprob(dfnum, dfden, F)   where usually dfnum=dfbn, dfden=dfwn
    """
    p = betai(0.5*dfden, 0.5*dfnum, dfden/float(dfden+dfnum*F))
    return p

def tprob(df, t):
    return betai(0.5*df,0.5,float(df)/(df+t*t))

def inversef(prob, df1, df2):
    """This function returns the f value for a given probability and 2 given
    degrees of freedom. It is an approximation using the fprob function.
    Adapted from Gary Perlmans critf function - apologies if copyright is 
    broken, but no copyright notice was attached """
    f_epsilon = 0.000001
    maxf = 9999.0
    minf = 0.0
    if (prob <= 0.0) or (prob >= 1.0):
        return 0.0
    fval = 1.0 / prob
    while (abs(maxf - minf) > f_epsilon):
        if fprob(fval, df1, df2) < prob:
            maxf = fval
        else:
            minf = fval
        fval = (maxf + minf) * 0.5
    return fval

def inverset(prob, df):
    """
    Returns an estimate of t for a given df and p-value
    """
    f_epsilon


def betacf(a,b,x):
    """
    This function evaluates the continued fraction form of the incomplete
    Beta function, betai.  (Adapted from: Numerical Recipies in C.)
    
    Usage:   betacf(a,b,x)
    """
    ITMAX = 200
    EPS = 3.0e-7

    bm = az = am = 1.0
    qab = a+b
    qap = a+1.0
    qam = a-1.0
    bz = 1.0-qab*x/qap
    for i in range(ITMAX+1):
        em = float(i+1)
        tem = em + em
        d = em*(b-em)*x/((qam+tem)*(a+tem))
        ap = az + d*am
        bp = bz+d*bm
        d = -(a+em)*(qab+em)*x/((qap+tem)*(a+tem))
        app = ap+d*az
        bpp = bp+d*bz
        aold = az
        am = ap/bpp
        bm = bp/bpp
        az = app/bpp
        bz = 1.0
        if (abs(az-aold)<(EPS*abs(az))):
            return az
    #print 'a or b too big, or ITMAX too small in Betacf.'


def gammln(xx):
    """
    Returns the gamma function of xx.
    Gamma(z) = Integral(0,infinity) of t^(z-1)exp(-t) dt.
    (Adapted from: Numerical Recipies in C.)

    Usage:   gammln(xx)
    """

    coeff = [76.18009173, -86.50532033, 24.01409822, -1.231739516,
                0.120858003e-2, -0.536382e-5]
    x = xx - 1.0
    tmp = x + 5.5
    tmp = tmp - (x+0.5)*math.log(tmp)
    ser = 1.0
    for j in range(len(coeff)):
        x = x + 1
        ser = ser + coeff[j]/x
    return -tmp + math.log(2.50662827465*ser)


def betai(a,b,x):
    """
    Returns the incomplete beta function:

    I-sub-x(a,b) = 1/B(a,b)*(Integral(0,x) of t^(a-1)(1-t)^(b-1) dt)

    where a,b>0 and B(a,b) = G(a)*G(b)/(G(a+b)) where G(a) is the gamma
    function of a.  The continued fraction formulation is implemented here,
    using the betacf function.  (Adapted from: Numerical Recipies in C.)

    Usage:   betai(a,b,x)
    """
    if (x<0.0 or x>1.0):
        raise ValueError, 'Bad x in lbetai'
    if (x==0.0 or x==1.0):
        bt = 0.0
    else:
        bt = math.exp(gammln(a+b)-gammln(a)-gammln(b)+a*math.log(x)+b*
                        math.log(1.0-x))
    if (x<(a+1.0)/(a+b+2.0)):
        return bt*betacf(a,b,x)/float(a)
    else:
        return 1.0-bt*betacf(b,a,1.0-x)/float(b)




