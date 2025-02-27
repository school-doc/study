
import os
import fitz  # PyMuPDF for editing PDFs
from pypdf import PdfReader, PdfWriter  # PyPDF for splitting PDFs


# Configuration
# Add whatever strings you want to remove from the PDFs
# This can be names, email addresses, or any other sensitive information
# The script will redact all instances of these strings
# ex: NAMES_TO_REMOVE = ["John Smith", "John", "Smith", "johnsmith@gmail.com"]
# Change names and emails to yours
NAMES_TO_REMOVE = ["John Smith", "johnsmith@gmail.com"]

# Only change these if you are experimenting or developing something
PDF_FOLDER = "."  # Path to the folder containing PDFs ('.' for current directory)
SIZE_LIMIT_MB = 100  # MB
CHUNK_SIZE_MB = 90. # MB


def remove_name_from_pdf(filepath):
    """Removes the specified name from the given PDF file."""
    doc = fitz.open(filepath)
    modified = False  # Track if changes were made

    for page in doc:
        for name in NAMES_TO_REMOVE:
            text_instances = page.search_for(name)
            for inst in text_instances:
                page.add_redact_annot(inst)
            if text_instances:
                page.apply_redactions()
                modified = True

    if modified:
        doc.save(filepath, incremental=True, encryption=0)
        print(f"Redacted: {filepath}")
    doc.close()
    
def split_large_pdf(filepath):
    """Splits large PDFs into chunks of 90MB.
        Due to github's file size limit, we will split the large PDFs into smaller chunks.
    """
    file_size = os.path.getsize(filepath) / (1024 * 1024)  # Convert bytes to MB

    if file_size < SIZE_LIMIT_MB:
        return  # Skip if below 100MB

    print(f"Splitting large PDF: {filepath} ({file_size:.2f}MB)")

    reader = PdfReader(filepath)
    total_pages = len(reader.pages)
    writer = PdfWriter()
    part = 1
    current_size = 0
    pages_per_chunk = []

    # Determine the number of pages per chunk based on file size
    estimated_chunks = int(file_size // CHUNK_SIZE_MB) + 1
    pages_per_chunk = max(1, total_pages // estimated_chunks)

    for i, page in enumerate(reader.pages):
        writer.add_page(page)

        # Save when reaching chunk size or last page
        if (i + 1) % pages_per_chunk == 0 or i == total_pages - 1:
            output_filename = f"{filepath[:-4]}_part{part}.pdf"
            with open(output_filename, "wb") as output_pdf:
                writer.write(output_pdf)

            print(f"Created: {output_filename}")

            writer = PdfWriter()  # Reset writer for next chunk
            part += 1

    # Only delete the original if at least 2 parts were created
    if part > 2:
        os.remove(filepath)
        print(f"Deleted original: {filepath}")
    else:
        print(f"Skipping deletion: {filepath} (only one part created)")

def process_pdfs(folder):
    """Processes all PDFs in the given folder and its subfolders."""
    for root, _, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".pdf"):
                filepath = os.path.join(root, filename)

                remove_name_from_pdf(filepath)
                split_large_pdf(filepath)


# Run the script
process_pdfs(PDF_FOLDER)
print("Processing complete!")
