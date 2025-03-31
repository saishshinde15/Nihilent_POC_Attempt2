# Nihilent_POC_Attempt2

An automation project using CrewAI for PDF document processing and modification.

## Project Overview

This project demonstrates an automated system for analyzing and modifying PDF documents using CrewAI. It includes capabilities for:
- Reading and analyzing PDF content
- Extracting tables from PDFs
- Modifying specific text content within PDFs
- Preserving document structure during modifications

## Project Structure

```
automation/
├── src/
│   └── automation/
│       ├── __init__.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── crew.py
│       ├── main.py
│       └── tools/
│           ├── __init__.py
│           └── pdf_tools.py
├── tests/
├── knowledge/
├── pyproject.toml
└── README.md
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/saishshinde15/Nihilent_POC_Attempt2.git
cd Nihilent_POC_Attempt2
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

To modify a PDF file:

1. Place your PDF file in the project directory
2. Run the automation script:
```bash
python src/automation/main.py path/to/your.pdf "Your modification request"
```

Example:
```bash
python src/automation/main.py word-file.pdf "Add Saish under Jones with M as the Gender"
```

## Dependencies

- Python 3.10+
- CrewAI
- PyPDF2
- pdfplumber
- python-dotenv
- google-generativeai

## License

MIT License
