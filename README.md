# AI Stock Agent Using MCP Workflow

## 1. Problem Statement
Investors currently need a unified, intelligent interface to access real-time market data and qualitative AI insights without navigating complex trading terminals.

## 2. Solution Overview
The solution is an **"AI Stock Agent"** that combines real-time financial data fetching with AI-driven analysis.

### Technologies Used 
* **Frameworks:** Streamlit, asyncio, Model Context Protocol (MCP), LangChain.
* **AI & Search:** Google Gemini (LLM), DuckDuckGo (Search).
* **Data & Utilities:** yfinance, pandas, python-dotenv.

---

## 3. System Architecture & Components
The solution is structured across four specific Python files.

### 1. `stock_data.py` (Data Logic)
**Purpose:** Acts as the "implementation detail" for fetching hard numbers.
* **Connection:** Uses the `yfinance` library to connect to the stock market.
* **Standardization:** Forces tickers to a standard format (e.g., converting "RELIANCE" to "RELIANCE.NS" for NSE).
* **Data Extraction:** Pulls a clean dictionary of metrics like `current_price`, `market_cap`, `pe_ratio`, and `52_week_high`.
* **Validation:** Checks if 1 year of history exists to ensure the stock is valid.

### 2. `ai_analysis.py` (Intelligence)
**Purpose:** Acts as the "brain" that provides qualitative context.
* **Search:** Uses `DuckDuckGo` to find real-time news and "company profile" information.
* **Synthesis:** Uses Google's **Gemini model** (via LangChain) to read and synthesize the search data.
* **Prompt Engineering:** Follows a strict prompt template (acting as a "financial analyst") to ignore fluff and output a clean Markdown summary.

### 3. `stock_mcp_server.py` (MCP Host)
**Purpose:** Bridges the gap between raw code and the agentic world.
* **Tool Wrapping:** Wraps the utility functions into MCP Tools: `get_stock_metrics` and `analyze_company`.
* **Server:** Runs a lightweight server (using `FastMCP`) that listens for standard input/output commands.
* **Abstraction:** It does not "know" about the UI; it simply waits for a tool call and returns raw string results.

### 4. `app.py` (Frontend Client)
**Purpose:** The visual dashboard the user interacts with.
* **MCP Client:** Starts `stock_mcp_server.py` as a background process and connects using `ClientSession`.
* **UI Construction:** Uses **Streamlit** with aggressive custom CSS to create "Apple-style" cards with specific shadows and fonts.
* **Orchestration:**
    1.  Calls `get_metrics_via_mcp` and renders metric cards.
    2.  [Calls `get_analysis_via_mcp` and renders the AI response in a glassmorphic card

---

## 4. Workflow Diagram

<img width="1098" height="867" alt="image" src="https://github.com/user-attachments/assets/90c40aea-fc38-494a-8059-374444f80ebd" />


**NOTE:** Use your own **API key** and **model**.
