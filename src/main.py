import os
import sys
import asyncio
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy import SMCStrategy
from risk_management import RiskManager
from execution import OrderExecutor

class VantEdgeSwarm:
    def __init__(self, symbols):
        self.symbols = symbols
        self.strategies = {s: SMCStrategy(s) for s in symbols}
        self.executors = {s: OrderExecutor(s) for s in symbols}
        self.is_running = True

    async def check_news_filter(self):
        """Institutional news filter: placeholder for real API integration."""
        # In production, fetch from ForexFactory or similar
        return True # Approved to trade

    async def monitor_symbol(self, symbol):
        logger.info(f"[*] Commencing node monitoring for {symbol}...")
        
        while self.is_running:
            try:
                # 1. Institutional Safeguards
                if not await self.check_news_filter():
                    await asyncio.sleep(300)
                    continue

                # 2. Generate Signals
                signal = self.strategies[symbol].generate_signal()
                if signal:
                    logger.warning(f"[!] ALGO TRIGGERED on {symbol}: {signal['reason']}")
                    
                    # 3. Risk Check
                    account_info = mt5.account_info()
                    risk_mgr = RiskManager(account_info.balance)
                    
                    # Calculate dynamically
                    tick = mt5.symbol_info_tick(symbol)
                    sl_points = abs(signal['price'] - signal['sl']) / mt5.symbol_info(symbol).point
                    lot_size = risk_mgr.calculate_position_size(symbol, sl_points)
                    
                    # 4. Execute
                    self.executors[symbol].execute_trade(
                        action=signal['action'],
                        lot=lot_size,
                        price=signal['price'],
                        sl=signal['sl'],
                        tp=signal['tp'],
                        comment=f"Nexus v2.0 - {signal['reason']}"
                    )
                    
                    await asyncio.sleep(600) # Cooldown after trade

                await asyncio.sleep(15) # High-frequency scan interval
                
            except Exception as e:
                logger.error(f"Node failure on {symbol}: {e}")
                await asyncio.sleep(30)

    async def start(self):
        # Initialize swarm
        load_dotenv()
        login = int(os.getenv("MT5_LOGIN", 0))
        password = os.getenv("MT5_PASSWORD", "")
        server = os.getenv("MT5_SERVER", "")

        if not mt5.initialize(login=login, password=password, server=server):
            logger.critical("MT5 Nexus Handshake Failed.")
            return

        logger.info(f"Nexus Swarm Online. Nodes: {len(self.symbols)}")
        
        # Parallel Execution
        tasks = [self.monitor_symbol(s) for s in self.symbols]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    symbols_to_trade = ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"]
    swarm = VantEdgeSwarm(symbols_to_trade)
    try:
        asyncio.run(swarm.start())
    except KeyboardInterrupt:
        logger.info("Nexus Swarm Disconnected.")
    finally:
        mt5.shutdown()
