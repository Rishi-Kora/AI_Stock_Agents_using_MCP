import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    # Smart Ticker Resolution (NSE Only)
    ticker = ticker.strip().upper()
    
    # 1. Handle common aliases for Indices
    alias_map = {
        "NIFTY 50": "^NSEI",
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN", 
        "BSE SENSEX": "^BSESN"
    }
    
    if ticker in alias_map:
        ticker = alias_map[ticker]
    
    # 2. Enforce NSE for stocks (ignore BSE suffix if present)
    elif not ticker.startswith("^"):
        # Remove any existing suffix (like .BO or .NS) to ensure we always apply .NS cleanly
        base_ticker = ticker.split('.')[0]
        ticker = f"{base_ticker}.NS"

    try:
        stock = yf.Ticker(ticker)
        
        # Get historical data for the last year failure check
        history = stock.history(period="1y")
        
        if history.empty:
            return {"error": f"No historical data found for {ticker} (period=1y). Symbol might be invalid or delisted."}
            
        current_price = history['Close'].iloc[-1]
        
        # Safe retrieval of info with fallback
        try:
            info = stock.info
        except Exception:
            info = {}
        
        # Basic Technicals / Stats (Fallback to None if info fails)
        data = {
            "current_price": current_price,
            "previous_close": info.get("previousClose", history['Close'].iloc[-2] if len(history) > 1 else None),
            # ... (keep existing fields) ...
            "open": info.get("open", history['Open'].iloc[-1] if not history.empty else None),
            "day_high": info.get("dayHigh", history['High'].iloc[-1] if not history.empty else None),
            "day_low": info.get("dayLow", history['Low'].iloc[-1] if not history.empty else None),
            "52_week_high": info.get("fiftyTwoWeekHigh", history['High'].max() if not history.empty else None),
            "52_week_low": info.get("fiftyTwoWeekLow", history['Low'].min() if not history.empty else None),
            "volume": info.get("volume", history['Volume'].iloc[-1] if not history.empty else None),
            "market_cap": info.get("marketCap", None),
            "pe_ratio": info.get("trailingPE", None),
            "dividend_yield": info.get("dividendYield", None),
            "currency": info.get("currency", "INR" if ticker.endswith(".NS") else "USD"),
            "company_name": info.get("longName", ticker.replace(".NS", ""))
        }
        
        return data

    except Exception as e:
        return {"error": f"Exception during fetch for {ticker}: {str(e)}"}
