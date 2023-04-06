from ..models import *
from django.conf import settings
import pandas as pd

ARCHIVE_PATH = str(settings.BASE_DIR) + "/archive/"



def calculate_indices(financials, balancesheet):
    #### TRY TO GET THE PARAMETERS FROM BALANCESHEET OR FINANCIALS OR
    #### SET THE VALUE AS float("NaN") to make the calculus of indices 
    #### much easier to handle, avoid errors
    try: current_assets = float(balancesheet.loc['CurrentAssets'][0])
    except KeyError: current_assets = float("NaN")     #1
    
    try: current_liabilities = float(balancesheet.loc['CurrentLiabilities'][0])#2
    except KeyError: current_liabilities = float("NaN")     

    try: inventory = float(balancesheet.loc['Inventory'][0])                   #3
    except KeyError: inventory = float("NaN")     
    
    try: stockholder_equity = float(balancesheet.loc['StockholdersEquity'][0]) #4
    except KeyError: stockholder_equity = float("NaN")     
    
    try: total_debt = float(balancesheet.loc['TotalDebt'][0])                  #6
    except KeyError: total_debt = float("NaN")     
    
    try: total_assets = float(balancesheet.loc['TotalAssets'][0])              #12
    except KeyError: total_assets = float("NaN")     
    
    try: net_sales = float(financials.loc['OperatingRevenue'][0])              #7
    except KeyError: net_sales = float("NaN")     
    
    try: interest_expense = float(financials.loc['InterestExpense'][0])        #8
    except KeyError: interest_expense = float("NaN")     
    
    try: invested_capital = float(balancesheet.loc['InvestedCapital'][0])      #9
    except KeyError: invested_capital = float("NaN")     
    
    try: net_income = float(financials.loc['NetIncome'][0])                    #10
    except KeyError: net_income = float("NaN")     
    
    try: EBIT = float(financials.loc['EBIT'][0]) 
    except KeyError: EBIT = float("NaN")     
    
    try: intangible_assets = float(balancesheet.loc['Goodwill'][0])
    except KeyError: intangible_assets = float("NaN")    
    
    try: short_term_debt = float(balancesheet.loc['TotalDebt'][0])
    except KeyError: short_term_debt = float("NaN")     
    
    try: long_term_debt = float(balancesheet.loc['LongTermDebt'][0])
    except KeyError: long_term_debt = float("NaN")     

    

    indices = {
        #liquidity indices
        'CR' : round(current_assets / current_liabilities, 3) if current_liabilities != 0 else 0,
        'QR' : round((current_assets - inventory) / current_liabilities, 3) if current_liabilities != 0 and inventory != 0 else 0,

        # financial solidity indices
        'fixed_asset_coverage' : round(((total_assets - intangible_assets)-(current_liabilities - short_term_debt))/total_debt, 3) if total_debt != 0 else 0,
        'RI' : round(total_debt / stockholder_equity, 3) if stockholder_equity != 0 else 0,
        'interest_expense_coverage' : round(EBIT / interest_expense, 3) if interest_expense != 0 else 0,
        'ROD' : round(net_income / long_term_debt, 3) if long_term_debt != 0 else 0,

        # redditivity indices
        'ROE' : round(net_income / stockholder_equity, 3) if stockholder_equity != 0 else 0,
        'ROA' : round(net_income / total_assets, 3) if total_assets != 0 else 0,
        'ROS' : round(net_sales / net_income, 3) if net_income != 0 else 0,
        'ROI' : round(net_income / invested_capital, 3) if invested_capital != 0 else 0,
        'ROT' : round(invested_capital / interest_expense, 3) if interest_expense != 0 else 0,
        'active_circulating_rotation' : round(net_income / current_assets, 3) if current_assets != 0 else 0,
    }
    return indices


def industry_mean(industry):

    companies = Company.objects.filter(industry=industry)

    income_statement = pd.read_csv(ARCHIVE_PATH + "income_statement/" + str(companies[0].income_statement), index_col=0)
    balancesheet = pd.read_csv(ARCHIVE_PATH + "balancesheet/" + str(companies[0].balancesheet), index_col=0)
    indices = calculate_indices(financials=income_statement, balancesheet=balancesheet)

    #calculate the indices for the first company
    mean_indices = {
        #liquidity indices
        'CR' : indices['CR'],
        'QR' : indices['QR'],

        # financial solidity indices
        'fixed_asset_coverage' : indices['fixed_asset_coverage'],
        'RI' : indices['RI'],
        'interest_expense_coverage' : indices['interest_expense_coverage'],
        'ROD' : indices['ROD'],

        # redditivity indices
        'ROE' : indices['ROE'],
        'ROA' : indices['ROA'],
        'ROS' : indices['ROS'],
        'ROI' : indices['ROI'],
        'ROT' : indices['ROT'],
        'active_circulating_rotation' : indices['active_circulating_rotation'],
    }
    
    # add all other companies
    for company in companies[1:]:
        income_statement = pd.read_csv(ARCHIVE_PATH + "income_statement/" + str(company.income_statement), index_col=0)
        balancesheet = pd.read_csv(ARCHIVE_PATH + "balancesheet/" + str(company.balancesheet), index_col=0)
        indices = calculate_indices(financials=income_statement, balancesheet=balancesheet)

        mean_indices['CR'] = (mean_indices['CR'] + indices['CR'])/2 if indices['CR'] is not float("NaN") else mean_indices['CR']
        mean_indices['QR'] = (mean_indices['QR'] + indices['QR'])/2 if indices['QR'] is not float("NaN") else mean_indices['QR']
        mean_indices['fixed_asset_coverage'] = (mean_indices['fixed_asset_coverage'] + indices['fixed_asset_coverage'])/2 if indices['fixed_asset_coverage'] is not float("NaN") else mean_indices['fixed_asset_coverage']
        mean_indices['RI'] = (mean_indices['RI'] + indices['RI'])/2 if indices['RI'] is not float("NaN") else mean_indices['RI']
        mean_indices['interest_expense_coverage'] = (mean_indices['interest_expense_coverage'] + indices['interest_expense_coverage'])/2 if indices['interest_expense_coverage'] is not float("NaN") else mean_indices['interest_expense_coverage']
        mean_indices['ROD'] = (mean_indices['ROD'] + indices['ROD'])/2 if indices['ROD'] is not float("NaN") else mean_indices['ROD']
        mean_indices['ROE'] = (mean_indices['ROE'] + indices['ROE'])/2 if indices['ROE'] is not float("NaN") else mean_indices['ROE']
        mean_indices['ROA'] = (mean_indices['ROA'] + indices['ROA'])/2 if indices['ROA'] is not float("NaN") else mean_indices['ROA']
        mean_indices['ROS'] = (mean_indices['ROS'] + indices['ROS'])/2 if indices['ROS'] is not float("NaN") else mean_indices['ROS']
        mean_indices['ROI'] = (mean_indices['ROI'] + indices['ROI'])/2 if indices['ROI'] is not float("NaN") else mean_indices['ROI']
        mean_indices['ROT'] = (mean_indices['ROT'] + indices['ROT'])/2 if indices['ROT'] is not float("NaN") else mean_indices['ROT']
        mean_indices['active_circulating_rotation'] = (mean_indices['active_circulating_rotation'] + indices['active_circulating_rotation'])/2 if indices['active_circulating_rotation'] is not float("NaN") else mean_indices['active_circulating_rotation']

    # round all the numbers
    for key in mean_indices:
        mean_indices[key] = round(mean_indices[key], 4)

    return mean_indices



