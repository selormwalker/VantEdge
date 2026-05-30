# VantEdge Forex Bot

A high-performance automated Forex trading bot designed for MetaTrader 5 (MT5).

## Features
- **MT5 Integration**: Native connection to MetaTrader 5 for fast execution.
- **Python-Powered**: Leveraging `pandas` and `MetaTrader5` for data analysis and trade management.
- **Configurable**: Easily adjust strategies, symbols, and risk parameters via `.env`.

## Setup
1. Install MetaTrader 5 on your Windows machine.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your credentials in `.env` (use `.env.example` as a template).
5. Run the bot:
   ```bash
   python src/main.py
   ```

## Tech Stack
- Python 3.x
- MetaTrader 5
- pandas (Data Analysis)
- Loguru (Logging)
- python-dotenv (Config Management)
