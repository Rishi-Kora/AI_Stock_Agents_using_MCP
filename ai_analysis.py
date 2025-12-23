import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

def get_company_details(ticker, company_name):
    """
    Uses Gemini and DuckDuckGo to find company details.
    Returns a summary and key details.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY not found in environment variables."

    try:
        llm = ChatGoogleGenerativeAI(model="gemma-3-12b-it", google_api_key=api_key, temperature=0.7)
        search = DuckDuckGoSearchRun()
        
        # Simple search for now, can be improved with an agent if complex logic is needed
        query = f"Latest recent news and company profile for {company_name} ({ticker})"
        try:
            search_results = search.run(query)
        except Exception:
            search_results = "Search rate limit exceeded. Please rely on your internal knowledge."
        
        prompt_template = """
        You are a financial analyst. Given the following search results about a company, provide a comprehensive summary.
        
        Company: {company_name} ({ticker})
        Search Results: {search_results}
        
        Please provide:
        1. A brief business summary (what they do).
        2. Key executives (CEO, etc) if mentioned or generally known.
        3. Recent major news or events.
        4. Official Website URL.

        Do NOT provide a table of key facts.
        Do NOT start with "Okay", "Here is", or similar conversational fillers.
        Do NOT include any disclaimers about "internal knowledge", "cutoff dates", or "search rate limits". Just provide the information directly.
        
        Format the output nicely in Markdown.
        """
        
        prompt = PromptTemplate(template=prompt_template, input_variables=["company_name", "ticker", "search_results"])
        chain = LLMChain(llm=llm, prompt=prompt)
        
        result = chain.run(company_name=company_name, ticker=ticker, search_results=search_results)
        return result

    except Exception as e:
        return f"Error performing AI analysis: {e}"
