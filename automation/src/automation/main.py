#!/usr/bin/env python
import os
import sys
import warnings
from automation.crew import Automation

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file runs the PDF modification crew.

def run():
    """
    Run the PDF modification crew.
    Takes user input for the modification request.
    """
    # Define the path to the PDF relative to this script's location
    script_dir = os.path.dirname(__file__)
    pdf_filename = "word-file.pdf" # The PDF provided in the root 'automation' directory
    pdf_path = os.path.abspath(os.path.join(script_dir, '..', '..', pdf_filename))

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at expected location: {pdf_path}")
        sys.exit(1)

    # Get user input for the modification request
    user_request = input("Please enter the modification you want to make to the PDF: ")

    if not user_request:
        print("Error: No modification request provided.")
        sys.exit(1)

    # Define the desired output path (relative to script location)
    output_pdf_filename = "modified_output.pdf"
    output_pdf_path = os.path.abspath(os.path.join(script_dir, output_pdf_filename)) # Save in src/automation/

    # Prepare inputs for the crew
    inputs = {
        'pdf_path': pdf_path,
        'user_request': user_request,
        'output_path': output_pdf_path # Add output path to inputs
    }

    print(f"\nStarting PDF modification crew for file: {pdf_path}")
    print(f"User request: {user_request}\n")

    try:
        # Instantiate and kickoff the crew
        result = Automation().crew().kickoff(inputs=inputs)
        print("\nCrew finished execution.")
        print("Result:")
        print(result) # The result should be the output of the last task (modify_pdf_task)
        print(f"\nCheck for the modified file at: {os.path.join(os.path.dirname(pdf_path), 'modified_output.pdf')}")

    except Exception as e:
        print(f"\nAn error occurred while running the crew: {e}")
        # Consider adding more detailed error logging if needed
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

# --- Optional: Keep or remove train/replay/test functions as needed ---
# def train(): ...
# def replay(): ...
# def test(): ...

if __name__ == "__main__":
    run()
