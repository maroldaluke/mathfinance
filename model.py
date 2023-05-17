from stockmodel import *
from volatility import *

class Model(object):

    def __init__(self):

        self.daycount = 256
        self.iterations = 5

    """
    
    note: because we are following arbitrage free market assumption, under the
    RNM the stock follows ~ GBM(r, sigma), ie. the mean return rate is equal to
    the risk free rate

    """
    def modelstock(self, C, S0, K, T, t, r):
        # first get the implied vol
        vol = ImpliedVolatility()
        iv = vol.computevolfast(C, S0, K, T, t, r)
        # now model the stock
        N = (T - t) * self.daycount
        alpha, sigma = StockModel.normalize(N, r, iv)
        print("Implied Volatility: ", iv)
        print("Number of Days (N): ", N)
        print("Annualized Return: ", r)
        print("Normalized Alpha: ", alpha)
        print("Annualized Volatility", iv)
        print("Normalized Sigma", sigma)
        StockModel.plotstock(self.iterations, N, S0, alpha, sigma)

if __name__ == "__main__":

    # establish our model parameters
    S0 = 50
    K = 70
    T = 2
    t = 0
    r = 0.05
    vol = 0.07
    # first compute a call price which can be used to find the volatility
    C = ImpliedVolatility.computeprice(S0, K, T, t, r, vol)
    print("Call Price: ", C)
    # now we can actually model the stock
    model = Model()
    model.modelstock(C, S0, K, T, t, r)