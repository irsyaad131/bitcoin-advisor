from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly
import json
import ta

app = Flask(__name__)

# Fungsi untuk mendapatkan data Bitcoin
def get_bitcoin_data(period='1y'):
    btc = yf.Ticker("BTC-USD")
    hist = btc.history(period=period)
    df = pd.DataFrame(hist)
    df = df[['Close']].rename(columns={'Close': 'price'})
    df = df.resample('D').mean().ffill()
    
    # Menghitung indikator teknis
    df['sma_20'] = ta.trend.sma_indicator(df['price'], window=20)
    df['sma_50'] = ta.trend.sma_indicator(df['price'], window=50)
    df['rsi'] = ta.momentum.rsi(df['price'], window=14)
    
    return df

# Fungsi untuk analisis rekomendasi
def analyze_bitcoin(df):
    recommendations = []
    
    # Golden Cross (SMA 20 > SMA 50)
    golden_cross = df[df['sma_20'] > df['sma_50']].index
    if len(golden_cross) > 0:
        last_golden_cross = golden_cross[-1]
        recommendations.append({
            'type': 'Golden Cross',
            'date': last_golden_cross.strftime('%Y-%m-%d'),
            'price': round(df.loc[last_golden_cross, 'price'], 2),
            'strength': 'Strong Buy Signal'
        })
    
    # RSI Oversold (<30)
    oversold = df[df['rsi'] < 30].index
    if len(oversold) > 0:
        last_oversold = oversold[-1]
        recommendations.append({
            'type': 'RSI Oversold',
            'date': last_oversold.strftime('%Y-%m-%d'),
            'price': round(df.loc[last_oversold, 'price'], 2),
            'strength': 'Good Buying Opportunity'
        })
    
    # Harga di bawah SMA 20
    below_sma20 = df[df['price'] < df['sma_20']].index
    if len(below_sma20) > 0:
        last_below = below_sma20[-1]
        recommendations.append({
            'type': 'Below SMA 20',
            'date': last_below.strftime('%Y-%m-%d'),
            'price': round(df.loc[last_below, 'price'], 2),
            'strength': 'Potential Buy'
        })
    
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    period = data.get('period', '1y')
    
    try:
        df = get_bitcoin_data(period)
        recommendations = analyze_bitcoin(df)
        
        # Buat plot
        fig = go.Figure()
        
        # Tambah harga Bitcoin
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['price'],
            name='Bitcoin Price',
            line=dict(color='#FF9500', width=2)
        ))
        
        # Tambah SMA 20
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_20'],
            name='SMA 20',
            line=dict(color='#34C759', width=1)
        ))
        
        # Tambah SMA 50
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_50'],
            name='SMA 50',
            line=dict(color='#AF52DE', width=1)
        ))
        
        # Update layout
        fig.update_layout(
            title='Bitcoin Price Analysis',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_dark',
            hovermode='x unified'
        )
        
        # Konversi plot ke JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'chart': graphJSON,
            'current_price': round(df['price'].iloc[-1], 2),
            'last_updated': df.index[-1].strftime('%Y-%m-%d')
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
