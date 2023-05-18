# compute implied vol

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import math as m
from scipy.stats import norm

class ImpliedVolatility(object):

    def __init__(self):

        self.error = 0.000000001
        self.increment = self.error / 100

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
    tau = T - t (time till expiration)

    """
    @staticmethod
    def computeprice(S, K, T, t, r, sigma):

        tau = T - t
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
    
    we can improve the calculation of implied vol by utilizing the greek
    vega of the bs solution. it is defined as follows:

    vega ~= d(C) / d(sigma) = S * N'(d1) * sqrt(tau)

    where

    tau = T - t
    d1 = (1 / (sigma * sqrt(tau))) * (ln(S/K) + (r + sigma^2 / 2) * tau)

    """
    @staticmethod
    def computevega(S, K, T, t, r, sigma):

        tau = T - t
        # first compute the integral bounds
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        # now compute the vega
        v = S * norm.pdf(d1) * m.sqrt(tau)
        return v

    """
    
    credit: Brenner and Subrahmanyam (1988)
    closed form estimate of implied vol, in the following form:

    sigma ~= sqrt(2pi / tau) * (C / S)

    """
    @staticmethod
    def initialguess(C, S, T, t):

        tau = T - t
        sigma = m.sqrt((2 * m.pi) / tau) * (C / S)
        return sigma

    """
    
    note the following: options prices increase with increasing vol
    thus if our computed value is higher than desired, we want to lower our
    sigma value
    similarly, if our computed value is lower than desired, increase sigma

    """
    def computevol(self, C, S, K, T, t, r):

        increase = True
        # first thing we do is compute the intial guess for IV
        sigma = self.initialguess(C, S, T, t)
        # now update sigma until our recorded call price matches BS result
        print("Computing Implied Vol...")
        while (1):
            computed = self.computeprice(S, K, T, t, r, sigma)
            difference = computed - C
            # if we have reached a sufficient value, break out
            if (abs(difference) <= self.error):
                return sigma
            # otherwise, update sigma and try again
            if (difference > 0): increase = False
            else: increase = True
            sigma = self.__updatesigma(sigma, increase)
            # print("New Sigma: ", sigma)

    """
    
    this algorithm computes the implied vol in a more efficient manner using
    the following difference equation, which follows from newton's method, when
    attempting to find values xN such that f(xN) = 0:

    recall, x1 = x0 - f(x0) / f'(x0)

    we can apply this to the closed form BS equation, BS(sigma)
    note we want to minimize the difference between the traded call price and 
    our computed value. ie, we want BS(sigma) - C = 0
    therefore, let f = BS(sigma) - C

    sigma1 = sigma0 - [ BS(sigma0) - C ] / BS'(sigma0)

    and we know the partial derivative of BS(sigma) wrt sigma is vega. thus

    sigma_N+1 = sigma_N - [ BS(sigma_N) - C ] / vega(sigma_N)
    
    """
    def computevolfast(self, C, S, K, T, t, r):

        # first thing we do is compute the intial guess for IV
        sigma = self.initialguess(C, S, T, t)
        # now update sigma until our recorded call price matches BS result
        print("Computing Implied Vol...")
        count = 0
        while (1):
            computed = self.computeprice(S, K, T, t, r, sigma)
            difference = computed - C
            # if we have reached a sufficient value, break out
            if (abs(difference) <= self.error):
                return sigma
            # otherwise, compute a new sigma
            if (difference > 0): increase = False
            else: increase = True
            sigma = self.__updatesigmafast(difference, S, K, T, t, r, sigma)
            # if sigma is -1, that means we have to use slow update
            if (sigma == -1): sigma = self.__updatesigma(sigma, increase)
            print("New Sigma: ", sigma)

    def __updatesigma(self, sigma, increase):

        newsig = 0
        if (increase): newsig = sigma + self.increment
        else: newsig = sigma - self.increment
        return newsig 
    
    """
    
    sigma_N+1 = sigma_N - [ BS(sigma_N) - C ] / vega(sigma_N)
    
    """
    def __updatesigmafast(self, difference, S, K, T, t, r, sigma):

        newsig = 0
        # need to compute vega
        vega = self.computevega(S, K, T, t, r, sigma)
        # cannot apply the fast algo if vega is 0!
        if (vega == 0): return -1
        # now with newton's method
        newsig = sigma - difference / vega
        return newsig 

if __name__ == "__main__":

    S = 42
    K = 70
    T = 10
    t = 5
    r = 0.05
    sigma = 0.11435117637

    C = ImpliedVolatility.computeprice(S, K, T, t, r, sigma)
    print("Call Price: ", C)
    iv = ImpliedVolatility()
    newsig = iv.computevolfast(C, S, K, T, t, r)
    print("Implied Volatility: ", newsig)
