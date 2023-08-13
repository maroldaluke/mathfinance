# lmarolda - greeks

from stockmodel import *
from blackscholes import *
from hedging import *

class Risk(object):

    def __init__(self):

        return
    
    @staticmethod
    def graphgreeks():

        # time parameters
        N = 2 * 256
        timestep = 0.1
        # stock parameters
        S0 = 50
        r = 0.05
        vol = 0.125

        # options parameters
        K1, K2, K3 = 40, 60, 50
        T1, T2, T3 = 2, 2, 2
        V1, V2, V3 = OptionModel.CALL, OptionModel.CALL, OptionModel.CALL

        f, ax = plt.subplots(3, 2)
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
        pm = OptionsPortfolio([(om1, "LONG")])
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
        f.tight_layout(pad=0.25)
        plt.show()

    """
    
    SUMMARY

    delta versus passage of time is also known as the second order greek "charm"

    for ITM options:
    - as time to expiry decreases, the delta of an ITM option increases
    - this is because the time value of the option disappears, causing an ITM
      option to behave closer and closer to the underlying, causing delta to
      increase towards 1
    for OTM options:
    - as time to expiry decreases, the delta of an ITM option decreases
    - this is because the time value of the option disappears, causing an OTM
      option to be less and less likely to be exercised, causing the delta to
      decrease towards 0
    for ATM options:
    - exactly ATM options will have the same delta as time to expiry changes
    
    """
    @staticmethod
    def deltaversusexpiry():

        Risk.greekversusexpiry("Delta")

    """

    SUMMARY

    gamma versus passage of time is known as the third order greek "color"

    for ATM options:
    with other factors held equal
    - as time to expiry decreases, gamma increases
    - as time to expiry increases, gamma decreases
    - ie. the further away from expiry, the lower the gamma profile
    intuition:
    - the closer to expiry, the more that delta is subject to fluctuations. 
      because we are ATM, there is high chance for the option to fluctuate into
      or out of the money, causing a higher change in delta. this corresponds
      to a higher gammma profile for options closer to expiration

    for OTM/ITM options:
    with other factors held equal
    - as time to expiry decreases, gamma decreases
    - as time to expiry increases, gamma increases
    - ie. the further away from expiry, the higher the gamma profile
    intuition:
    - the closer we are to expiry, if an option is already ITM or OTM, the
      higher the prob that we will stay ITM or OTM. this means delta will remain
      relatively consistent, causing gamma to be small

    """
    @staticmethod
    def gammaversusexpiry():

        Risk.greekversusexpiry("Gamma")


    @staticmethod
    def greekversusexpiry(greek):

        # time parameters
        N = 2 * 256
        timestep = 0.1
        # stock parameters
        S0 = 50
        r = 0.05
        vol = 0.125
        # options parameters
        K1, K2, K3, K4, K5 = 50, 50, 50, 50, 50
        T1, T2, T3, T4, T5 = 0.25, 0.5, 0.75, 1, 2
        V1, V2, V3, V4, V5 = OptionModel.CALL, OptionModel.CALL, OptionModel.CALL, OptionModel.CALL, OptionModel.CALL

        f, ax = plt.subplots(2)
        stock = StockModel(N, S0, r, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax[0].set_title("Stock Price")
        ax[0].plot(t, st)
        # now build our options models
        om1 = OptionModel(V1, K1, T1, r, vol, stock, timestep)
        om2 = OptionModel(V2, K2, T2, r, vol, stock, timestep)
        om3 = OptionModel(V3, K3, T3, r, vol, stock, timestep)
        om4 = OptionModel(V4, K4, T4, r, vol, stock, timestep)
        om5 = OptionModel(V5, K5, T5, r, vol, stock, timestep)
        options = [om1, om2, om3, om4, om5]
        # model the options
        for o in options: o.model(t, st)
        # plot the greek
        ax[1].set_title(greek)
        for o in options: 
            if greek == "Delta": g = o.delta
            elif greek == "Gamma": g = o.gamma
            ax[1].plot(o.t, g)
        f.tight_layout(pad=0.25)
        plt.show()

    """
    
    SUMMARY

    - delta increases as an option moves further ITM
    - delta decreases as an option moves further OTM
    - delta is roughly 0.50 (50) for options that are exactly ATM, slightly
      skewed towards higher strikes
    - therefore as an option moves further ITM, its price movement resembles
      the underlying more and more
    
    """
    @staticmethod
    def deltaversusstrike():

        Risk.greekversusstrike("Delta")

    """
    
    SUMMARY

    gamma is the highest (maximized) for ATM options
    this is true for calls and puts
    gamma becomes successively lower as options move further ITM or OTM 
    
    """
    @staticmethod
    def gammaversusstrike():

        Risk.greekversusstrike("Gamma")

    @staticmethod
    def greekversusstrike(greek):
        
        # time parameters
        N = 2 * 256
        timestep = 0.1
        # stock parameters
        S0 = 50
        r = 0.05
        vol = 0.125
        # options parameters
        K1, K2, K3, K4, K5 = 30, 40, 50, 60, 70
        T1, T2, T3, T4, T5 = 2, 2, 2, 2, 2
        V1, V2, V3, V4, V5 = OptionModel.CALL, OptionModel.CALL, OptionModel.CALL, OptionModel.CALL, OptionModel.CALL

        f, ax = plt.subplots(2)
        stock = StockModel(N, S0, r, vol, timestep)
        # first model the underlying
        (t, st) = stock.model()
        ax[0].set_title("Stock Price")
        ax[0].plot(t, st)
        # now build our options models
        om1 = OptionModel(V1, K1, T1, r, vol, stock, timestep)
        om2 = OptionModel(V2, K2, T2, r, vol, stock, timestep)
        om3 = OptionModel(V3, K3, T3, r, vol, stock, timestep)
        om4 = OptionModel(V4, K4, T4, r, vol, stock, timestep)
        om5 = OptionModel(V5, K5, T5, r, vol, stock, timestep)
        options = [om1, om2, om3, om4, om5]
        # model the options
        for o in options: o.model(t, st)
        # plot the greek
        ax[1].set_title(greek)
        for o in options: 
            if greek == "Delta": g = o.delta
            elif greek == "Gamma": g = o.gamma
            ax[1].plot(o.t, g, label = "Strike: " + str(o.K))
        f.tight_layout(pad=0.25)
        plt.legend()
        plt.show()

if __name__ == "__main__":

    # Risk.graphgreeks()
    # Risk.deltaversusexpiry()
    # Risk.gammaversusexpiry()
    Risk.deltaversusstrike()
