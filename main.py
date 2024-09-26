import os
import csv
import pdfplumber
from PIL import Image
from pyzbar.pyzbar import decode
import shutil

def extract_top_barcode_from_pdf(pdf_path):
    print(f"Processing PDF: {pdf_path}")
    
    # Open the PDF file
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Get the first page of the PDF
            page = pdf.pages[0]
            print(f"Extracted page 1 of {pdf_path}")

            # Convert page to image
            img = page.to_image(resolution=300)
            print(f"Converted page to image for {pdf_path}")

            # Save the page image temporarily
            temp_image_path = 'temp_page.png'
            img.save(temp_image_path)
            print(f"Saved temporary image for {pdf_path}")

            # Decode all barcodes from the image
            barcode_data = decode(Image.open(temp_image_path))
            os.remove(temp_image_path)
            print(f"Decoded barcode(s) for {pdf_path}")

            # If multiple barcodes found, find the highest one (smallest y-coordinate)
            if barcode_data:
                top_barcode = min(barcode_data, key=lambda b: b.rect.top)
                barcode_text = top_barcode.data.decode("utf-8")
                print(f"Top barcode found on the first page of {os.path.basename(pdf_path)}: {barcode_text}")
                return barcode_text
            else:
                print(f"No barcodes found on {pdf_path}")

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return None  # Return None if no barcode is found

def process_pdf_folder(input_folder, output_folder, output_csv):
    print(f"Reading PDFs from folder: {input_folder}")
    
    # Get list of all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF(s) in folder")

    # Create CSV file if it doesn't exist
    if not os.path.exists(output_csv):
        with open(output_csv, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Original Filename', 'Barcode', 'New Filename'])  # Write header
        print(f"Created new CSV file: {output_csv}")

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        print(f"Starting extraction for {pdf_file}")
        
        # Extract the top barcode from the first page of the PDF
        barcode_text = extract_top_barcode_from_pdf(pdf_path)
        
        if barcode_text:
            # Use the first 6 characters of the barcode text to create a new filename
            new_filename = f"{barcode_text[:6]}.pdf"
            new_pdf_path = os.path.join(output_folder, new_filename)

            # Copy and rename the PDF file to the output folder
            shutil.copy2(pdf_path, new_pdf_path)

            # Append original filename, barcode, and new filename to CSV
            with open(output_csv, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([pdf_file, barcode_text, new_filename])
            
            print(f"Copied and renamed '{pdf_file}' to '{new_filename}' in '{output_folder}'")
        else:
            print(f"No valid barcode found for {pdf_file}")

if __name__ == "__main__":
    input_folder = "PDF_IN"  # Folder containing input PDFs
    output_folder = "PDF_OUT"  # Folder to save renamed PDFs
    output_csv = "barcodes.csv"  # CSV file to save the barcode data and new filenames

    process_pdf_folder(input_folder, output_folder, output_csv)
