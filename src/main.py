import os
import sys
import MetaTrader5 as mt5
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logger():
    logger.add("logs/vantedge_forex.log", rotation="500 MB", level="INFO")
    logger.info("VantEdge Forex Bot Initialized")

def connect_mt5():
    login = int(os.getenv("MT5_LOGIN", 0))
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "")

    if not mt5.initialize(login=login, password=password, server=server):
        logger.error(f"MT5 initialization failed, error code: {mt5.last_error()}")
        return False
    
    logger.info("Connected to MetaTrader 5 Successfully")
    return True

def main():
    load_dotenv()
    setup_logger()
    
    if not connect_mt5():
        return

    symbol = os.getenv("TRADING_SYMBOL", "EURUSD")
    logger.info(f"VantEdge monitoring {symbol}...")
    
    from strategy import SMCStrategy
    from risk_management import RiskManager
    from execution import OrderExecutor
    
    # Switch to M5 for faster real-time testing
    strategy = SMCStrategy(symbol, timeframe=mt5.TIMEFRAME_M5)
    executor = OrderExecutor(symbol, magic_number=int(os.getenv("MAGIC_NUMBER", 123456)))
    
    import time
    logger.info(f"VantEdge Live Scanner started on {symbol} (M5). Press Ctrl+C to stop.")
    
    try:
        while True:
            # Refresh account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Could not retrieve account info.")
                break
                
            risk_manager = RiskManager(account_info.balance)
            
            # SMC Strategy Check
            signal = strategy.generate_signals()
            if signal:
                logger.info(f"ALGO TRIGGERED: {signal['action']} signal found!")
                lot_size = risk_manager.calculate_position_size(symbol, signal['sl_points'])
                
                executor.execute_trade(
                    action=signal['action'],
                    lot=lot_size,
                    price=signal['entry_price'],
                    sl=signal['stop_loss'],
                    tp=signal['take_profit']
                )
                # Wait longer after a trade
                time.sleep(300) 
            
            # Wait 60 seconds before next scan
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Scanner stopped by user.")
    except Exception as e:
        logger.error(f"Execution error: {e}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
