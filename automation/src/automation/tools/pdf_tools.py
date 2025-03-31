import os
import re # Import regex module
import pdfplumber
from pypdf import PdfReader, PdfWriter
from crewai.tools import BaseTool # Correct import path
from io import BytesIO

class PDFContentReaderTool(BaseTool):
    name: str = "PDF Content Reader Tool"
    description: str = "Reads and extracts text content from a specified PDF file."

    def _run(self, pdf_path: str) -> str:
        """Reads text content from the PDF."""
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at {pdf_path}"
        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    full_text += f"--- Page {i+1} Content ---\n"
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=1) # Adjust tolerances slightly if needed
                    if page_text:
                        full_text += f"{page_text}\n\n"

                    # Attempt to extract tables
                    tables = page.extract_tables()
                    if tables:
                        full_text += f"--- Tables on Page {i+1} ---\n"
                        for table_num, table in enumerate(tables):
                            full_text += f"Table {table_num + 1}:\n"
                            # Simple Markdown-like representation
                            if table:
                                # Create header row
                                header = "| " + " | ".join(str(cell) if cell is not None else '' for cell in table[0]) + " |"
                                separator = "|-" + "-|".join(['-' * len(str(cell) if cell is not None else '') for cell in table[0]]) + "-|"
                                full_text += header + "\n"
                                full_text += separator + "\n"
                                # Create data rows
                                for row in table[1:]:
                                    full_text += "| " + " | ".join(str(cell) if cell is not None else '' for cell in row) + " |\n"
                            full_text += "\n" # Add space after table
                        full_text += "\n" # Add space after all tables on page

            return full_text if full_text else "No text or table content found in the PDF."
        except Exception as e:
            return f"Error reading PDF content: {e}"

