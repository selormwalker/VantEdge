import os
import MetaTrader5 as mt5
from loguru import logger

class RiskManager:
    def __init__(self, account_balance):
        self.max_risk_per_trade = float(os.getenv("MAX_RISK_PERCENT", 1.0)) / 100.0
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS_PERCENT", 3.0)) / 100.0
        self.account_balance = account_balance

    def calculate_position_size(self, symbol, stop_loss_points):
        """Calculates lot size based on risk percent and SL distance."""
        if stop_loss_points <= 0:
            return 0.01 # Minimum lot size safety
        
        risk_amount = self.account_balance * self.max_risk_per_trade
        
        # Get point value for the symbol
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.01
            
        point_value = symbol_info.trade_tick_value
        lot_step = symbol_info.volume_step
        
        # Basic position sizing formula
        # risk_amount = lot_size * stop_loss_points * tick_value_per_lot
        # Note: This is simplified; actual calculation depends on account currency
        raw_lot = risk_amount / (stop_loss_points * point_value)
        
        # Round to nearest lot step
        lot_size = round(raw_lot / lot_step) * lot_step
        return max(lot_size, symbol_info.volume_min)

    def is_trading_allowed(self, current_daily_loss):
        """Checks if daily loss limits have been hit."""
        if current_daily_loss >= (self.account_balance * self.max_daily_loss):
            logger.warning("Daily loss limit reached. Trading suspended.")
            return False
        return True
