# Financial Document Analyzer - Debug Report

This document serves as a comprehensive report detailing the debugging process, the specific issues found, and the steps taken to resolve them in the Financial Document Analyzer project. It also includes setup instructions and API documentation.

---

## Bugs Found and Fixed

### 1. Dependency and Environment Issues
*   **Bug in `README.md`**: Typo in setup instructions referring to `requirement.txt` instead of `requirements.txt`.
    *   **Fix**: Corrected the typo to avoid confusion during setup.
*   **Bug in `requirements.txt`**: Strict version pinning (e.g., `openai==1.34.1`, `numpy==1.26.4`) caused severe dependency resolution conflicts during `pip install`, especially for Windows/Python 3.13 environments.
    *   **Fix**: Relaxed version constraints to allow `pip` to resolve compatible versions automatically. Retained `crewai==0.130.0` as it was explicitly required.
*   **Incompatibility with `crewai_tools`**: The `embedchain` dependency within `crewai_tools` failed to build.
    *   **Fix**: Removed the `crewai_tools` dependency and implemented custom tools using LangChain and native CrewAI decorators to replicate the required functionality without the problematic dependency.

### 2. Issues in `tools.py`
*   **Missing Import**: `FinancialDocumentTool.read_data_tool` attempted to instantiate a `Pdf` class that was never imported or defined.
    *   **Fix**: Imported and utilized `PyPDFLoader` from `langchain_community.document_loaders` to properly read and extract text from PDF files.
*   **Infinite Loop**: The `analyze_investment_tool` contained a faulty `while` loop intended to remove double spaces, which caused an infinite loop due to incorrect indexing logic.
    *   **Fix**: Replaced the dangerous `while` loop with a simple and safe string replacement: `content.replace("  ", " ")`.
*   **Validation Errors (CrewAI 0.130.0)**: The `read_data_tool` functions were not properly recognized as valid tools by CrewAI, causing the application to crash during agent initialization.
    *   **Fix**: Refactored the tools to be standalone functions and decorated them with the native `@tool` decorator from `crewai.tools` to ensure compatibility.

### 3. Issues in `agents.py`
*   **Undefined Variable**: The LLM initialization contained a syntax error: `llm = llm`, where `llm` was undefined.
    *   **Fix**: Properly initialized the LLM using `ChatOpenAI(model="gpt-4o", openai_api_key=api_key)` from `langchain_community.chat_models`.
*   **Unprofessional Prompts**: The `role`, `goal`, and `backstory` for the agents (Financial Analyst, Verifier, Investment Advisor, Risk Assessor) were humorous and unprofessional.
    *   **Fix**: Rewrote the prompts to reflect serious, professional financial personas capable of delivering accurate insights.
*   **Missing Environment Variable**: The LLM required an OpenAI API key, but the code did not load it correctly from the `env` file.
    *   **Fix**: Configured `python-dotenv` explicitly to load the `env` file (`load_dotenv('env')`) and retrieved the key using `os.environ.get("OPENAI_API_KEY")`.

### 4. Issues in `task.py`
*   **Incorrect Tool Assignment**: Tools were incorrectly assigned or missing from the tasks, limiting the agents' capabilities.
    *   **Fix**: Explicitly mapped the `read_data_tool` and `search_tool` to the appropriate tasks (`verification`, `analyze_financial_document`, `investment_analysis`, `risk_assessment`).
*   **Unprofessional Task Descriptions**: Similar to the agents, the task descriptions lacked professional framing.
    *   **Fix**: Updated the task descriptions and expected outputs to demand structured, high-quality financial analysis.

### 5. Issues in `main.py`
*   **Name Shadowing**: The FastAPI endpoint was named `analyze_financial_document`, which shadowed the task of the same name imported from `task.py`.
    *   **Fix**: Renamed the API endpoint function to `analyze_document_endpoint` to resolve the conflict.
*   **Incomplete Pipeline**: The `run_crew` function only initialized the `verifier` and `analyze_financial_document` tasks, ignoring the investment advisor and risk assessor entirely.
    *   **Fix**: Updated the `Crew` initialization to include all four agents and their respective tasks in a `Process.sequential` execution flow.
*   **Uvicorn Reload Error**: The script attempted to run Uvicorn with `reload=True` by passing the `app` instance directly, which is not supported and caused a crash.
    *   **Fix**: Changed the Uvicorn execution to pass the module string `"main:app"` instead.
*   **Hardcoded File Path (Critical Bug)**: The `file_path` of the dynamically uploaded PDF was never passed to the CrewAI tasks. The agents were unknowingly analyzing a hardcoded `data/sample.pdf` on every request.
    *   **Fix**: Updated `task.py` descriptions to include a dynamic `{file_path}` variable and updated `main.py` to inject the correct path via `financial_crew.kickoff({'query': query, 'file_path': file_path})`.

---

## 🚀 Setup and Usage Instructions

### Prerequisites
*   Python 3.10 or higher.
*   An active OpenAI API Key.

### Installation

1.  **Clone the Repository** and navigate to the project directory:
    ```bash
    cd financial-document-analyzer-debug
    ```

2.  **Set up the Environment**:
    Open the `env` file in the root directory and add your OpenAI API Key:
    ```env
    OPENAI_API_KEY=your-actual-api-key-here
    ```

3.  **Install Dependencies**:
    Run the following command to install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server**:
    Start the FastAPI application using Uvicorn:
    ```bash
    uvicorn main:app --port 8000
    ```
    *(Note: You can also use `python main.py` to start the server).*

    The API will now be accessible at `http://127.0.0.1:8000`.
    Swagger URL : http://localhost:8000/docs

---

## 🕵️ AgentOps Tracing

This project integrates with **AgentOps** to provide comprehensive execution traces for all CrewAI agents. You can monitor the detailed execution steps, token usage, time elapsed, and tool invocations in real-time.

You can view the traces here: [https://app.agentops.ai/traces](https://app.agentops.ai/traces)

*Note: Make sure to sign up for a free AgentOps API Key and add it to your `env` file as `AGENTOPS_API_KEY` to enable this feature.*

---

## API Documentation

### 1. Health Check
*   **URL**: `/`
*   **Method**: `GET`
*   **Description**: Verifies that the API server is up and running.
*   **Response**:
    ```json
    {
      "message": "Financial Document Analyzer API is running"
    }
    ```

### 2. Analyze Document
*   **URL**: `/analyze`
*   **Method**: `POST`
*   **Description**: Uploads a financial PDF document and triggers the CrewAI multi-agent pipeline to generate an analysis, investment recommendation, and risk assessment based on the provided query.
*   **Content-Type**: `multipart/form-data`
*   **Parameters**:
    *   `file` (Required): The PDF document to be analyzed (e.g., `application/pdf`).
    *   `query` (Optional): A specific question or instruction for the AI (e.g., "Summarize the Q3 revenue metrics"). Defaults to "Analyze this financial document for investment insights".
*   **Example Request (cURL)**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/analyze" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@/path/to/your/financial_report.pdf" \
         -F "query=What are the key risk factors mentioned?"
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "status": "success",
      "query": "What are the key risk factors mentioned?",
      "analysis": "[Detailed markdown response generated by the AI Crew...]",
      "file_processed": "financial_report.pdf"
    }
    ```
*   **Error Response (500 Internal Server Error)**:
    ```json
    {
      "detail": "Error processing financial document: [Error specifically detailed here]"
    }
    ```
