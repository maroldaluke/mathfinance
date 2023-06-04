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

class HedgingPortfolio(object):


    def __init__(self, underlying, portfolio):

        # the portfolio in which we would want to hedge
        self.options = portfolio
        self.stock = underlying
        self.shares = 0
        self.bankpos = 0
        self.rebalanceinterval = 50
        self.t = []
        self.ht = []
        self.underlying = []
        self.bank = []
        self.error = []

    def model(self):

        # model both the underlying stock and options portfolio
        self.stock.model()
        self.options.model(self.stock.t, self.stock.st)

    """
    
    the following steps detail how we can accomplish a delta hedge:

    say we sell an options portfolio that has value X_t:

    then to hedge this sale at time t, we compute the delta of the portfolio,
    denoted by D_t. this will be the number of shares of the underlying that
    we hold at time t

    the remaining capital from the sale will be invested (or borrowed) in bank
    
    in summary, to hedge the sale at time t:

    - purchase D_t shares of the underlying
    - invest X_t - D_t * S_t in the bank

    (note that if X_t - D_t * S_t < 0, we are borrowing from the bank)
    
    """
    def deltahedge(self):

        # at each rebalance interval, compute portfolio delta
        duration = len(self.stock.t)
        for i in range(duration):
            # only recompute hedge if we are at proper interval
            if i % self.rebalanceinterval == 0: self.__updatehedge(i)
            # update the underlying and bank values
            self.__updatehedgeportfolio(i)

    """
    
    this method dynamically updates the option hedging portfolio. we recompute
    the delta and adjust the underlying and bank positions at each interval

    """
    def __updatehedge(self, i):

        delta = self.options.delta[i]
        self.shares = delta
        self.bankpos = self.options.price[i] - self.shares * self.stock.st[i]

    """
    
    regardless of the dynamic hedge interval, we must always still compute the
    present value of our underlying and bank positions.

    to adjust the underlying value, we can just use the new value of underlying
    for bank position, we must account for the continuous interest earned
    
    """
    def __updatehedgeportfolio(self, i):

        # update the underlying
        underlying = self.shares * self.stock.st[i]
        # update the bank pos by the interest earned over the timestep
        bank = self.bankpos * m.exp(self.stock.sigma * self.stock.timestep)
        value = underlying + bank
        # now compute the difference in portfolio and hedging portfolio
        difference = self.options.price[i] - value
        # append all of the new values
        self.t.append(self.stock.t[i])
        self.ht.append(value)
        self.underlying.append(underlying)
        self.bank.append(bank)
        self.error.append(difference)

    def graphoptions(self):

        f, ax = plt.subplots(3, 2)
        # model and plot
        self.model()
        self.deltahedge()
        # plot the stock
        ax[0, 0].set_title("Stock")
        ax[0, 0].plot(self.stock.t, self.stock.st)
        # plot the error between portfolio and hedge
        ax[0, 1].set_title("Error")
        ax[0, 1].plot(self.t, self.error)
        # plot the options portfolio
        ax[1, 0].set_title("Portfolio")
        ax[1, 0].plot(self.options.t, self.options.price)
        # plot the hedging portfolio
        ax[1, 1].set_title("Hedging Portfolio")
        ax[1, 1].plot(self.t, self.ht)
        # plot the underlying pos
        ax[2, 0].set_title("Hedge - Underlying Position")
        ax[2, 0].plot(self.t, self.underlying)
        # plot the bank pos
        ax[2, 1].set_title("Hedge - Bank Position")
        ax[2, 1].plot(self.t, self.bank)
        f.tight_layout(pad=0.25)
        plt.show()