class PDFModifyAndSaveTool(BaseTool):
    name: str = "PDF Modify and Save Tool"
    description: str = (
        "Attempts to modify a PDF by replacing text and saves the result. "
        "Requires the original PDF path, a description of modifications "
        "(e.g., 'Replace \"Old Text\" with \"New Text\" on page 1'), and the output path. "
        "Note: Complex formatting preservation is challenging."
    )

    def _run(self, original_pdf_path: str, modifications_description: str, output_pdf_path: str) -> str:
        """
         Modifies the PDF based on text replacement instructions provided in the description and saves it.
         This is a simplified approach and might not handle all formatting perfectly.
         The 'modifications_description' should contain one or more instructions like "Replace 'text to find' with 'new text'".
         """
        if not os.path.exists(original_pdf_path):
            return f"Error: Original PDF file not found at {original_pdf_path}"

        tool_errors = [] # To collect errors during processing
        try:
            # Use regex to find all "Replace '...' with '...'" patterns
            # This handles variations in quoting and spacing better.
            # Pattern breakdown:
            # Replace\s+      : Match "Replace" followed by one or more spaces
            # (['"]?)         : Capture opening quote (optional) - Group 1
            # (.*?)           : Capture the text to find (non-greedy) - Group 2
            # \1              : Match the same closing quote as the opening one
            # \s+with\s+      : Match " with " surrounded by spaces
            # (['"]?)         : Capture opening quote for replacement (optional) - Group 3
            # (.*?)           : Capture the replacement text (non-greedy) - Group 4
            # \3              : Match the same closing quote as the opening one
            pattern = re.compile(r"Replace\s+(['\"]?)(.*?)\1\s+with\s+(['\"]?)(.*?)\3", re.IGNORECASE)
            matches = pattern.findall(modifications_description)

            replacements = {}
            if matches:
                for _, old_text, _, new_text in matches:
                    # Basic cleanup, might need more sophisticated handling
                    old_text_cleaned = old_text.strip()
                    new_text_cleaned = new_text.strip()
                    if old_text_cleaned: # Ensure we have something to replace
                        replacements[old_text_cleaned] = new_text_cleaned
            else:
                tool_errors.append(f"Could not parse any 'Replace X with Y' instructions from description: '{modifications_description}'")
                # Proceeding without replacements might just copy the file

            if not replacements and not tool_errors:
                 tool_errors.append("No specific text replacements identified from the description.")
                 # Proceeding without replacements might just copy the file

            reader = PdfReader(original_pdf_path)
            writer = PdfWriter()
            num_pages = len(reader.pages)
            print(f"[PDFModifyTool] INFO: Opened '{original_pdf_path}'. Found {num_pages} pages.")

            for page_num in range(num_pages):
                current_page_index = page_num + 1
                print(f"[PDFModifyTool] INFO: Processing page {current_page_index}...")
                page_added = False
                try:
                    page = reader.pages[page_num] # Get page by index
                    # Extract text using pypdf's built-in method for replacement context
                    print(f"[PDFModifyTool] DEBUG: Extracting text from page {current_page_index}...")
                    page_text = page.extract_text()
                    if page_text is None:
                        page_text = "" # Ensure page_text is always a string
                        print(f"[PDFModifyTool] WARNING: page.extract_text() returned None for page {current_page_index}.")

                    # --- Replacement Identification Logic (no actual modification here) ---
                    text_to_replace_found = False
                    if replacements: # Only check if there are replacements defined
                        for old_text in replacements.keys():
                            if old_text in page_text:
                                text_to_replace_found = True
                                print(f"[PDFModifyTool] DEBUG: Identified text '{old_text}' for potential replacement on page {current_page_index}.")
                                break # Break inner loop once found

                    # --- Always attempt to add the page ---
                    print(f"[PDFModifyTool] INFO: Attempting to add page {current_page_index} to writer...")
                    writer.add_page(page)
                    page_added = True
                    print(f"[PDFModifyTool] INFO: Page {current_page_index} added successfully to the writer object.")
                    if text_to_replace_found:
                        # Make this message stronger
                        print(f"[PDFModifyTool] WARNING: Text replacement was identified on page {current_page_index}, but the modification could NOT be applied due to pypdf limitations. Original page content was added.")
                        tool_errors.append(f"Identified replacement on page {current_page_index} but could not apply it.")

                except Exception as page_error:
                    page_err_msg = f"ERROR processing page {current_page_index}: {page_error}"
                    print(f"[PDFModifyTool] {page_err_msg}")
                    tool_errors.append(page_err_msg)
                    # Attempt to add the original page even if processing failed
                    if not page_added:
                         try:
                             # Re-fetch the page object in case the original 'page' variable is problematic
                             page_obj_on_error = reader.pages[page_num]
                             print(f"[PDFModifyTool] WARNING: Adding original page {current_page_index} after processing error...")
                             writer.add_page(page_obj_on_error)
                             print(f"[PDFModifyTool] WARNING: Original page {current_page_index} added after error.")
                         except Exception as add_error:
                             critical_err_msg = f"CRITICAL: Failed to add page {current_page_index} even after initial processing error: {add_error}"
                             print(f"[PDFModifyTool] {critical_err_msg}")
                             tool_errors.append(critical_err_msg)

            # --- Writing the output file ---
            print(f"[PDFModifyTool] INFO: Processed all pages. Attempting to write to '{output_pdf_path}'...")
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_pdf_path)
            try:
                if output_dir and not os.path.exists(output_dir):
                    print(f"[PDFModifyTool] INFO: Creating output directory '{output_dir}'...")
                    os.makedirs(output_dir)
            except Exception as dir_error:
                 print(f"[PDFModifyTool] ERROR: Failed to create output directory '{output_dir}': {dir_error}")
                 tool_errors.append(f"Failed to create output directory: {dir_error}")
                 # Return early if directory creation fails
                 return f"Error: Failed to create output directory '{output_dir}'. PDF not saved."

            try:
                with open(output_pdf_path, "wb") as output_file:
                    writer.write(output_file)
                print(f"[PDFModifyTool] INFO: Successfully wrote output PDF to '{output_pdf_path}'.")
            except Exception as write_error:
                print(f"[PDFModifyTool] CRITICAL: Failed to write output PDF '{output_pdf_path}': {write_error}")
                tool_errors.append(f"Failed to write output PDF: {write_error}")
                # Return error if writing fails
                return f"Error: Failed to write output PDF to '{output_pdf_path}'. Reason: {write_error}"

            # --- Construct the final return message ---
            # Ensure we use the correct output_pdf_path variable passed to the tool
            result_message = f"PDF processing completed. Output saved to {output_pdf_path}. Replacements identified: {replacements}."
            if tool_errors:
                result_message += f" IMPORTANT NOTE: Text replacements were identified but **COULD NOT BE APPLIED** due to library (pypdf) limitations or errors ({'; '.join(tool_errors)}). The output file likely contains the original, unmodified content. Please verify the output file at {output_pdf_path}."
            else:
                 # Ensure we use the correct output_pdf_path variable passed to the tool
                 result_message += f" IMPORTANT NOTE: Text replacements were identified but **COULD NOT BE APPLIED** due to library (pypdf) limitations. The output file likely contains the original, unmodified content. Please verify the output file at {output_pdf_path}."
            return result_message

        except Exception as e:
            return f"Error modifying and saving PDF: {e}"

# Instantiate tools for export
pdf_reader_tool = PDFContentReaderTool()
pdf_modifier_tool = PDFModifyAndSaveTool()
