# brownian motion

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import math as m
from scipy.stats import bernoulli

class RandomWalk(object):

    def __init__(self, p, timestep):

        self.p = p
        self.timestep = timestep
        self.size = m.sqrt(self.timestep)
        self.x = []
        self.y = []
        self.z = []

    def iterate(self):

        (x,y,z) = self.__generatestep()
        self.__addstep(x, y, z)

    def simulate(self, num):

        steps = m.floor(num / self.timestep)
        for i in range(steps): self.iterate()

    """
    generates next step of RV based on distribution 
    uses scipy bernoulli discrete RV as randomness
    """
    def __generatestep(self):

        r1 = bernoulli.rvs(self.p)
        r2 = bernoulli.rvs(self.p)
        step1 = self.size if r1 == 1 else -self.size
        step2 = self.size if r2 == 1 else -self.size
        # determine next elem to add to list
        nx = self.x[-1] + self.timestep if len(self.x) > 0 else self.timestep
        ny = self.y[-1] + step1 if len(self.y) > 0 else step1
        nz = self.z[-1] + step2 if len(self.z) > 0 else step2
        return (nx,ny,nz)

    def __addstep(self, x, y, z):

        self.x.append(x)
        self.y.append(y)
        self.z.append(z)

if __name__ == "__main__":

    timesteps = [10, 5, 1, 0.5, 0.25, 0.1, 0.01, 0.001, 0.0001]

    fig = plt.figure()
    ax = plt.axes(projection='3d')

    for time in timesteps:
        
        rw = RandomWalk(0.5, time)
        rw.simulate(100)
        # plt.plot(rw.x, rw.y, linewidth=2.0)
        ax.plot3D(rw.x, rw.y, rw.z)

    plt.show()