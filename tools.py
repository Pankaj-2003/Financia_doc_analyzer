## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.utilities import GoogleSerperAPIWrapper

@tool("Search the internet")
def search_tool(query: str) -> str:
    """Useful for when you need to answer questions about current events or the current state of the world by searching the internet."""
    search = GoogleSerperAPIWrapper()
    return search.run(query)

@tool("Read Financial Document")
def read_data_tool(path: str = 'data/sample.pdf') -> str:
    """Tool to read data from a pdf file from a path."""
    import os
    if not os.path.exists(path):
        return "File not found."

    loader = PyPDFLoader(file_path=path)
    docs = loader.load()

    full_report = ""
    for data in docs:
        content = data.page_content
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")
        full_report += content + "\n"
        
    return full_report

## Creating Investment Analysis Tool
@tool("Analyze Investment Potential")
def analyze_investment_tool(financial_document_data: str) -> str:
    """A custom tool to perform simulated quantitative investment analysis on financial data."""
    # Clean up the data format
    processed_data = financial_document_data.replace("  ", " ").lower()
    
    # Simple simulated logic based on keywords in the text
    score = 50
    if "revenue increase" in processed_data or "growth" in processed_data:
        score += 20
    if "profit" in processed_data or "margin improvement" in processed_data:
        score += 15
    if "debt" in processed_data or "loss" in processed_data:
        score -= 20
        
    recommendation = "Hold"
    if score >= 75:
        recommendation = "Strong Buy"
    elif score >= 60:
        recommendation = "Buy"
    elif score < 40:
        recommendation = "Sell"
        
    return f"Investment Score: {score}/100. Quantitative Recommendation: {recommendation}. Mention this score explicitly in your recommendation."

## Creating Risk Assessment Tool
@tool("Assess Financial Risk")
def create_risk_assessment_tool(financial_document_data: str) -> str:
    """A custom tool to evaluate risk factors and calculate a volatility index."""
    processed_data = financial_document_data.lower()
    
    risk_factors = []
    if "regulatory" in processed_data or "lawsuit" in processed_data:
        risk_factors.append("High Legal/Regulatory Risk")
    if "decline" in processed_data or "decrease" in processed_data:
        risk_factors.append("Revenue Volatility")
    if "inflation" in processed_data or "macroeconomic" in processed_data:
        risk_factors.append("Macroeconomic Exposure")
        
    risk_level = "Low"
    if len(risk_factors) >= 2:
        risk_level = "High"
    elif len(risk_factors) == 1:
        risk_level = "Medium"
        
    factors_str = ", ".join(risk_factors) if risk_factors else "None detected"
    
    return f"Calculated Risk Level: {risk_level}. Identified Risk Factors: {factors_str}. Please use these exact factors in your assessment."