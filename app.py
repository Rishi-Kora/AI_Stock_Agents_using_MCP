import streamlit as st
import pandas as pd
import asyncio
import os
import ast
import sys
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI Stock Agent", layout="wide")

# Ensure markdown is installed (Auto-fix for environment mismatches)
try:
    import markdown
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

# --- APPLE-STYLE CSS ---
st.markdown("""
<style>
    /* 1. Global Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        color: #1d1d1f; /* Apple's near-black */
    }
    
    .stApp {
        background-color: #f5f5f7; /* iOS Settings Background */
    }

    /* 2. Header / Title */
    h1 {
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -0.02em;
        color: #111;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.01em;
    }

    /* 3. Input Styling (Search Bar) */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #d2d2d7;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 16px;
        color: #1d1d1f;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .stTextInput > div > div > input:focus {
        border-color: #007aff; /* Apple Blue */
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
        outline: none;
    }

    /* 4. Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.8);
        text-align: center;
        transition: transform 0.2s ease;
        min-height: 160px; /* Enforce uniform height */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center; /* Horizontally center content */
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        color: #86868b; /* Apple Gray */
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        width: 100%; /* Ensure centering works */
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #1d1d1f;
        padding: 4px 0;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 14px;
        font-weight: 600;
        padding-top: 4px;
    }

    /* 5. Dataframes / Tables */
    div[data-testid="stDataFrame"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #e5e5ea;
    }
    
    /* 6. AI Analysis Panel (Glassmorphismish) */
    .ai-analysis-card {
        background: linear-gradient(135deg, #ffffff 0%, #fbfbfd 100%);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid white;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    .ai-analysis-title {
        font-size: 20px;
        font-weight: 700;
        color: #007aff;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* 7. Spinner */
    .stSpinner > div {
        border-top-color: #007aff !important;
    }

    /* Custom Metric Card Class (to match stMetric but allow custom colors) */
    .metric-card-container {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 35px 24px 24px 24px; /* Increased top padding, flex-start handles alignment */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.8);
        text-align: center;
        transition: transform 0.2s ease;
        height: 180px; /* Fixed height to ensure perfect uniformity */
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Align content to top */
        align-items: center;
        gap: 5px; /* Add gap for consistent spacing */
    }
    .metric-card-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 13px;
        color: #86868b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        padding: 4px 0;
    }
    .metric-delta {
        font-size: 14px;
        font-weight: 600;
        padding-top: 4px;
    }
    
    /* 8. Hide default Streamlit fluff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("AI Stock Agent")
st.markdown("<p style='color: #86868b; font-size: 18px; margin-top: -15px;'>Instant financial intelligence & market analysis.</p>", unsafe_allow_html=True)

# --- CHECK API KEY ---
if not os.getenv("GOOGLE_API_KEY"):
    st.warning("⚠️ GOOGLE_API_KEY not found. Please set it in your .env file to enable AI analysis.")


# --- SEACH BAR ---
ticker = st.text_input("Search Ticker", placeholder="Enter a Stock Ticker (e.g., AAPL, RELIANCE, TSLA)", help="Type a ticker symbol and hit Enter").strip().upper()

# --- MCP FUNCTIONS ---
async def get_metrics_via_mcp(ticker_symbol):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["stock_mcp_server.py"],
        env=os.environ
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_stock_metrics", arguments={"ticker": ticker_symbol})
            return result.content[0].text

async def get_analysis_via_mcp(ticker_symbol, company_name):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["stock_mcp_server.py"],
        env=os.environ
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("analyze_company", arguments={"ticker": ticker_symbol, "company_name": company_name})
            return result.content[0].text

# --- MAIN LOGIC ---
if ticker:

    with st.spinner(f"Getting live market data for {ticker}..."):
        try:
            # 1. Fetch Metrics
            stock_data_str = asyncio.run(get_metrics_via_mcp(ticker))
            
            # Parse result
            stock_data = None
            try:
                if stock_data_str.startswith("{"):
                    stock_data = ast.literal_eval(stock_data_str)
            except Exception as e:
                st.error(f"Error parsing data: {e}")

            if stock_data:
                if "error" in stock_data:
                    st.error(f"❌ {stock_data['error']}")
                else:
                    # --- SUCCESS STATE UI ---
                    company_name = stock_data.get('company_name', ticker)
                    currency = stock_data.get('currency', 'USD')
                    
                    st.markdown(f"<h2 style='text-align: center; margin-bottom: 25px;'>{company_name} <span style='color: #86868b; font-weight: 400;'>({ticker})</span></h2>", unsafe_allow_html=True)

                    # Metric Row 1
                    col1, col2, col3, col4 = st.columns(4)
                    
                    current_price = stock_data.get('current_price')
                    prev_close = stock_data.get('previous_close')
                    
                    delta = None
                    delta_percent = 0.0
                    
                    if current_price and prev_close:
                        delta = current_price - prev_close
                        delta_percent = (delta / prev_close) * 100
                    
                    # Determine Colors for Price Card
                    price_color = "#1d1d1f" # Default black
                    arrow = ""
                    if delta:
                        if delta > 0:
                            price_color = "#28cd41" # Apple Green
                            arrow = "↑"
                        elif delta < 0:
                            price_color = "#ff3b30" # Apple Red
                            arrow = "↓"
                            
                    with col1:
                        # Custom HTML for Price to control colors
                        st.markdown(f"""
                        <div class="metric-card-container">
                            <div class="metric-label">Price</div>
                            <div class="metric-value" style="color: {price_color};">
                                {current_price:,.2f} <span style="font-size: 16px; color: #86868b;">{currency}</span>
                            </div>
                            <div class="metric-delta" style="color: {price_color};">
                                {arrow} {abs(delta):,.2f} ({delta_percent:.2f}%)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        val = stock_data.get('market_cap')
                        fmt_val = f"{val/1e9:.2f}B" if isinstance(val, (int, float)) else "N/A"
                        # st.metric("Market Cap", fmt_val)
                        st.markdown(f"""
                        <div class="metric-card-container">
                            <div class="metric-label">Market Cap</div>
                            <div class="metric-value" style="color: #1d1d1f;">{fmt_val}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                         # st.metric("52W High", f"{stock_data.get('52_week_high', 'N/A')}")
                         st.markdown(f"""
                        <div class="metric-card-container">
                            <div class="metric-label">52W High</div>
                            <div class="metric-value" style="color: #1d1d1f;">{stock_data.get('52_week_high', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col4:
                        # st.metric("52W Low", f"{stock_data.get('52_week_low', 'N/A')}")
                        st.markdown(f"""
                        <div class="metric-card-container">
                            <div class="metric-label">52W Low</div>
                            <div class="metric-value" style="color: #1d1d1f;">{stock_data.get('52_week_low', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)



                    # --- Technicals Section (Bulleted) ---
                    st.markdown("### Technicals")
                    
                    display_keys = {
                        "open": "Open",
                        "day_high": "Day High",
                        "day_low": "Day Low",
                        "volume": "Volume",
                        "pe_ratio": "P/E Ratio",
                        "dividend_yield": "Div Yield",
                        "beta": "Beta"
                    }
                    
                    # Create a multi-column bullet layout for technicals
                    tech_cols = st.columns(4) # Distribute bullets across 4 columns for a clean look
                    
                    items_list = list(display_keys.items())
                    
                    for i, (key, label) in enumerate(items_list):
                        val = stock_data.get(key)
                        val_str = str(val) if val is not None else "N/A"
                        
                        # Calculate which column to place this item in
                        col_index = i % 4
                        with tech_cols[col_index]:
                            st.markdown(
                                f"""
                                <div style="background-color: white; padding: 10px; border-radius: 10px; border: 1px solid #e5e5ea; margin-bottom: 10px; text-align: center;">
                                    <div style="font-size: 12px; color: #86868b; text-transform: uppercase;">{label}</div>
                                    <div style="font-size: 16px; font-weight: 600; color: #1d1d1f;">{val_str}</div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )

                    st.markdown("<br>", unsafe_allow_html=True)

                    # --- AI Analysis Section ---
                    with st.spinner("Analyzing market structure & news..."):
                        analysis_text = asyncio.run(get_analysis_via_mcp(ticker, company_name))
                        
                        # Convert Markdown to HTML to properly verify nesting inside the div
                        import markdown
                        html_content = markdown.markdown(analysis_text)
                        
                        # Render the card with the content inside via a SINGLE st.markdown call
                        st.markdown(
                            f"""
                            <div class="ai-analysis-card">
                                <div class="ai-analysis-title">Company Details</div>
                                {html_content}
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

        except Exception as e:
            st.error(f"System Error: {str(e)}")
