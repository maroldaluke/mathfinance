# lmarolda - blackscholes

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import math as m
from scipy.stats import norm

class Error(object):

    def __init__(self):

        self.num = -1
        self.message = "Error: Unsupported Option Type"

class BlackScholes(object):

    zero = 0.000000000000001

    ### Pricing ###

    @staticmethod
    def price(typ, S, K, T, r, q, sigma):

        # need to ensure T does not reach 0 or below (float pt in python)
        if (T <= 0):
            if typ == "C": return max(0, S - K)
            elif typ == "P": return max(0, K - S)
            else: return Error()
        # first compute the integral bounds
        coef = 1 / (sigma * m.sqrt(T))
        d1 = coef * (m.log(S / K) + (r - q + (sigma ** 2 / 2)) * T)
        d2 = d1 - (sigma * m.sqrt(T))
        # finally we compute the option price
        if typ == "C": 
            price = (S * m.exp(-q * T) * norm.cdf(d1)) - (K * m.exp(-r * T) * norm.cdf(d2))
        elif typ == "P": 
            price = (K * m.exp(-r * T) * norm.cdf(-d2)) - (S * m.exp(-q * T) * norm.cdf(-d1))
        else: price = Error()

        return price
    
    ### First Order Greeks ###

    @staticmethod
    def delta(typ, S, K, T, r, q, sigma):

        if (T <= 0): T = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(T))
        d1 = coef * (m.log(S / K) + (r - q + (sigma ** 2 / 2)) * T)
        # now compute delta
        if typ == "C": delta = m.exp(-q * T) * norm.cdf(d1)
        elif typ == "P": delta = -m.exp(-q * T) * norm.cdf(-d1)
        else: delta = Error()

        return delta
    
    @staticmethod
    def vega(typ, S, K, T, r, q, sigma):

        if (T <= 0): T = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(T))
        d1 = coef * (m.log(S / K) + (r - q + (sigma ** 2 / 2)) * T)
        # now compute the vega
        V = S * m.exp(-q * T) * norm.pdf(d1) * m.sqrt(T)

        return V

    @staticmethod
    def theta(typ, S, K, T, r, q, sigma):

        if (T <= 0): T = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(T))
        d1 = coef * (m.log(S / K) + (r - q + (sigma ** 2 / 2)) * T)
        d2 = d1 - (sigma * m.sqrt(T))
        # now compute the theta
        T1 = (-m.exp(-q * T) * S * norm.pdf(d1) * sigma) / (2 * m.sqrt(T))
        C2 = r * K * m.exp(-r * T)
        C3 = q * S * m.exp(-q * T)
        if typ == "C": theta = T1 - C2 * norm.cdf(d2) + C3 * norm.cdf(d1)
        elif typ == "P": theta = T1 + C2 * norm.cdf(-d2) - C3 * norm.cdf(-d1)
        else: theta = Error()

        return theta
    
    @staticmethod
    def rho(typ, S, K, T, r, q, sigma):

        if (T <= 0): T = BlackScholes.zero
        coef = 1 / (sigma * m.sqrt(T))
        d1 = coef * (m.log(S / K) + (r - q + (sigma ** 2 / 2)) * T)
        d2 = d1 - (sigma * m.sqrt(T))
        # now compute the rho
        if typ == "C": rho = K * T * m.exp(-r * T) * norm.cdf(d2)
        elif typ == "P": rho = -K * T * m.exp(-r * T) * norm.cdf(-d2)
        else: rho = Error()

        return rho
    
    ### Second Order Greeks ###

    @staticmethod
    def computegamma(S, K, tau, r, sigma):

        # if tau has gone negative that means we are at expiration (float pt)
        if (tau <= 0): tau = BlackScholes.zero
        factor = 1 / (S * sigma * m.sqrt(tau))
        coef = 1 / (sigma * m.sqrt(tau))
        d1 = coef * (m.log(S / K) + (r + (sigma ** 2 / 2)) * tau)
        G = factor * norm.pdf(d1)        
        return G
    
