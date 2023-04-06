import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

#helper function that assign color to the cloud
def get_fill_color(label):
    if label >= 1:
        return "rgba(0, 250, 0 , 0.4)"
    else:
        return "rgba(250, 0, 0 , 0.4)"

def plot_bollinger_bands(df):

    # add bollinger band to df
    df['middle_band'] = df['close'].rolling(window=20).mean()
    df['upper_band'] = df['middle_band'] + 1.96 * df['close'].rolling(window=20).std()
    df['lower_band'] = df['middle_band'] - 1.96 * df['close'].rolling(window=20).std()

    fig = go.Figure()
    
    candle = go.Candlestick(x=df.index, open=df["open"], close=df["close"], high=df["high"], low=df["low"], name="Candlestick")
    upper_line = go.Scatter(x=df.index, y=df["upper_band"], line=dict(color="rgba(250, 0, 0, 0.75)", width=1), name='Upper Band')
    middle_line = go.Scatter(x=df.index, y=df["middle_band"], line=dict(color="rgba(0, 0, 250, 0.75)", width=0.7), name='Middle Band')
    lower_line = go.Scatter(x=df.index, y=df["lower_band"], line=dict(color="rgba(0, 250, 0, 0.75)", width=1), name='Lower Band')

    fig.add_trace(candle)
    fig.add_trace(upper_line)
    fig.add_trace(middle_line)
    fig.add_trace(lower_line)

    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")

    fig.update_layout(title="Bollinger Bands", height=800, width=1200, showlegend=True)
    return fig

def plot_Ichimoku(df):

    # add ichimoku values to df
    high_value = df['high'].rolling(window=9).max()
    low_value = df['low'].rolling(window=9).min()
    df['Conversion'] = (high_value + low_value)/2

    #base line = (highest value in period + lowest value in period)/2 (26 periods)
    high_value2 = df['high'].rolling(window=26).max()
    low_value2 = df['low'].rolling(window=26).min()
    df['Baseline'] = (high_value2 + low_value2)/2

    #leading span A = (Conversion Value + Base Value)/2 (26 periods)
    df['SpanA'] = ((df['Conversion'] + df['Baseline']) / 2 )

    #leading span B = (Conversion Value + Base Value)/2 (52 periods) 
    high_value3 = df['high'].rolling(window=52).max()
    low_value3 = df['low'].rolling(window=52).min()
    df['SpanB'] = ((high_value3 + low_value3) / 2).shift(26)

    #lagging span = price shifted back 2 periods
    df['Lagging'] = df['close'].shift(-26)

    candle = go.Candlestick(x=df.index, open=df["open"], close=df["close"], high=df["high"], low=df["low"], name="Candlestick")

    df1 = df.copy()
    fig = go.Figure()
    df["label"] = np.where(df["SpanA"] > df["SpanB"], 1, 0)
    df['group'] = df['label'].ne(df['label'].shift()).cumsum()
    df = df.groupby('group')

    dfs =[]
    for name, data in df:
        dfs.append(data)

    for df in dfs:
        fig.add_traces(go.Scatter(x=df.index, y=df.SpanA, line=dict(color="rgba(0,0,0,0)")))
        fig.add_traces(go.Scatter(x=df.index, y=df.SpanB, line=dict(color="rgba(0,0,0,0)"), fill='tonexty', fillcolor=get_fill_color(df['label'].iloc[0])))

    baseline = go.Scatter(x=df1.index, y=df1['Baseline'], line=dict(color='pink', width=2), name='Baseline')
    conversion = go.Scatter(x=df1.index, y=df1['Conversion'], line=dict(color='black', width=1), name='Conversion')
    lagging = go.Scatter(x=df1.index, y=df1['Lagging'], line=dict(color='purple', width=1), name='Lagging')
    spanA = go.Scatter(x=df1.index, y=df1['SpanA'], line=dict(color='green', width=2, dash='dot'), name='Span A')
    spanB = go.Scatter(x=df1.index, y=df1['SpanB'], line=dict(color='red', width=2, dash='dot'), name='Span B')

    fig.add_trace(candle)
    fig.add_trace(baseline)
    fig.add_trace(conversion)
    fig.add_trace(lagging)
    fig.add_trace(spanA)
    fig.add_trace(spanB)

    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")

    fig.update_layout(title="Ichimoku", height=800, width=1200, showlegend=True)
    return fig

def plot_pie(df):
    # create the vector that define major owner to be pulled
        distanced_from_center =[0.3]
        for i in range(0, len(df)-1):
            distanced_from_center.append(0)

        return go.Figure(data=[go.Pie(
            labels=df['Holder'], 
            values=df['% Out'], 
            hole=.3,
            textinfo='percent',
            insidetextorientation='horizontal',
            textfont_size=20,
            pull=distanced_from_center,
            )])

def plot_candlestick(df):
    
    candlestick = go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            showlegend=False
            )
    volume_bars = go.Bar(
            x=df.index, 
            y=df['volume'],
            showlegend=False,
            marker_color='black',
            )

    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, subplot_titles=('OHLC', 'Volume'), 
               row_width=[0.2, 0.7])

    fig.add_trace(candlestick, row=1, col=1)
    # Bar trace for volumes on 2nd row without legend
    fig.add_trace(volume_bars, row=2, col=1)
    # Do not show OHLC's rangeslider plot 
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update(layout_xaxis_rangeselector_visible=False)
    #add buttons
    fig.update_xaxes(
    rangeslider_visible=False,
    rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=3, label="3y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
            ])),
     
    )
    

    return fig

def plot_balancesheet(df):

    #get assets, handle Nan, and convert to integers
    asset = df.loc['TotalAssets'].fillna(0).astype(float).astype(int).tolist()

    #get liabilities
    liabilities = df.loc['TotalLiabilitiesNetMinorityInterest'].fillna(0).astype(float).astype(int).tolist()

    x = ["Total Assets","Total Liabilities"] 
    years = pd.to_datetime(df.loc["asOfDate"]).dt.year.tolist()
    fig = go.Figure(data=[
        go.Bar(name = x[0], x=years, y=asset, marker_color="skyblue"),
        go.Bar(name = x[1], x=years, y=liabilities, marker_color="darkblue"),
        
    ])

    return fig

def plot_income_statement(df):
    ## in this plot we need to exclude the term TTM, 
    # get revenue
    revenue = df.loc['TotalRevenue'].fillna(0).astype(float).astype(int).tolist()
    #eliminate TTM
    del revenue[-1]

    #get income
    income = df.loc['NetIncome'].fillna(0).astype(float).astype(int).tolist()
    #eliminate TTM
    del income[-1]

    x = ["Revenue","Income"] 
    years = pd.to_datetime(df.loc["asOfDate"]).dt.year.tolist()
    #eliminate TTM
    del years[-1]

    fig = go.Figure(data=[
        go.Bar(name = x[0], x=years, y=revenue, marker_color="goldenrod"),
        go.Bar(name = x[1], x=years, y=income, marker_color="green")
    ])

    return fig