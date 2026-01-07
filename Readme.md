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
Following this, I crop each png into original pieces by hand.     

## Archiving 
This is a system I am working on in order to archive the art pieces I have at hand. I start from high-quality scans or photos and generate print-ready, web and thumbnail derivatives for each image, and store artwork metadata (title, medium, size, availability, descriptions) in a relational database.     

```
art_archive/
├── originals/        # Archival images (never overwritten)
│   └── <slug>/
│       └── main.JPEG
├── derivatives/      # Script-generated images
│   └── <slug>/
│       ├── web_2400px.jpg
│       └── thumb_600px.jpg
├── metadata/
│   └── metadata.csv    # Batch metadata entry for all works
├── db/
│   └── archive.db    # SQLite database (authoritative metadata)
└── scripts/          # Ingest, image processing, export utilities
```

Each artwork is identified by a stable `slug`, which is used consistently across
folders, filenames, database records, and URLs. The archive uses a relational SQLite database to store:
- Artwork metadata (title, year, medium, size, availability)
- Image records (role, path, dimensions, color profile)
Images are stored on disk, not in the database. All derivatives are reproducible from the original files.    
#### Workflow
1, Scan or photograph artwork → save as `originals/<slug>/main.JPEG`
2. Add a row to `metadata/metadata.csv`
3. Run the build script `scripts/build.py`
   1. Initializes the database 
   2. Inserts artwork into the database
   3. Generates image derivatives
   4. Registers image paths and metadata
4. Run the interactive tagging script `scripts/tag.py`
   1. Will run through each piece
   2. Ask you to add/remove tags interactively
5. 