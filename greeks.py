# more greek stuff

from hedging import *
from blackscholes import *

class VanillaOption(object):

    def __init__(self, typ, strike, expiry, side):

        self.typ = typ
        self.strike = strike
        self.expiry = expiry
        self.side = side

class Greek(object):

    def __init__(self, r, sigma):

        self.r = r
        self.sigma = sigma

    def gammaspotstructure_downandoutput(self):

        # options parameters for a put spread
        V1, V2, V3 = "CALL", "CALL", "PUT"
        S1, S2, S3 = "LONG", "SHORT", "LONG"
        K1, K2, K3 = 40, 50, 80 
        maxstrike = max(K1, K2, K3)
        T1, T2, T3 = 1, 1, 1
        o1 = VanillaOption(V1, K1, T1, S1)
        o2 = VanillaOption(V2, K2, T2, S2)
        o3 = VanillaOption(V3, K3, T3, S3)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1, o2, o3 ]
        self.gammaspotstructure(portfolio, maxstrike)

    def vegaspotstructure_riskreversal(self):

        # options parameters for a put spread
        V1, V2 = "PUT", "CALL"
        S1, S2 = "SHORT", "LONG"
        K1, K2 = 40, 60 
        maxstrike = max(K1, K2)
        T1, T2 = 1, 1
        o1 = VanillaOption(V1, K1, T1, S1)
        o2 = VanillaOption(V2, K2, T2, S2)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1, o2 ]
        self.vegaspotstructure(portfolio, maxstrike)

    def gammaspotstructure_callspread(self):

        # options parameters for a put spread
        V1, V2 = "CALL", "PUT"
        S1, S2 = "LONG", "SHORT"
        K1, K2 = 40, 50
        maxstrike = max(K1, K2)
        T1, T2 = 1, 1
        o1 = VanillaOption(V1, K1, T1, S1)
        o2 = VanillaOption(V2, K2, T2, S2)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1, o2 ]
        self.gammaspotstructure(portfolio, maxstrike)

    def gammaspotstructure_putspread(self):

        # options parameters for a put spread
        V1, V2 = "CALL", "PUT"
        S1, S2 = "SHORT", "LONG"
        K1, K2 = 40, 50
        maxstrike = max(K1, K2)
        T1, T2 = 1, 1
        o1 = VanillaOption(V1, K1, T1, S1)
        o2 = VanillaOption(V2, K2, T2, S2)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1, o2 ]
        self.gammaspotstructure(portfolio, maxstrike)

    def gammaspotstructure_call(self):

        # options parameters for a put spread
        V1 = "CALL"
        S1 = "LONG"
        K1 = 50
        maxstrike = K1
        T1 = 1
        o1 = VanillaOption(V1, K1, T1, S1)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1 ]
        self.gammaspotstructure(portfolio, maxstrike)

    def vegaspotstructure_call(self):

        # options parameters for a put spread
        V1 = "CALL"
        S1 = "LONG"
        K1 = 100
        maxstrike = K1
        T1 = 1
        o1 = VanillaOption(V1, K1, T1, S1)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1 ]
        self.vegaspotstructure(portfolio, maxstrike)

    def vannaspotstructure_callspread(self):

        # options parameters for a put spread
        V1, V2 = "CALL", "CALL"
        S1, S2 = "LONG", "SHORT"
        K1, K2 = 50, 60
        maxstrike = K2
        T1, T2 = 1, 1
        o1 = VanillaOption(V1, K1, T1, S1)
        o2 = VanillaOption(V2, K2, T2, S2)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1, o2 ]
        self.vannaspotstructure(portfolio, maxstrike)

    def vannaspotstructure_call(self):

        # options parameters for a put spread
        V1 = "CALL"
        S1 = "LONG"
        K1 = 50
        maxstrike = K1
        T1 = 1
        o1 = VanillaOption(V1, K1, T1, S1)
        # any arbitrary structure of long/short puts and calls
        portfolio = [ o1 ]
        self.vannaspotstructure(portfolio, maxstrike)

    def vannaspotstructure(self, portfolio, maxstrike):

        ax = plt.axes()
        spots = []
        for i in range(maxstrike - 1, 0, -1): spots.append(maxstrike - i)
        for i in range(maxstrike + 1): spots.append(maxstrike + i)
        deltas = self.__computedeltaversusvolatility(spots, portfolio)
        # plot the gamma profile over spot
        ax.set_title("Delta vs. Volatility Spot Structure")
        for i in range(len(deltas)):
            ax.plot(spots, deltas[i][1], label = "Vol: " + str(deltas[i][0]))
        plt.legend()
        plt.show()

    def __computedeltaversusvolatility(self, spots, portfolio):

        sigmas = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
        result = []

        for sigma in sigmas:
            deltas = []
            for spot in spots:
                # compute the gamma for each option in the portfolio
                totaldelta = 0
                for o in portfolio:
                    d = BlackScholes.computecalldelta(spot, o.strike, o.expiry, self.r, sigma)
                    if o.side == "LONG": totaldelta += d
                    elif o.side == "SHORT": totaldelta -= d
                deltas.append(totaldelta)
            result.append((sigma,deltas))

        return result

    def gammaspotstructure(self, portfolio, maxstrike):

        ax = plt.axes()
        spots = []
        for i in range(maxstrike - 1, 0, -1): spots.append(maxstrike - i)
        for i in range(maxstrike + 1): spots.append(maxstrike + i)
        gammas = self.__computegammaspotstructure(spots, portfolio)
        # plot the gamma profile over spot
        ax.set_title("Gamma Spot Structure")
        ax.plot(spots, gammas)
        plt.show()

    def vegaspotstructure(self, portfolio, maxstrike):

        ax = plt.axes()
        spots = []
        for i in range(maxstrike - 1, 0, -1): spots.append(maxstrike - i)
        for i in range(maxstrike + 1): spots.append(maxstrike + i)
        vegas = self.__computevegaspotstructure(spots, portfolio)
        # plot the gamma profile over spot
        ax.set_title("Vega Spot Structure")
        ax.plot(spots, vegas)
        plt.show()

    def __computegammaspotstructure(self, spots, portfolio):

        gammas = []
        for spot in spots:
            # compute the gamma for each option in the portfolio
            totalgamma = 0
            for o in portfolio:
                g = BlackScholes.computegamma(spot, o.strike, o.expiry, self.r, self.sigma)
                if o.side == "LONG": totalgamma += g
                elif o.side == "SHORT": totalgamma -= g
            gammas.append(totalgamma)
        return gammas
    
    def __computevegaspotstructure(self, spots, portfolio):

        vegas = []
        for spot in spots:
            # compute the gamma for each option in the portfolio
            totalvega = 0
            for o in portfolio:
                v = BlackScholes.computevega(spot, o.strike, o.expiry, self.r, self.sigma)
                if o.side == "LONG": totalvega += v
                elif o.side == "SHORT": totalvega -= v
            vegas.append(totalvega)
        return vegas

if __name__ == "__main__":

    r = 0.05
    sigma = 0.125

    G = Greek(r, sigma)
    # G.gammaspotstructure_downandoutput()
    # G.gammaspotstructure_call()
    # G.vegaspotstructure_call()
    # G.vannaspotstructure_call()
    # G.vannaspotstructure_callspread()
    G.vegaspotstructure_riskreversal()

