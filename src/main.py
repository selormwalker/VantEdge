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
    
    try:
        # Placeholder for Forex Trading Logic
        # account_info = mt5.account_info()
        # logger.info(f"Account Balance: {account_info.balance}")
        logger.info("Bot engine ready for execution...")
    except Exception as e:
        logger.error(f"Execution error: {e}")
    finally:
        # mt5.shutdown()
        pass

if __name__ == "__main__":
    main()
