# lmarolda - blackscholes

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import math as m
from scipy.stats import norm

class BlackScholes(object):

    zero = 0.000000000001

    """
    
    compute solution for call price using black scholes solution

    C = S * N(d1(tau,S)) - K * exp(-r * tau) * N(d2(tau,S))

    where

    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)
    d2 = d1 - sigma * sqrt(tau)

    S = stock price
    K = strike price
    T = expiration
    t = current time
    r = risk free rate
    sigma = volatility
    tau = T - t (time till expiration, in years)

    """
    @staticmethod
    def computecallprice(S, K, tau, r, sigma):

        # need to ensure tau does not reach 0 or below (float pt in python)
        if (tau <= 0): return max(0, S - K)
        # first compute the integral bounds
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        d2 = d1 - (sigma * m.sqrt(tau))
        # now compute the norm dist values
        n1, n2 = norm.cdf(d1), norm.cdf(d2)
        # finally we compute the call price
        C = (S * n1) - (K * m.exp(-r * tau) * n2)
        return C

    """
    
    we can use put call parity to derive the price of put option
    consider a portfolio that is long one call and short one put (same K,T)

    then our wealth follows

    X_T = max(0, S_T - K) - max(0, K - S_T)

    but we know that max(0, x) - max(0, -x) = x, thus

    X_T = S_T - K

    then discounting back brings us to the result

    C_t - P_t = S_t - K * exp(-r * tau)

    so our put price is:

    P_t = C_t + K * exp(-r * tau) - S_t
    
    """
    @staticmethod
    def computeputprice(S, K, tau, r, sigma):

        # first compute the call price
        C = BlackScholes.computecallprice(S, K, tau, r, sigma)
        # then the discounted strike
        discountedK = K * m.exp(-r * tau)
        P = C + discountedK - S
        return P

    """
    
    for a call, we have the following closed form solution for delta:
    
    dC/dS = N(d1)

    where
    
    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)

    """
    @staticmethod
    def computecalldelta(S, K, tau, r, sigma):

        # if tau has gone negative that means we are at expiration (float pt)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        delta = norm.cdf(d1)
        return delta
    
    @staticmethod
    def __calldeltaexpiry(S, K):

        if (S > K): return 1
        elif (S == K): return 0.5
        else: return 0
    
    """
    
    for a put, we have the following closed form solution for delta:
    
    dP/dS = -N(-d1) = N(d1) - 1

    where
    
    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)

    """
    @staticmethod
    def computeputdelta(S, K, tau, r, sigma):

        # if tau has gone negative that means we are at expiration (float pt)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        delta = norm.cdf(d1) - 1
        return delta
    
    @staticmethod
    def __putdeltaexpiry(S, K):

        if (S < K): return -1
        elif (S == K): return -0.5
        else: return 0

    """
    
    for a call/put, we have the following closed form solution for gamma:
    
    d^2V/dS^2 = (1 / (S * sigma * sqrt(tau))) * N'(d1)

    where
    
    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)
    
    """
    @staticmethod
    def computegamma(S, K, tau, r, sigma):

        # if tau has gone negative that means we are at expiration (float pt)
        if (tau <= 0): tau = BlackScholes.zero
        factor = 1 / (S * sigma * m.sqrt(tau))
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        G = factor * norm.pdf(d1)        
        return G

    """
    
    for a call/put, we have the following closed form solution for gamma:

    dV/d(sigma) = S * N'(d1) * sqrt(tau)

    where
    
    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)

    """
    @staticmethod
    def computevega(S, K, tau, r, sigma):

        # if tau has gone negative that means we are at expiration (float pt)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        # now compute the vega
        V = S * norm.pdf(d1) * m.sqrt(tau)
        return V

    """

    for a call, we have the following closed form solution for theta:
    
    dC/dt = -r * K * exp(-r * tau) * N(d2) 
            - (sigma * S) / (2 * sqrt(tau)) * N'(d1)

    where

    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)
    d2 = d1 - sigma * sqrt(tau)
    
    """
    @staticmethod
    def computecalltheta(S, K, tau, r, sigma):

        # need to ensure tau does not reach 0 or below (float pt in python)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        d2 = d1 - (sigma * m.sqrt(tau))
        # now compute the theta
        n, p = norm.cdf(d2), norm.pdf(d1)
        T1 = -r * K * m.exp(-r * tau) * n
        T2 = ((sigma * S) / (2 * m.sqrt(tau))) * p
        T = T1 - T2
        return T
    
    """

    for a put, we have the following closed form solution for theta:
    
    dC/dt = r * K * exp(-r * tau) * N(-d2) 
            - (sigma * S) / (2 * sqrt(tau)) * N'(d1)

    where

    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)
    d2 = d1 - sigma * sqrt(tau)
    
    """
    @staticmethod
    def computeputtheta(S, K, tau, r, sigma):

        # need to ensure tau does not reach 0 or below (float pt in python)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        d2 = d1 - (sigma * m.sqrt(tau))
        # now compute the theta
        n, p = norm.cdf(-d2), norm.pdf(d1)
        T1 = r * K * m.exp(-r * tau) * n
        T2 = ((sigma * S) / (2 * m.sqrt(tau))) * p
        T = T1 - T2
        return T
    
    """
    
    for a call, we have the following closed form solution for rho:
    
    dC/dr = K * tau * exp(-r * tau) * N(d2) 
    
    """
    @staticmethod
    def computecallrho(S, K, tau, r, sigma):

        # need to ensure tau does not reach 0 or below (float pt in python)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        d2 = d1 - (sigma * m.sqrt(tau))
        # now compute the theta
        N2 = norm.cdf(d2)
        R = K * tau * m.exp(-r * tau) * N2
        return R

    """
    
    for a put, we have the following closed form solution for rho:
    
    dC/dr = -K * tau * exp(-r * tau) * N(-d2) 
    
    """
    @staticmethod
    def computeputrho(S, K, tau, r, sigma):

        # need to ensure tau does not reach 0 or below (float pt in python)
        if (tau <= 0): tau = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        d2 = d1 - (sigma * m.sqrt(tau))
        # now compute the theta
        N2 = norm.cdf(-d2)
        R = -K * tau * m.exp(-r * tau) * N2
        return R