class OptionsPortfolio(object):

    def __init__(self, securities):

        # list of all options model objects, with position
        # ex. [ (OptionModel1(), "LONG"), (OptionModel2(), "SHORT") ]
        self.options = securities
        self.t = []
        self.price = []
        self.delta = []
        self.gamma = []
        self.vega = []
        self.theta = []
        self.rho = []

    def model(self, t, st):
        
        # for each of the component options, model them
        for o in self.options:
            option = o[0]
            option.model(t, st)
        # now iterate through and add the values of each component option
        totalsteps = len(t)
        for i in range(totalsteps):
            p, d, g, v, th, r = 0, 0, 0, 0, 0, 0
            for o in self.options:
                option = o[0]
                side = o[1]
                # update values based on position side
                if (side == "LONG"): 
                    p += option.price[i]
                    d += option.delta[i]
                    g += option.gamma[i]
                    v += option.vega[i]
                    th += option.theta[i]
                    r += option.rho[i]
                elif (side == "SHORT"): 
                    p -= option.price[i]
                    d -= option.delta[i]
                    g -= option.gamma[i]
                    v -= option.vega[i]
                    th -= option.theta[i]
                    r -= option.rho[i]
            self.t.append(t[i])
            self.price.append(p)
            self.delta.append(d)
            self.gamma.append(g)
            self.vega.append(v)
            self.theta.append(th)
            self.rho.append(r)

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
        # greeks
        self.delta = []
        self.gamma = []
        self.vega = []
        self.theta = []
        self.rho = []
        # we need a model for the underlying
        self.underlying = underlying

    def model(self, t, st):

        # now compute the options prices at each time interval
        totalsteps = len(t)
        for i in range(totalsteps):
            p, d, g, v, th, r = 0, 0, 0, 0, 0, 0
            currtime, currstock = t[i], st[i]
            if (self.option == OptionModel.CALL): 
                p = self.__computecallprice(currtime, currstock)
                d = self.__computecalldelta(currtime, currstock)
                th = self.__computecalltheta(currtime, currstock)
                r = self.__computecallrho(currtime, currstock)
            elif (self.option == OptionModel.PUT): 
                p = self.__computeputprice(currtime, currstock)
                d = self.__computeputdelta(currtime, currstock)
                th = self.__computeputtheta(currtime, currstock)
                r = self.__computeputrho(currtime, currstock)
            g = self.__computegamma(currtime, currstock)
            v = self.__computevega(currtime, currstock)
            # append the necessary results
            self.t.append(currtime)
            self.price.append(p)
            self.delta.append(d)
            self.gamma.append(g)
            self.vega.append(v)
            self.theta.append(th)
            self.rho.append(r)

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
    
    def __computecalldelta(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        D = BlackScholes.computecalldelta(st, self.K, tau, self.r, self.sigma)
        return D
    
    def __computeputdelta(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        D = BlackScholes.computeputdelta(st, self.K, tau, self.r, self.sigma)
        return D

    def __computegamma(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        G = BlackScholes.computegamma(st, self.K, tau, self.r, self.sigma)
        return G
    
    def __computevega(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        V = BlackScholes.computevega(st, self.K, tau, self.r, self.sigma)
        return V
    
    def __computecalltheta(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        T = BlackScholes.computecalltheta(st, self.K, tau, self.r, self.sigma)
        return T
    
    def __computeputtheta(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        T = BlackScholes.computeputtheta(st, self.K, tau, self.r, self.sigma)
        return T
    
    def __computecallrho(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        R = BlackScholes.computecallrho(st, self.K, tau, self.r, self.sigma)
        return R
    
    def __computeputrho(self, t, st):

        tau = self.__computetimetoexpiry(t, self.T)
        R = BlackScholes.computeputrho(st, self.K, tau, self.r, self.sigma)
        return R

if __name__ == "__main__":

    # time parameters
    N = 2 * 256
    timestep = 0.1
    # stock parameters
    S0 = 50
    r = 0.05
    vol = 0.125

    def graphportfolio():

        # options parameters
        K1, K2, K3 = 50, 50, 50
        T1, T2, T3 = 2, 2, 2
        V1, V2, V3 = OptionModel.CALL, OptionModel.CALL, OptionModel.CALL

        ax = plt.axes()
        stock = StockModel(N, S0, r, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax.plot(t, st)
        # now build our options models
        om1 = OptionModel(V1, K1, T1, r, vol, stock, timestep)
        om2 = OptionModel(V2, K2, T2, r, vol, stock, timestep)
        om3 = OptionModel(V3, K3, T3, r, vol, stock, timestep)
        # model the portfolio
        pm = OptionsPortfolio([(om1, "LONG"), (om2, "LONG"), (om3, "LONG")])
        pm.model(t, st)
        # plot the result!
        ax.plot(pm.t, pm.price)
        plt.show()

    def graphgreeks():

        # options parameters
        K1, K2, K3 = 50, 60, 50
        T1, T2, T3 = 2, 2, 2
        V1, V2, V3 = OptionModel.CALL, OptionModel.CALL, OptionModel.CALL

        _, ax = plt.subplots(3, 2)
        stock = StockModel(N, S0, r, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax[0, 0].set_title("Stock Price")
        ax[0, 0].plot(t, st)
        # now build our options models
        om1 = OptionModel(V1, K1, T1, r, vol, stock, timestep)
        om2 = OptionModel(V2, K2, T2, r, vol, stock, timestep)
        om3 = OptionModel(V3, K3, T3, r, vol, stock, timestep)
        # model the portfolio
        pm = OptionsPortfolio([(om1, "LONG"), (om2, "SHORT"), (om3, "LONG")])
        pm.model(t, st)
        # plot the delta
        ax[0, 1].set_title("Delta")
        ax[0, 1].plot(pm.t, pm.delta)
        # plot the gamma
        ax[1, 0].set_title("Gamma")
        ax[1, 0].plot(pm.t, pm.gamma)
        # plot the vega
        ax[1, 1].set_title("Vega")
        ax[1, 1].plot(pm.t, pm.vega)
        # plot the theta
        ax[2, 0].set_title("Theta")
        ax[2, 0].plot(pm.t, pm.theta)
        # plot the rho
        ax[2, 1].set_title("Rho")
        ax[2, 1].plot(pm.t, pm.rho)
        plt.show()

    def demonstrateparity():

        # options parameters
        K1, K2 = 50, 50
        T1, T2 = 2, 2
        N = T1 * 256
        V1, V2 = OptionModel.CALL, OptionModel.PUT

        ax = plt.axes()
        stock = StockModel(N, S0, r, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax.plot(t, st)
        # now build our options models
        om1 = OptionModel(V1, K1, T1, r, vol, stock, timestep)
        om2 = OptionModel(V2, K2, T2, r, vol, stock, timestep)
        # model the portfolio
        pm = OptionsPortfolio([(om1, "LONG"), (om2, "SHORT")])
        pm.model(t, st)
        # plot the result!
        ax.plot(pm.t, pm.price)
        # now observe the beauty of put call parity!
        finalprice, expectedprice = pm.price[-1], st[-1] - K1
        print("Maturity: N = ", pm.t[-1])
        print("Portfolio Value: X = ", finalprice)
        print("Stock Price Minus Strike: S - K = ", expectedprice)
        print("Error: = ", finalprice - expectedprice)
        print("That's pretty damn cool!")
        plt.show()

    def demonstratedelta():

        # option parameters
        typ = OptionModel.PUT
        T = 2

        ax = plt.axes()
        stock = StockModel(N, S0, r, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax.plot(t, st)
        # observe the differences between ITM and OTM calls
        # strikes = [50, 55, 60, 65, 70, 75, 80]
        strikes = [20, 25, 30, 35, 40, 45, 50]
        for strike in strikes:
            om = OptionModel(typ, strike, T, r, vol, stock, timestep)
            om.model(t, st)
            ax.plot(om.t, om.price, label = "Strike: " + str(strike))
        plt.legend()
        plt.show()

    def plotportfolio():

        # options parameters
        K1, K2, K3 = 50, 60, 50
        T1, T2, T3 = 2, 2, 2
        V1, V2, V3 = OptionModel.CALL, OptionModel.CALL, OptionModel.PUT

        stock = StockModel(N, S0, r, vol, timestep)
        # now build our options models
        om1 = OptionModel(V1, K1, T1, r, vol, stock, timestep)
        om2 = OptionModel(V2, K2, T2, r, vol, stock, timestep)
        om3 = OptionModel(V3, K3, T3, r, vol, stock, timestep)
        # model the portfolio
        pm = OptionsPortfolio([(om1, "LONG"), (om2, "SHORT"), (om3, "LONG")])

        # now creating the hedging portfolio
        hedge = HedgingPortfolio(stock, pm)
        hedge.graphoptions()

    # demonstratedelta()
    # demonstrateparity()
    # graphgreeks()
    plotportfolio()



