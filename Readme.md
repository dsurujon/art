# Art utilities
This repo contains code that I use to digitize and process my art. While the most important parts are manual, some parts can use automation. 

## Digitization process
I start by scanning each piece at my library. They have a Xerox machine with a 11x17 inch scan area. For anything bigger, I take a photograph.     
I scan many pieces at once, and end up with multi-page PDF documents, where each page might contain 1-6 paintings depending on their size. In December 2025 I decided to scan the whole backlog of paintings I had in various portfolios, and ended up with a total of 16 PDF files, some having 20+ pages, with hundreds of individual paintings.      
I wanted to at least get the PDFs split into individual pages first, and saved as high quality png files. Then I could use any photo editing software to crop and adjust colors, and do this on a page-by-page basis. Once I get to individual page PNG files, I could even do this on my phone while sitting on the bus or whatnot.     
* `process_pdf.py`: this script processes all PDF files in a user-specified directory (`input_pdf_dir`), splitting each page into its own PNG image and saving it in an output directory (`output_png_dir`), where each file is named `[prefix]_[PDF_number]_[page number].png`. Usage: 
```
python3 process_pdf.py input_pdf_dir output_png_dir prefix
```
**Dependencies**: [PyMuPDF](https://github.com/pymupdf/PyMuPDF/releases/tag/1.26.7)