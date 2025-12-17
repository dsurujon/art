# PDF processing 

import pymupdf
import os
import sys

"""
This script processes all PDF files in a specified input directory, 
converting each page to a high-resolution PNG image.
The output PNG files are saved in a specified output directory with 
filenames formatted as [prefix]_[PDF_number]_[page number].png.

working example: 
input_pdf_dir = '/mnt/c/Users/defne/Documents/Art/Finished_pieces/scans_20251215/'
output_png_dir = '/mnt/c/Users/defne/Documents/Art/Finished_pieces/scans_20251215/pngs/'
prefix = '20251215_scan'
"""


# Process all PDF files in the input directory, saving each page as a PNG in the output directory
def process_pdfs(input_pdf_dir, output_png_dir, prefix):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_png_dir):
        os.makedirs(output_png_dir)

    # List all PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_pdf_dir) if f.lower().endswith('.pdf')]
    pdf_files.sort()  # Sort for consistent numbering

    # Iterate over each PDF file
    for pdf_idx, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(input_pdf_dir, pdf_file)
        doc = pymupdf.open(pdf_path)  # Open the PDF file
        # Iterate over each page in the PDF
        for page_idx in range(len(doc)):
            page = doc.load_page(page_idx)  # Load the page
            pix = page.get_pixmap(dpi=300)  # Render page to a high-res PNG
            # Construct output filename: [prefix]_[PDF_number]_[page number].png
            out_name = f"{prefix}_{pdf_idx}_{page_idx+1}.png"
            out_path = os.path.join(output_png_dir, out_name)
            pix.save(out_path)  # Save the PNG file
        doc.close()  # Close the PDF file

# Entry point for command-line usage
def main():
    # Check for correct number of arguments
    if len(sys.argv) != 4:
        print(len(sys.argv))
        print("Usage: python3 process_pdf.py input_pdf_dir output_png_dir prefix")
        sys.exit(1)
    input_pdf_dir = sys.argv[1]
    output_png_dir = sys.argv[2]
    prefix = sys.argv[3]
    process_pdfs(input_pdf_dir, output_png_dir, prefix)

if __name__ == "__main__":
    main()


