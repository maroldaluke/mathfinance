# first attempt at stock model (GBM)

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import math as m
from scipy.stats import bernoulli

class BrownianMotion(object):

    def __init__(self, timestep = 0.001):

        self.p = 0.5
        self.timestep = timestep
        self.size = m.sqrt(self.timestep)
        self.t = []
        self.wt = []

    @staticmethod
    def plotInstances(num, iterations):

        bm = BrownianMotion()
        ax = plt.axes()
        for i in range(num): 
            bm.simulate(iterations)
            ax.plot(bm.t, bm.wt)
            bm.clear()
        plt.show()

    def iterate(self):

        (t,wt) = self.__generatestep()
        self.t.append(t)
        self.wt.append(wt)

    def simulate(self, num):

        steps = m.floor(num / self.timestep)
        for i in range(steps): self.iterate()

    def clear(self):

        self.t.clear()
        self.wt.clear()

    def plotBM(self):

        ax = plt.axes()
        ax.plot(self.t, self.wt)
        plt.show()

    def __generatestep(self):

        r = bernoulli.rvs(self.p)
        step = self.size if r == 1 else -self.size
        # determine next elem to add to list
        nt = self.t[-1] + self.timestep if len(self.t) > 0 else self.timestep
        nwt = self.wt[-1] + step if len(self.wt) > 0 else step
        return (nt,nwt)

"""

simple stock model St ~ GBM(alpha, sigma)
alpha: drift parameter
sigma: volatility parameter

"""
class StockModel(object):

    def __init__(self, N, s0, drift, vol, timestep = 0.001):

        self.N = N
        self.timestep = timestep
        self.t = [0]
        self.s0 = s0
        self.st = [s0]
        self.bm = BrownianMotion(timestep)
        # automatically normalize the alpha / sigma
        self.alpha, self.sigma = StockModel.normalize(N, drift, vol)

    @staticmethod
    def plotstock(num, iterations, s0, drift, vol, timestep):

        ax = plt.axes()
        for i in range(num): 
            s = StockModel(iterations, s0, drift, vol, timestep)
            s.simulate(iterations)
            ax.plot(s.t, s.st)
        plt.show()

    @staticmethod
    def normalize(n, returnrate, volatility):

        rate = returnrate / n
        vol = volatility / m.sqrt(n)
        return (rate, vol)

    def model(self):

        self.simulate(self.N)
        return (self.t, self.st)

    def simulate(self, totaltime):

        steps = m.floor(totaltime / self.timestep)
        for i in range(steps): self.iterate()

    def iterate(self):

        (t,st) = self.__generatestep()
        self.t.append(t)
        self.st.append(st)

    """
    
    stock follows following distribution:
    St = S0 * exp( (alpha - sigma^2 / 2) * t + sigma * Wt )

    """
    def __generatestep(self):

        # first iterate the brownian motion
        self.bm.iterate()
        nt = self.bm.t[-1]
        nwt = self.bm.wt[-1]
        # now compute and update the stock price
        expg = ( ( self.alpha - ( (self.sigma ** 2) / 2 ) ) * nt)
        ito = self.sigma * nwt
        nst = self.s0 * m.exp(expg + ito)
        return (nt, nst)

"""

obtain annualized data for the following:
mean return rate
expected volatility (implied, historical, etc.)

A = annual return rate
S = annual volatility

ex.
A = 0.05 -> A / N = 0.05 / 100 = 0.0005
S = 0.10 -> S / sqrt(N) = 0.10 / 10 = 0.01

"""

if __name__ == "__main__":

    I = 5
    N = 365
    S0 = 100
    A = 0.05
    S = 0.15
    timestep = 0.01

    """
    stock = StockModel(N, S0, A, S)
    (t, st) = stock.model()
    """

    StockModel.plotstock(I, N, S0, A, S, timestep)