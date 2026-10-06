import os
from PIL import Image
import qrcode
import imageio as iio
from rapidocr_onnxruntime import RapidOCR
from pypdfium2 import PdfDocument
import numpy as np
import pandas as pd
 


def convert_image(user_input, output_user):
    try:
        img = Image.open(user_input)
        
        # Convert RGBA transparency to RGB if saving as JPG
        _, ext = os.path.splitext(output_user.lower())
        if ext in [".jpg", ".jpeg"] and img.mode in ("RGBA", "LA", "P"):
            conv = img.convert("RGB")
            conv.save(output_user)
        else:
            img.save(output_user)
            
        print(f"Saved: {output_user}")
    except FileNotFoundError:
        print(f"File not found: {user_input}")
    except Exception as e:
        print(f"Error converting image: {e}")

def text_to_qr(user_input , output_user):
  try:
     qr = qrcode.QRCode(
     version=1,
     error_correction=qrcode.constants.ERROR_CORRECT_L,
     box_size=10,
     border=4,
     )
     qr.add_data(user_input)
     qr.make(fit=True)
     img = qr.make_image(fill_color="black", back_color="white")
     img.save(output_user)
     print(f"Saved: {output_user}")
  except Exception as e :
      print(f"Error generated Qr Code: {e}")


import os
from PIL import Image

def image_to_gif(user_input, output_user):
    valid_exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
    
    try:
        # Collect file paths
        if isinstance(user_input, str) and os.path.isdir(user_input):
            files = [os.path.join(user_input, f) for f in os.listdir(user_input) if f.lower().endswith(valid_exts)]
            files.sort()
        elif isinstance(user_input, str) and os.path.isfile(user_input):
            files = [user_input]
        elif isinstance(user_input, (list, tuple)):
            files = user_input
        else:
            print(f"Invalid path or input: {user_input}")
            return

        if not files:
            print("No valid image files found.")
            return

        # Load images and convert to adaptive 256-color palette mode (P)
        frames = []
        for f in files:
            with Image.open(f) as img:
                # Quantize forces palette compression (cuts file size by ~80-90%)
                converted = img.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                frames.append(converted)

        # Save with optimization flags enabled
        frames[0].save(
            output_user,
            format="GIF",
            append_images=frames[1:],
            save_all=True,
            duration=500,
            loop=0,
            optimize=True  # Enables delta-frame & palette optimization
        )
        print(f"Compressed GIF created: {output_user}")

    except Exception as e:
        print(f"Error creating GIF: {e}")

engine = RapidOCR()


def image_to_text(input_path, output_path):
    """
    Extracts text from an image, a folder of images, or a PDF file using RapidOCR.
    """
    try:
        valid_img_exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff")
        extracted_text = []

        # Case 1: PDF Document
        if os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
            print(f"Processing PDF OCR on '{input_path}'...")
            
            pdf = PdfDocument(input_path)
            
            for i, page in enumerate(pdf):
                # Render page to PIL Image at 200 DPI
                pil_image = page.render(scale=200 / 72).to_pil()
                
                # Convert PIL Image to NumPy array for RapidOCR
                img_np = np.array(pil_image)
                
                # Pass NumPy array to RapidOCR
                result, _ = engine(img_np)
                if result:
                    lines = [line[1] for line in result]
                    extracted_text.append(f"--- Page {i + 1} ---\n" + "\n".join(lines))
                else:
                    extracted_text.append(f"--- Page {i + 1} ---\n[No readable text found]")

        # Case 2: Single Image File
        elif os.path.isfile(input_path) and input_path.lower().endswith(valid_img_exts):
            print(f"Processing Image OCR on '{input_path}'...")
            result, _ = engine(input_path)
            if result:
                lines = [line[1] for line in result]
                extracted_text.append("\n".join(lines))

        # Case 3: Folder of Images
        elif os.path.isdir(input_path):
            files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(valid_img_exts)]
            files.sort()

            if not files:
                print("No supported image files found in folder.")
                return False

            print(f"Processing OCR on {len(files)} images inside '{input_path}'...")
            for img_file in files:
                result, _ = engine(img_file)
                if result:
                    lines = [line[1] for line in result]
                    file_name = os.path.basename(img_file)
                    extracted_text.append(f"--- Text from {file_name} ---\n" + "\n".join(lines))

        else:
            print(f"Invalid input path or unsupported file format: {input_path}")
            return False

        # Save output
        final_content = "\n\n".join(extracted_text) if extracted_text else "No readable text found."
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        print(f"OCR Complete! Text saved to: {output_path}")
        return True

    except Exception as e:
        print(f"OCR Error: {e}")
        return False


def image_to_excel(
    user_input: str, output_user: str, y_tolerance: int = 5
) -> bool:
    try:
        pages_results = []

        # 1. Properly check file extension
        if user_input.lower().endswith(".pdf"):
            pdf = PdfDocument(user_input)
            for page in pdf:
                pil_image = page.render(scale=200 / 72).to_pil()
                img_np = np.array(pil_image)
                res, _ = engine(img_np)
                if res:
                    pages_results.append(res)
        else:
            res, _ = engine(user_input)
            if res:
                pages_results.append(res)

        if not pages_results:
            print("Not found")
            return False

        # 2. Flatten page results into a uniform list of text boxes
        items = []
        for page_res in pages_results:
            for box, text, _ in page_res:
                if not text.strip():
                    continue
                y_center = sum(pt[1] for pt in box) / 4.0
                x_left = min(pt[0] for pt in box)
                items.append((x_left, y_center, text.strip()))

        if not items:
            print("No text items found")
            return False

        # 3. Sort top-to-bottom
        items.sort(key=lambda item: item[1])

        # 4. Cluster items into rows (Y-axis)
        rows_grouped = []
        for x, y, text in items:
            placed = False
            for row in rows_grouped:
                # Group if Y-coordinate is near the row's average Y position
                if abs(y - np.mean([item[1] for item in row])) <= y_tolerance:
                    row.append((x, y, text))
                    placed = True
                    break
            if not placed:
                rows_grouped.append([(x, y, text)])

        # 5. Extract global X column boundaries across all rows
        all_x = [x for row in rows_grouped for x, _, _ in row]
        all_x.sort()

        col_clusters = []
        x_tolerance = 15  # Adjust threshold based on column spacing

        for x in all_x:
            if not col_clusters or (x - col_clusters[-1][-1]) > x_tolerance:
                col_clusters.append([x])
            else:
                col_clusters[-1].append(x)

        if not col_clusters:
            print("Failed to cluster columns")
            return False

        # Calculate average X position for each column boundary
        col_centers = [sum(cluster) / len(cluster) for cluster in col_clusters]
        num_cols = len(col_centers)

        # Helper function to find the nearest column index
        def get_col_index(x_val):
            return min(
                range(num_cols), key=lambda i: abs(col_centers[i] - x_val)
            )

        # 6. Build structured 2D grid matrix
        final_grid = []
        for row in rows_grouped:
            grid_row = [""] * num_cols
            for x, y, text in row:
                col_idx = get_col_index(x)
                # Append text if multiple words land in the same cell
                grid_row[col_idx] = (grid_row[col_idx] + " " + text).strip()
            final_grid.append(grid_row)

        # 7. Export to Excel/CSV
        pd.DataFrame(final_grid).to_excel(output_user, index=False, header=False)
        print("Excel Created Successfully")
        return True

    except Exception as e:
        print(f"error {e}")
        return False