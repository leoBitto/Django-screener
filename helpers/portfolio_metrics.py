import numpy as np


def total_return(total_value, total_investment):
    return (total_value - total_investment) / total_investment

def annualized_return(total_value, total_investment, years):
    return ((total_value / total_investment) ** (1 / years)) - 1

def sharpe_ratio(expected_portfolio_return, risk_free_rate, portfolio_std_dev):
    return (expected_portfolio_return - risk_free_rate) / portfolio_std_dev

def cagr(total_value, total_investment, years):
    return ((total_value / total_investment) ** (1 / years)) - 1

def volatility(returns):
    return np.std(returns)

def drawdown(returns):
    cum_returns = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cum_returns)
    drawdowns = (cum_returns - peak) / peak
    max_drawdown = np.min(drawdowns)
    return max_drawdown


def stock_percentage(stock_value, total_investment):
    return (stock_value / total_investment) * 100
