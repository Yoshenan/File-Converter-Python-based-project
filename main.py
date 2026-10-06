import os
from image import convert_image, text_to_qr, image_to_gif, image_to_text,image_to_excel
from video import convert_video, image_to_video, convert_audio, add_audio_to_image
from encoding import file_to_base, base_to_file
from data import convert_data,clean_data
from document import convert_document, merge_pdfs
import pandas as pd
def main():
    user_input = input("Enter File, comma-separated PDFs, or Text: ").strip().strip('"').strip("'")

    if not user_input:
        print("Input cannot be empty")
        return

    # 0. SIMPLE HANDLER: Multi-file PDF Merging
    if "," in user_input:
        pdf_list = [f.strip().strip('"').strip("'") for f in user_input.split(",")]
        user_preference = input("Multiple files detected. Enter target format (e.g. .pdf): ").strip().lower()
        
        if not user_preference.startswith("."):
            user_preference = "." + user_preference

        if user_preference == ".pdf":
            output_user = "merged_output.pdf"
            merge_pdfs(pdf_list, output_user)
        else:
            print(f"Cannot merge multiple files into {user_preference}")
        return

    # 1. Handle QR Code generation if input is NOT a file on disk
    if not os.path.exists(user_input):
        user_preference = input("Path not found on disk. Is this text for a QR code? Enter target format (e.g. .png): ").strip().lower()
        if not user_preference.startswith("."):
            user_preference = "." + user_preference

        if user_preference in [".png", ".jpg", ".jpeg"]:
            output_user = "qrcode" + user_preference
            text_to_qr(user_input, output_user)
        else:
            print(f"File does not exist: {user_input}")
        return

    # 2. Standard File Conversions setup
    file_root, original = os.path.splitext(user_input)
    user_preference = input(f"Detected {original}. Enter target format: ").strip().lower()

    if not user_preference.startswith("."):
        user_preference = "." + user_preference

    output_user = file_root + user_preference

    # Extension categories
    ocr_supported_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".pdf"}
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
    audio_exts = {".mp3", ".wav", ".aac", ".flac", ".ogg"}
    base_map = {".b16": 16, ".b32": 32, ".b64": 64, ".b85": 85}
    data_exts = {
        ".csv", ".json", ".parquet", ".pq", 
        ".yaml", ".yml", ".db", ".sqlite", ".sql", 
        ".xls", ".xlsx", ".odf", ".odt", ".ods", ".xlsm", ".xlsb", 
        ".html"
    }
    document_exts = {".pdf", ".svg", ".md", ".markdown"}
    src_ext = original.lower()

    # 3. Routing logic
    # OCR Extraction (Image or PDF -> .txt)
    if src_ext in ocr_supported_exts and user_preference == ".txt":
        image_to_text(user_input, output_user)
    elif src_ext and user_preference == ".csv":
        df_raw = pd.read_csv(user_input)
        df_clean = clean_data(df_raw)
        df_clean.to_csv(output_user,index=False)

    # Image -> GIF
    elif src_ext in image_exts and user_preference == ".gif":
        image_to_gif(user_input, output_user)

    # Route both Images and PDFs to Excel
    elif (src_ext in image_exts or src_ext == ".pdf") and user_preference in [".xlsx", ".xls"]:
        image_to_excel(user_input, output_user)
    
    # Standard Image Conversions
    elif src_ext in image_exts and user_preference in image_exts:
        convert_image(user_input, output_user)

    # Data Conversions
    elif src_ext in data_exts and user_preference in data_exts:
        convert_data(user_input, output_user)

    # Document Conversions
    elif src_ext in document_exts and user_preference in image_exts:
        convert_document(user_input, output_user)

    # Video Conversions
    elif src_ext in video_exts and user_preference in video_exts:
        convert_video(user_input, output_user)

    # Encoding to Base string file
    elif user_preference in base_map:
        base_num = base_map[user_preference]
        file_to_base(user_input, output_user, base_type=base_num)

    # Decoding Base string file to binary file
    elif src_ext in base_map:
        base_num = base_map[src_ext]
        base_to_file(user_input, output_user, base_type=base_num)

    # Audio Conversions
    elif src_ext in audio_exts and user_preference in audio_exts:
        convert_audio(user_input, output_user)

    # Video Audio-Extraction
    elif src_ext in video_exts and user_preference in audio_exts:
        convert_audio(user_input, output_user)

    # Image to Video Conversion
    elif src_ext in image_exts and user_preference in video_exts:
        add_music = input("Add audio? (y/n): ").strip().lower()
        if add_music == "y":
            audio_path = input("Enter audio file path: ").strip().strip('"').strip("'")
            if os.path.exists(audio_path):
                add_audio_to_image(user_input, audio_path, output_user)
            else:
                print("Audio file does not exist")
        else:
            image_to_video(user_input, output_user)

    else:
        print(f"Cannot convert {src_ext} to {user_preference}")

if __name__ == "__main__":
    main()