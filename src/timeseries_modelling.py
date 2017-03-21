import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pymc3 as pm
from pymc3.distributions.timeseries import GaussianRandomWalk

from scipy import optimize


if __name__ == "__main__":
    df = pd.read_csv('../../backtester/data/train_2016.csv')
    log_returns = np.array(np.log(df['Weighted Price']) - np.log(df['Weighted Price'].shift(1)))[1:]
    plt.plot(log_returns)

    prices = df['Weighted Price'].values[:100]
    log_returns = log_returns[:100]

    model = pm.Model()
    with model:
        sigma = pm.Exponential('sigma', 1./.02, testval=.1)

        nu = pm.Exponential('nu', 1./10)
        s = GaussianRandomWalk('s', sigma**-2, shape=len(log_returns))

        r = pm.StudentT('r', nu, lam=pm.math.exp(-2*s), observed=log_returns)

    with model:
        trace = pm.sample(2000)
    
    fig, axarr = plt.subplots(2,1, sharex=True)
    axarr[0].plot(log_returns)
    axarr[1].plot(trace['s'][-500:,:].T,'b', alpha=.03);
    axarr[0].xlabel('time')
    axarr[1].ylabel('log volatility')
    plt.show()

    plt.plot(np.abs(log_returns))
    plt.plot(np.exp(trace['s'][::10].T), 'r', alpha=.03)
    plt.xlabel('time')
    plt.ylabel('absolute returns')
    plt.show()

    # now use the volatilies to forecast
    predict_period = 3
    volatilities = np.exp(np.mean(trace['s'][-50:],axis=0))

    n_samples = 1000
    change = volatilities[:, np.newaxis, np.newaxis] * np.random.randn(len(log_returns), predict_period, n_samples) + 1
    brownian = prices[:, np.newaxis, np.newaxis] * np.cumprod(change,axis=1)
    plt.plot(brownian[:, 0, :], 'r', alpha=0.03)
    stdevs = np.std(brownian,axis=2)
    outlier_locations = (prices[1:] > prices[:-1] + 1.96 * stdevs[:-1,0]) | (
                           prices[1:] < prices[:-1] - 1.96 * stdevs[:-1,0])
    outliers = prices[1:][outlier_locations]
    outliers = np.array([np.arange(99)[outlier_locations], outliers])
    plt.plot(prices + 1.96 * stdevs[:,0],'--')
    plt.plot(prices - 1.96 * stdevs[:,0],'--')
    plt.plot(prices[1:], 'k')
    plt.scatter(outliers[0, :], outliers[1, :])
    plt.show()

