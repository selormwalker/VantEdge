import MetaTrader5 as mt5
from loguru import logger

class OrderExecutor:
    def __init__(self, symbol, magic_number=123456):
        self.symbol = symbol
        self.magic_number = magic_number

    def execute_trade(self, action, lot, price, sl, tp, comment="VantEdge SMC"):
        """
        Sends an execution request to MT5.
        action: 'BUY' or 'SELL'
        """
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
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10, # Slippage protection in points
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order to MT5
        result = mt5.order_send(request)
        
        if result is None:
            logger.error("Order send failed: MT5 result is None")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed! Retcode: {result.retcode}, Comment: {result.comment}")
            return result
        
        logger.info(f"Order executed successfully: {action} {lot} {self.symbol} at {price}")
        return result

    def close_all_positions(self):
        """Emergency function to close all open positions for this bot's magic number."""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return

        for pos in positions:
            if pos.magic == self.magic_number:
                # Close logic for each position
                pass # Implementation for closing logic