class Option(object):

    def __init__(self, typ, side, K, T, r, q, sigma):

        self.typ = typ
        self.side = side
        self.K = K
        self.T = T
        self.r = r
        self.q = q
        self.sigma = sigma
        
class Pricer(object):

    """
    
    strategy: list of option objects

    """

    @staticmethod
    def plot(strategy, plots = ['payoff', 'price', 'delta', 'vega']):

        numplots = len(plots)

        f, ax = plt.subplots(numplots)
        f.set_figheight(2 * numplots)
        f.set_figwidth(7)

        for i in range(numplots):

            plottype = plots[i]
            if plottype == "payoff": x, y = Pricer.computepayoff(strategy)
            elif plottype == "price": x, y = Pricer.computeprice(strategy)
            elif plottype == "delta": x, y = Pricer.computegreek(strategy, "delta")
            elif plottype == "vega": x, y = Pricer.computegreek(strategy, "vega")
            elif plottype == "theta": x, y = Pricer.computegreek(strategy, "theta")
            elif plottype == "rho": x, y = Pricer.computegreek(strategy, "rho")

            if numplots == 1: 
                ax.plot(x, y, label = plottype)
                ax.legend()
            else: 
                ax[i].plot(x, y, label = plottype)
                ax[i].legend()

        plt.show()

    @staticmethod
    def computepayoff(strategy):

        values = []
        maxspot = 2 * Pricer.__maxstrike(strategy) + 1
        spots = [ s for s in range(1, maxspot) ]

        for S in spots:
            value = 0
            for o in strategy:
                p = BlackScholes.price(o.typ, S, o.K, 0, o.r, o.q, o.sigma)
                if o.side == "Long": value += p
                elif o.side == "Short": value -= p
            values.append(value)

        return (spots, values)

    @staticmethod
    def computeprice(strategy):

        values = []
        maxspot = 2 * Pricer.__maxstrike(strategy) + 1
        spots = [ s for s in range(1, maxspot) ]

        for S in spots:
            value = 0
            for o in strategy:
                p = BlackScholes.price(o.typ, S, o.K, o.T, o.r, o.q, o.sigma)
                if o.side == "Long": value += p
                elif o.side == "Short": value -= p
            values.append(value)

        return (spots, values)
    
    @staticmethod
    def computegreek(strategy, greek):

        values = []
        maxspot = 2 * Pricer.__maxstrike(strategy) + 1
        spots = [ s for s in range(1, maxspot) ]

        for S in spots:
            value = 0
            for o in strategy:
                g = Pricer.__getgreek(S, o, greek)
                if o.side == "Long": value += g
                elif o.side == "Short": value -= g
            values.append(value)

        return (spots, values)
    
    @staticmethod
    def __getgreek(S, o, greek):

        g = 0
        if greek == "delta":
            g = BlackScholes.delta(o.typ, S, o.K, o.T, o.r, o.q, o.sigma)
        elif greek == "vega":
            g = BlackScholes.vega(o.typ, S, o.K, o.T, o.r, o.q, o.sigma)
        elif greek == "theta":
            g = BlackScholes.theta(o.typ, S, o.K, o.T, o.r, o.q, o.sigma)
        elif greek == "rho":
            g = BlackScholes.rho(o.typ, S, o.K, o.T, o.r, o.q, o.sigma)

        return g

    @staticmethod
    def __maxstrike(strategy):

        maxstrike = -1
        for option in strategy:
            if option.K >= maxstrike: maxstrike = option.K
        return maxstrike
    
if __name__ == "__main__":

    T = 1
    r = 0.05
    q = 0.01
    sigma = 0.15

    C = Option("C", "Long", 80, T, r, q, sigma)
    P = Option("C", "Short", 120, T, r, q, sigma)

    strategy = [C, P]
    Pricer.plot(strategy)