import MetaTrader5 as mt5
from loguru import logger

class OrderExecutor:
    def __init__(self, symbol, magic_number=123456):
        self.symbol = symbol
        self.magic_number = magic_number

    def execute_trade(self, action, lot, price, sl, tp, comment="VantEdge SMC"):
        """
        Sends an execution request to MT5 with enhanced filling protection.
        """
        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            logger.error(f"Symbol {self.symbol} not found.")
            return None

        if action == 'BUY':
            order_type = mt5.ORDER_TYPE_BUY
        elif action == 'SELL':
            order_type = mt5.ORDER_TYPE_SELL
        else:
            logger.error(f"Invalid action: {action}")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(lot),
            "type": order_type,
            "price": float(price),
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20, # Increased for high-speed
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK if symbol_info.filling_mode == mt5.SYMBOL_FILLING_FOK else mt5.ORDER_FILLING_IOC,
        }

        # Send order to MT5
        result = mt5.order_send(request)
        
        if result is None:
            logger.error("Order send failed: MT5 result is None")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed! Retcode: {result.retcode}, Comment: {result.comment}")
            return result
        
        logger.warning(f"INSTITUTIONAL EXECUTION: {action} {lot} {self.symbol} at {price}")
        return result

    def apply_trailing_stop(self, position_ticket, trail_pips):
        """Institutional Trailing Stop placeholder for v2.0."""
        # This will be implemented with a dedicated thread in the next patch
        pass

    def close_all_positions(self):
        """Emergency function to close all open positions for this bot's magic number."""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return

        for pos in positions:
            if pos.magic == self.magic_number:
                # Close logic for each position
                pass # Implementation for closing logic
