from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
import plotly.io as pi
import datetime as dt
from screener.models import *
from .helpers.db_manager import *
from .helpers.plotter import *
from .helpers.index_calculator import *
from django.contrib import messages
from transactions.models import Portfolio

# Create your views here.
def index(request):
    ## add news 

    portfolios = Portfolio.objects.all()

    context={
        'portfolios':portfolios
    }
    return render(request, 'screener/overview.html', context)


def company(request):
    '''
    Gives an overview of a single company,
    if not in the db it download it
    '''

    try:
        ticker = request.GET['search_query'].upper()

        company = Company.objects.filter(ticker = ticker)

        if not company:
            #create company objects
            create_object(ticker)
            

    ## HANDLE ERRORS
    except Exception as e:
        context = { 
            'req': request.GET['search_query'],
            'error': f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}",
        }
        return render(request, 'screener/404.html', context)

        
    # query db and create context
    company = Company.objects.filter(ticker = ticker)[0]

    # CALCULATE INDICES
    # get income_statement and balancesheet
    income_statement = pd.read_csv(ARCHIVE_PATH + "income_statement/" + str(company.income_statement), index_col=0)
    balancesheet = pd.read_csv(ARCHIVE_PATH + "balancesheet/" + str(company.balancesheet), index_col=0)
    cash_flow = pd.read_csv(ARCHIVE_PATH + "cash_flow/" + str(company.cash_flow), index_col=0)
    
    indices = calculate_indices(financials = income_statement, balancesheet = balancesheet)
    mean_indices = industry_mean(company.industry)

    # CREATE PLOTS
    # get history
    end_date = dt.datetime.today().date()
    history = pd.read_csv(ARCHIVE_PATH + "history/" + str(company.history), index_col='date')
    #convert dates to str
    start_date = dt.datetime.strftime(end_date-pd.DateOffset(years= 10), '%Y-%m-%d')
    end_date = dt.datetime.strftime(end_date, '%Y-%m-%d')

    candle_plot = pi.to_html(    
        plot_candlestick(history.loc[start_date: end_date]), 
        full_html=False, 
        default_height="800px"
        )

    asset_liabilities = pi.to_html(
        plot_balancesheet(balancesheet), 
        full_html=False, 
        )

    revenue_income = pi.to_html(
        plot_income_statement(income_statement), 
        full_html=False, 
        )

    context={

        'ticker':company.ticker,
        'name':company.name,
        'sector':company.sector,
        'industry':company.industry,
        'phone':company.phone,
        'website':company.website,
        'country':company.country,
        'state':company.state,
        'city':company.city,
        'address':company.address,
        'summary':company.summary,
        'employees':company.employees,

        'latest_update':company.latest_update,

        'balancesheet':balancesheet.iloc[:,:1].to_html(classes="table col-12 table-sm table-hover", header=False),
        'income_statement':income_statement.iloc[:,:1].to_html(classes="table col-12 table-sm table-hover", header=False),
        'cash_flow':cash_flow.iloc[:,:1].to_html(classes="table table-sm table-hover", header=False),

        'history':history,
        

        'indices':indices,
        'mean_indices':mean_indices,

        #plots 
        'candlestick': candle_plot,
        'asset_liabilities': asset_liabilities,
        'revenue_income': revenue_income,
        
    }

    return render(request, 'screener/company.html', context)


def update(request):
    
    ticker = request.GET['search_query'].upper()
    update_object(ticker)
    return HttpResponseRedirect('/company/?search_query=' + ticker)


