## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor, reporting_agent
from tools import search_tool, read_data_tool, analyze_investment_tool, create_risk_assessment_tool

verification = Task(
    description="Analyze the uploaded file located at {file_path} to verify if it contains valid financial data.\n\
Ensure that the document is relevant to the requested analysis.",
    expected_output="A confirmation on whether the document is a valid financial report, "
                    "including a brief summary of the document's main subjects.",
    agent=verifier,
    tools=[read_data_tool]
)

analyze_financial_document = Task(
    description="Perform a comprehensive analysis of the financial document at {file_path} to answer the user's query: {query}.\n\
You should highlight key revenue metrics, profit margins, and significant operational milestones.",
    expected_output="A highly structured and detailed financial analysis report highlighting "
                    "key metrics, performance indicators, and operational insights.",
    agent=financial_analyst,
    tools=[search_tool, read_data_tool]
)

investment_analysis = Task(
    description="Based on the financial analysis from {file_path}, recommend strategic investment actions.\n\
Focus on concrete financial data and reliable market trends. User query: {query}",
    expected_output="A professional list of investment recommendations, weighing the pros and cons, "
                    "with clear justification based on the analyzed data.",
    agent=investment_advisor,
    tools=[search_tool, read_data_tool, analyze_investment_tool]
)

risk_assessment = Task(
    description="Evaluate the potential risks involved in the current financial state ({file_path}) or planned investments.\n\
Produce a measured, evidence-based risk assessment.",
    expected_output="A comprehensive risk assessment outlining potential market vulnerabilities, "
                    "operational risks, and suggested hedging strategies.",
    agent=risk_assessor,
    tools=[search_tool, read_data_tool, create_risk_assessment_tool]
)

final_report_task = Task(
    description="Take all the previous analyses and synthesize them into a final executive summary for the user. \n\
You MUST output the final response in Markdown format. You MUST include exactly the following headings exactly as written:\n\
- Investment recommendations\n\
- Risk assessment\n\
- Market insights\n\
Make sure the content under each heading is detailed, clearly formatted with bullet points if necessary, and directly addresses the user query: {query}",
    expected_output="A beautifully formatted Markdown document containing exactly the requested sections and the synthesized research.",
    agent=reporting_agent
)