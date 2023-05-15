# compute implied vol

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import math as m
from scipy.stats import norm

class ImpliedVolatility(object):

    def __init__(self):

        self.error = 0.0001
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

    def __updatesigma(self, sigma, increase):

        newsig = 0
        if (increase): newsig = sigma + self.increment
        else: newsig = sigma - self.increment
        return newsig 

if __name__ == "__main__":

    S = 42
    K = 50
    T = 10
    t = 5
    r = 0.05
    sigma = 0.06783

    C = ImpliedVolatility.computeprice(S, K, T, t, r, sigma)
    print("Call Price: ", C)
    iv = ImpliedVolatility()
    newsig = iv.computevol(C, S, K, T, t, r)
    print("Implied Volatility: ", newsig)
