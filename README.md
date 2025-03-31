# PDF Modification CrewAI Project
# Note that this a Shelved Project which is on Github for future references
This project implements a multi-agent system using CrewAI to attempt modifications on a PDF file based on user requests. It utilizes a Large Language Model (LLM) via Google Gemini to analyze the request and the PDF content, and custom tools to interact with the PDF.

## Project Goal

The primary goal is to create an agentic system that can:
1.  Read the content of a specified PDF (`word-file.pdf` in this project).
2.  Understand a user's natural language request for modifications (e.g., "add name and gender to the table").
3.  Attempt to apply these modifications to the PDF.
4.  Save the resulting PDF.

## Setup

1.  **Clone/Download:** Ensure you have the project files.
2.  **Environment:** It's recommended to use a virtual environment (like `venv` or `conda`).
3.  **Dependencies:** Install the required Python packages using pip:
    ```bash
    cd /path/to/Nihilent_Automation/automation
    pip install -e .
    ```
    This command reads the dependencies from `pyproject.toml` and installs them.
4.  **API Key:** Create a `.env` file in the `automation` directory with your Google Gemini API key:
    ```dotenv
    # automation/.env
    GEMINI_API_KEY=YOUR_API_KEY_HERE
    MODEL=gemini/gemini-2.5-pro-exp-03-25 # Or another compatible model
    ```

## Usage

1.  Navigate to the project's root directory (`automation`) in your terminal.
2.  Run the main script:
    ```bash
    python src/automation/main.py
    ```
3.  The script will prompt you to enter your desired modification for the `word-file.pdf`.
4.  The CrewAI system will execute, involving analysis and attempted modification steps.
5.  The output PDF will be saved as `modified_output.pdf` inside the `src/automation/` directory.

## Workflow

The system uses two main agents:

1.  **PDF Content and Table Analyst (`pdf_analyzer`):**
    *   Uses the `PDFContentReaderTool` to read the text and extract table structures (as Markdown) from the input PDF.
    *   Analyzes the user's request and the extracted content.
    *   Attempts to identify the exact text strings that need replacement to fulfill the request, being aware of the modification tool's limitations.
    *   Generates "Replace 'X' with 'Y'" instructions for the next agent.

2.  **PDF Modification Specialist (`pdf_modifier`):**
    *   Receives the replacement instructions from the analyzer.
    *   Uses the `PDFModifyAndSaveTool` to process the original PDF.
    *   **IMPORTANT:** This tool currently identifies where replacements *should* occur but **cannot reliably apply them** using the `pypdf` library without potentially corrupting the PDF or losing formatting. It copies the original page content to the output file.
    *   Saves the processed (likely unmodified) PDF to the specified output path.

## Custom Tools

*   **`PDFContentReaderTool`:** Reads text and extracts tables from the PDF using `pdfplumber`.
*   **`PDFModifyAndSaveTool`:** Attempts to parse replacement instructions and uses `pypdf` to read the original PDF and write an output file. **Crucially, it does not perform effective in-place text replacement due to `pypdf` limitations.**

## !! Critical Limitations !!

*   **Modification Ineffectiveness:** The core limitation is that the `PDFModifyAndSaveTool`, built using the `pypdf` library, **cannot reliably perform in-place text replacement** within the PDF structure, especially for tables or complex layouts, while preserving formatting.
*   **Output Content:** Although the system identifies the text intended for replacement, the current modification tool **copies the original page content** to the output file (`src/automation/modified_output.pdf`). Therefore, the output PDF will likely look identical to the original input PDF, even if the logs indicate replacements were identified.
*   **True Modification Requires Different Tools:** Achieving reliable PDF modification (especially for tables and formatting) would necessitate using more advanced libraries (e.g., ReportLab for reconstruction, PyMuPDF/fitz for lower-level manipulation, or commercial SDKs) and significantly more complex agent logic.

This project serves as a demonstration of a CrewAI workflow for PDF analysis but highlights the significant challenges in programmatically modifying complex PDF structures using standard open-source tools like `pypdf`.
