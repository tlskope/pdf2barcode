import os
import csv
import pdfplumber
from PIL import Image
from pyzbar.pyzbar import decode
import shutil

def extract_barcode_from_pdf(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through each page
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            # Convert page to image
            img = page.to_image(resolution=300)
            
            # Save the page image temporarily
            temp_image_path = 'temp_page.png'
            img.save(temp_image_path)

            # Decode the barcode from the image
            barcode_data = decode(Image.open(temp_image_path))
            os.remove(temp_image_path)

            # If barcode data found
            if barcode_data:
                # Extract barcode text
                barcode_text = barcode_data[0].data.decode("utf-8")
                
                print(f"Barcode found on page {page_num + 1} of {os.path.basename(pdf_path)}: {barcode_text}")
                return barcode_text  # Return barcode text after finding the first one

    return None  # Return None if no barcode is found

def process_pdf_folder(input_folder, output_folder, output_csv):
    # Get list of all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    # Create CSV file if it doesn't exist
    if not os.path.exists(output_csv):
        with open(output_csv, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Original Filename', 'Barcode', 'New Filename'])  # Write header

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        
        # Extract the barcode from the PDF
        barcode_text = extract_barcode_from_pdf(pdf_path)
        
        if barcode_text:
            # Use part of the barcode text to create a new filename (e.g., first 10 characters)
            new_filename = f"{barcode_text[:10]}.pdf"
            new_pdf_path = os.path.join(output_folder, new_filename)

            # Copy and rename the PDF file to the output folder
            shutil.copy2(pdf_path, new_pdf_path)

            # Append original filename, barcode, and new filename to CSV
            with open(output_csv, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([pdf_file, barcode_text, new_filename])
            
            print(f"Copied and renamed '{pdf_file}' to '{new_filename}' in '{output_folder}'")

if __name__ == "__main__":
    input_folder = "PDF_IN"  # Folder containing input PDFs
    output_folder = "PDF_OUT"  # Folder to save renamed PDFs
    output_csv = "barcodes.csv"  # CSV file to save the barcode data and new filenames
    
    process_pdf_folder(input_folder, output_folder, output_csv)
