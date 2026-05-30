import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from loguru import logger

class SMCStrategy:
    def __init__(self, symbol, timeframe=mt5.TIMEFRAME_H1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.swing_window = 5 # Window for swing detection

    def get_market_data(self, count=200):
        """Fetches historical data from MT5."""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, count)
        if rates is None:
            logger.error(f"Failed to fetch data for {self.symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def identify_swings(self, df):
        """Identifies swing highs and swing lows."""
        df['swing_high'] = df['high'].rolling(window=self.swing_window*2+1, center=True).max()
        df['swing_low'] = df['low'].rolling(window=self.swing_window*2+1, center=True).min()
        
        df['is_swing_high'] = df['high'] == df['swing_high']
        df['is_swing_low'] = df['low'] == df['swing_low']
        return df

    def detect_bos_choch(self, df):
        """Detects Break of Structure (BOS) and Change of Character (CHoCH)."""
        swings = df[(df['is_swing_high']) | (df['is_swing_low'])].copy()
        if len(swings) < 4:
            return None, "Not enough market structure"

        latest_close = df['close'].iloc[-1]
        last_high = swings[swings['is_swing_high']]['high'].iloc[-1]
        last_low = swings[swings['is_swing_low']]['low'].iloc[-1]
        
        structure = None
        if latest_close > last_high:
            structure = "BULLISH_BOS" if df['close'].iloc[-5] > last_low else "CHoCH_BULLISH"
        elif latest_close < last_low:
            structure = "BEARISH_BOS" if df['close'].iloc[-5] < last_high else "CHoCH_BEARISH"
            
        return structure, (last_high, last_low)

    def find_order_blocks(self, df, structure_type):
        """Identifies the most recent Order Block based on structure break."""
        # Simplified: Last opposite candle before the move
        if "BULLISH" in structure_type:
            # Find last bearish candle before the breakout
            for i in range(len(df)-2, 0, -1):
                if df['close'].iloc[i] < df['open'].iloc[i]:
                    return {'type': 'bullish', 'price': df['low'].iloc[i], 'top': df['high'].iloc[i]}
        elif "BEARISH" in structure_type:
            # Find last bullish candle before the breakout
            for i in range(len(df)-2, 0, -1):
                if df['close'].iloc[i] > df['open'].iloc[i]:
                    return {'type': 'bearish', 'price': df['high'].iloc[i], 'bottom': df['low'].iloc[i]}
        return None

    def detect_fvg(self, df):
        """Detects Fair Value Gaps (FVG)."""
        fvgs = []
        for i in range(len(df)-3, len(df)):
            if i < 2: continue
            # Bullish FVG (Gap between Candle 1 High and Candle 3 Low)
            if df['low'].iloc[i] > df['high'].iloc[i-2]:
                fvgs.append({'type': 'bullish', 'zone': (df['high'].iloc[i-2], df['low'].iloc[i])})
            # Bearish FVG (Gap between Candle 1 Low and Candle 3 High)
            elif df['high'].iloc[i] < df['low'].iloc[i-2]:
                fvgs.append({'type': 'bearish', 'zone': (df['low'].iloc[i-2], df['high'].iloc[i])})
        return fvgs

    def generate_signals(self):
        """Generates high-confluence SMC signals."""
        df = self.get_market_data()
        if df is None: return None
        
        df = self.identify_swings(df)
        structure, levels = self.detect_bos_choch(df)
        
        if not structure:
            return None

        ob = self.find_order_blocks(df, structure)
        fvgs = self.detect_fvg(df)
        
        # CONFLUENCE CHECK: Structure + OB + FVG
        if ob and fvgs:
            logger.info(f"SMC Setup: {structure} with OB at {ob['price']} and {len(fvgs)} FVGs")
            
            # Example Signal Format for Executor
            if "BULLISH" in structure:
                return {
                    'action': 'BUY',
                    'entry_price': df['close'].iloc[-1],
                    'stop_loss': ob['price'],
                    'take_profit': df['close'].iloc[-1] + (df['close'].iloc[-1] - ob['price']) * 2, # 1:2 RR
                    'sl_points': abs(df['close'].iloc[-1] - ob['price']) * 100000 # Simplified point calc
                }
            elif "BEARISH" in structure:
                return {
                    'action': 'SELL',
                    'entry_price': df['close'].iloc[-1],
                    'stop_loss': ob['price'],
                    'take_profit': df['close'].iloc[-1] - (ob['price'] - df['close'].iloc[-1]) * 2, # 1:2 RR
                    'sl_points': abs(ob['price'] - df['close'].iloc[-1]) * 100000
                }
                
        return None
