# lmarolda - let's hedge some options!

from stockmodel import *
from blackscholes import *

"""

goal:
-> vanilla options portfolio (long 3 calls X, short 2 puts Y, etc.)
-> delta hedge the portfolio
-> return hedging portfolio whose value can be tracked
-> graph wealth of options portfolio vs replication portfolio
-> be able to dynamically adjust hedge at varying time intervals, and then 
   visualize the changes to effectiveness of tracking portfolio

"""

class Portfolio(object):

    def __init__(self, securities):

        # list of all security objects
        self.securities = securities

class OptionModel(object):

    CALL = 1
    PUT = 2
    daycount = 256

    def __init__(self, option, strike, expiration, r, sigma, underlying, timestep):

        # option params
        self.K = strike
        self.T = expiration
        self.r = r
        self.sigma = sigma
        # the type of the security
        self.option = option
        # time and price lists
        self.timestep = timestep
        self.t = []
        self.price = []
        # we need a model for the underlying
        self.underlying = underlying

    def model(self, t, st):

        # now compute the options prices at each time interval
        totalsteps = len(t)
        for i in range(totalsteps):
            p = 0
            currtime, currstock = t[i], st[i]
            if (self.option == OptionModel.CALL): 
                p = self.__computecallprice(currtime, currstock)
            elif (self.option == OptionModel.PUT): 
                p = self.__computeputprice(currtime, currstock)
            # append the necessary results
            self.t.append(currtime)
            self.price.append(p)

    def __computetimetoexpiry(self, t, T):

        # compute the current time in years
        curr = t / OptionModel.daycount
        tau = T - curr
        return tau

    def __computecallprice(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        P = BlackScholes.computecallprice(st, self.K, tau, self.r, self.sigma)
        return P

    def __computeputprice(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        P = BlackScholes.computeputprice(st, self.K, tau, self.r, self.sigma)
        return P

if __name__ == "__main__":

    # time parameters
    N = 256
    timestep = 0.1
    # stock parameters
    S0 = 50
    A = 0.05
    vol = 0.125
    # option parameters
    typ = OptionModel.PUT
    T = 2

    def demonstratedelta():

        ax = plt.axes()
        stock = StockModel(N, S0, A, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax.plot(t, st)
        # observe the differences between ITM and OTM calls
        # strikes = [50, 55, 60, 65, 70, 75, 80]
        strikes = [20, 25, 30, 35, 40, 45, 50]
        for strike in strikes:
            om = OptionModel(typ, strike, T, A, vol, stock, timestep)
            om.model(t, st)
            ax.plot(om.t, om.price, label = "Strike: " + str(strike))
        plt.legend()
        plt.show()

    demonstratedelta()


