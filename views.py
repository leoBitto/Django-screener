from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
import plotly.io as pi
import datetime as dt
from screener.models import *
from .helpers.db_manager import *
from .helpers.plotter import *
from .helpers.index_calculator import *
from django.contrib import messages
from .forms import TransactionStockForm, ManageCashForm

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

        'balancesheet':balancesheet.iloc[:,:1].to_html(classes="table table-sm table-hover", header=False),
        'income_statement':income_statement.iloc[:,:1].to_html(classes="table table-sm table-hover", header=False),
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


def create_portfolio(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')  # Assicurati che il form abbia un campo 'start_date'
        cash_balance = request.POST.get('cash_balance')
                
        
        # Crea un nuovo portfolio
        portfolio = Portfolio.objects.create(
            name=name, 
            start_date=start_date,
            cash_balance = cash_balance
            )

        # Reindirizza alla pagina di dettaglio del nuovo portfolio
        return redirect('screener:portfolio_details', pk=portfolio.pk)

    # Se il metodo non è POST, visualizza il form per la creazione
    return render(request, 'screener/create_portfolio.html')


def eliminate_portfolio(request, pk):
                    
    # elimina portfolio
    Portfolio.objects.filter(pk=pk).delete()

    # Reindirizza alla pagina iniziale
    return redirect('screener:index')



def portfolio_details(request, pk):
    '''
    Gives an overview of the portfolio
    '''
    form_stocks = TransactionStockForm()
    form_cash = ManageCashForm()
    portfolio = Portfolio.objects.get(pk=pk)
    
    context={
        "portfolio":portfolio,
        'companies': Company.objects.all(),  # Aggiungi le aziende disponibili
        'form_stocks':form_stocks,
        'form_cash':form_cash,
    }

    return render(request, 'screener/portfolio.html', context)


def manage_stock(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)

    if request.method == 'POST':
        form = TransactionStockForm(request.POST)

        if form.is_valid():
            company_name = form.cleaned_data['company']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            commission = form.cleaned_data['commission']
            date = form.cleaned_data['transaction_date']
            transaction_type = form.cleaned_data['transaction_type']

            if transaction_type == 'BUY':
                company = get_object_or_404(Company, name=company_name)
                total_purchase_cost = (quantity * price) + commission

                if total_purchase_cost <= portfolio.cash_balance:
                    try:
                        stock = StockInPortfolio.objects.get(related_portfolio=portfolio, company=company)
                    except StockInPortfolio.DoesNotExist:
                        stock = None

                    if stock:
                        stock.quantity += quantity
                        stock.price = (stock.price + price) / 2
                        stock.save()
                    else:
                        stock = StockInPortfolio.objects.create(
                            related_portfolio=portfolio,
                            company=company,
                            quantity=quantity,
                            price=price,
                        )

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type='BUY',
                        quantity=quantity,
                        price=price,
                        commission=commission,
                        transaction_date=date
                    )

                    # Aggiornamento dei valori del portafoglio
                    portfolio.cash_balance -= total_purchase_cost
                    tot_stock_val = 0
                    for stock in StockInPortfolio.objects.filter(related_portfolio=portfolio):
                        tot_stock_val = stock.quantity * stock.price
                    portfolio.stock_value = tot_stock_val
                    portfolio.total_value = portfolio.cash_balance + portfolio.stock_value
                    portfolio.save()

                else:
                    messages.error(request, 'Fondi insufficienti per acquistare queste azioni.')
            
            else: # transaction_type == 'SELL'
                
                company = get_object_or_404(StockInPortfolio, company__name=company_name, related_portfolio=portfolio)
                
                if quantity <= company.quantity:
                    company.quantity -= quantity
                    company.save()

                    StockTransaction.objects.create(
                        stock=company,
                        transaction_type='SELL',
                        quantity=quantity,
                        price=price,
                        commission=commission,
                        transaction_date=date
                    )

                    # Aggiornamento dei valori del portafoglio
                    portfolio.cash_balance += (quantity * price - commission)
                    tot_stock_val = 0
                    for stock in StockInPortfolio.objects.filter(related_portfolio=portfolio):
                        tot_stock_val = stock.quantity * stock.price
                    portfolio.stock_value = tot_stock_val
                    portfolio.total_value = portfolio.cash_balance + portfolio.stock_value
                    portfolio.save()

                    # Se la quantità rimanente è zero, elimina l'oggetto StockInPortfolio
                    if company.quantity == 0:
                       company.delete()

                else:
                    messages.error(request, 'La quantità venduta supera la quantità disponibile.')


    else:
        form = TransactionStockForm()

    context = {
        'portfolio': portfolio,
        'companies': Company.objects.all(),
        'form_stocks': form,
        'form_cash': ManageCashForm(),
    }

    return render(request, 'screener/portfolio.html', context)


def manage_cash(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)

    if request.method == 'POST':
        form = ManageCashForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            transaction_type = form.cleaned_data['transaction_type']
            commission = form.cleaned_data['commission']

            if transaction_type == 'DEPOSIT':
                portfolio.cash_balance += (amount - commission)
                portfolio.total_investment += (amount - commission)
            elif transaction_type == 'WITHDRAW':
                if (amount + commission) <= portfolio.cash_balance:
                    portfolio.cash_balance -= (amount + commission)
                    portfolio.total_investment -= (amount + commission)  # Aggiornamento dell'investimento iniziale
                else:
                    messages.error(request, 'La quantità richiesta supera la quantità disponibile.')

            portfolio.total_value = portfolio.cash_balance + portfolio.stock_value
            portfolio.save()

    else:
        form = ManageCashForm()

    context = {
        'portfolio': portfolio,
        'companies': Company.objects.all(),
        'form_stocks': TransactionStockForm(),
        'form_cash': form,
    }

    return render(request, 'screener/portfolio.html', context)


