import os 
import pymupdf
import cairosvg
import markdown
from weasyprint import HTML


def convert_document(user_input, output_user):
    _, input_ext = os.path.splitext(user_input.lower())
    base_output, output_ext = os.path.splitext(output_user)
    output_ext = output_ext.lower()

    try:
        # 1. Image -> PDF
        if input_ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"] and output_ext == ".pdf":
            doc = pymupdf.open(user_input)
            pdf_bytes = doc.convert_to_pdf()
            doc.close()

            with pymupdf.open("pdf", pdf_bytes) as pdf_doc:
                pdf_doc.save(output_user)
            print(f"Saved PDF: {output_user}")

        # 2. PDF -> Images
        elif input_ext == ".pdf" and output_ext in [".png", ".jpg", ".jpeg"]:
            with pymupdf.open(user_input) as doc:
                for i, page in enumerate(doc):
                    pix = page.get_pixmap(dpi=150)
                    pix.save(f"{base_output}_page_{i+1}{output_ext}")
                print(f"Extracted {len(doc)} pages using prefix: {base_output}_page_*")

        # 3. Markdown -> HTML / PDF
        elif input_ext in [".md", ".markdown"]:
            with open(user_input, "r", encoding="utf-8") as f:
                html_str = f"<html><body>{markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])}</body></html>"

            if output_ext == ".html":
                with open(output_user, "w", encoding="utf-8") as f:
                    f.write(html_str)
            elif output_ext == ".pdf":
                HTML(string=html_str).write_pdf(output_user)
            print(f"Saved: {output_user}")

        # 4. SVG -> PNG / PDF
        elif input_ext == ".svg" and output_ext in [".png", ".pdf"]:
            svg_convert = {".png": cairosvg.svg2png, ".pdf": cairosvg.svg2pdf}
            svg_convert[output_ext](url=user_input, write_to=output_user)
            print(f"Saved: {output_user}")

        else:
            print(f"Unsupported conversion: {input_ext} to {output_ext}")

    except FileNotFoundError:
        print(f"Error: File '{user_input}' not found.")
    except Exception as e:
        print(f"Conversion failed: {e}")



def merge_pdfs(pdf_list, output_user):
    # Create a new PDF document
    merged_pdf = pymupdf.open()
    
    # Iterate through each PDF file
    for pdf_path in pdf_list:
        # Open the PDF
        pdf_document = pymupdf.open(pdf_path)
        
        # Insert all pages from the current PDF
        merged_pdf.insert_pdf(pdf_document)
        
        # Close the current PDF
        pdf_document.close()
    
    # Save the merged PDF
    merged_pdf.save(output_user)
    merged_pdf.close()
