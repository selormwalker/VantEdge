import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import os

class ReportGenerator:
    def __init__(self, magic_number):
        self.magic_number = magic_number

    def get_daily_stats(self):
        """Calculates trading stats for the last 24 hours."""
        from_date = datetime.now() - timedelta(days=1)
        to_date = datetime.now()
        
        # Fetch history
        history = mt5.history_deals_get(from_date, to_date)
        if history is None or len(history) == 0:
            return "No trades executed in the last 24 hours."

        df = pd.DataFrame(list(history), columns=history[0]._asdict().keys())
        # Filter by magic number
        df = df[df['magic'] == self.magic_number]
        
        if df.empty:
            return "No VantEdge trades in the last 24 hours."

        total_profit = df['profit'].sum()
        total_trades = len(df)
        wins = len(df[df['profit'] > 0])
        win_rate = (wins / total_trades) * 100

        report = (
            f"📊 *VantEdge Daily Report*\n"
            f"Period: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}\n"
            f"---------------------------\n"
            f"💰 Total PnL: ${total_profit:.2f}\n"
            f"📈 Total Trades: {total_trades}\n"
            f"✅ Win Rate: {win_rate:.1f}%\n"
            f"---------------------------\n"
            f"Status: Trading Active 🚀"
        )
        return report

    def save_report_to_file(self):
        report = self.get_daily_stats()
        with open("logs/daily_report.txt", "w") as f:
            f.write(report)
        logger.info("Daily performance report generated.")
