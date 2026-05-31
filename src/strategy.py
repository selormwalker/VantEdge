import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from loguru import logger

class SMCStrategy:
    def __init__(self, symbol, timeframe=mt5.TIMEFRAME_M5):
        self.symbol = symbol
        self.timeframe = timeframe
        self.swing_window = 7 # Larger window for institutional swings

    def get_market_data(self, count=500):
        """Fetches institutional-grade historical data."""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, count)
        if rates is None:
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def detect_liquidity_sweep(self, df):
        """Identifies 'Stop Hunts' or Liquidity Sweeps above/below old swings."""
        # Find local peaks
        df['local_high'] = df['high'].rolling(window=20).max()
        df['local_low'] = df['low'].rolling(window=20).min()
        
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Bullish Sweep: Price dips below local low then closes above it
        if prev_candle['low'] < df['local_low'].iloc[-20] and last_candle['close'] > df['local_low'].iloc[-20]:
            return "BULLISH_SWEEP"
        
        # Bearish Sweep: Price spikes above local high then closes below it
        if prev_candle['high'] > df['local_high'].iloc[-20] and last_candle['close'] < df['local_high'].iloc[-20]:
            return "BEARISH_SWEEP"
            
        return None

    def find_institutional_ob(self, df):
        """Finds high-probability Order Blocks with FVG confirmation."""
        # Bullish OB: Last down candle before a massive bullish push
        for i in range(len(df)-5, 0, -1):
            if df['close'].iloc[i] < df['open'].iloc[i]:
                # Check for displacement (strong move after)
                if df['close'].iloc[i+1] > df['high'].iloc[i]:
                    return {'type': 'BULLISH', 'level': df['low'].iloc[i], 'top': df['high'].iloc[i]}
        return None

    def generate_signal(self):
        """Generates high-confluence institutional setup."""
        df = self.get_market_data()
        if df is None: return None
        
        sweep = self.detect_liquidity_sweep(df)
        ob = self.find_institutional_ob(df)
        
        current_price = df['close'].iloc[-1]
        
        # CONFLUENCE: Sweep + OB tap
        if sweep == "BULLISH_SWEEP" and ob and ob['type'] == 'BULLISH':
            if current_price > ob['level'] and current_price < ob['top'] * 1.001:
                return {
                    'action': 'BUY',
                    'price': current_price,
                    'sl': ob['level'] - (50 * mt5.symbol_info(self.symbol).point), # 5 pips buffer
                    'tp': current_price + (current_price - ob['level']) * 3, # 1:3 RR
                    'reason': 'Liquidity Sweep + OB Tap'
                }
                
        elif sweep == "BEARISH_SWEEP":
            # Add bearish logic here
            pass
            
        return None
