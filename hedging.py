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

    # demonstratedelta()
    # demonstrateparity()
    graphgreeks()


