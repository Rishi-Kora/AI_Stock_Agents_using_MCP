from mcp.server.fastmcp import FastMCP
from utils.stock_data import get_stock_data
from utils.ai_analysis import get_company_details
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("AI Stock Agent")

@mcp.tool()
def get_stock_metrics(ticker: str) -> str:
    """
    Fetches stock metrics for a given ticker.
    Returns a string representation of the data dictionary.
    """
    data = get_stock_data(ticker)
    
    # Return the dictionary (or error dictionary) as a string
    return str(data)

@mcp.tool()
def analyze_company(ticker: str, company_name: str) -> str:
    """
    Get AI analysis of a company based on ticker and company name.
    """
    return get_company_details(ticker, company_name)

if __name__ == "__main__":
    mcp.run()
