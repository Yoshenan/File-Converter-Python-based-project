import os
import tempfile
import pandas as pd
import streamlit as st

# Import your custom modules
from image import convert_image, text_to_qr, image_to_gif, image_to_text, image_to_excel
from video import convert_video, image_to_video, convert_audio, add_audio_to_image
from encoding import file_to_base, base_to_file
from data import convert_data, clean_data, file_smart
from document import convert_document, merge_pdfs

def main():
    st.set_page_config(page_title="Universal File Converter", page_icon="⚡", layout="centered")
    st.title("⚡ Universal File Converter")

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

    st.subheader("1. Input File(s) or Text")

    input_choice = st.radio("Select Input Type", ["Upload File(s)", "Text / URL"], horizontal=True)

    # -------------------------------------------------------------
    # OPTION A: TEXT / URL (QR CODE GENERATION)
    # -------------------------------------------------------------
    if input_choice == "Text / URL":
        user_input = st.text_area("Enter Text or URL to Encode")
        user_preference = st.selectbox("Target Format:", [".png", ".jpg", ".jpeg"])

        if user_input and st.button("Generate QR Code"):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_user = os.path.join(tmpdir, f"qrcode{user_preference}")
                text_to_qr(user_input, output_user)

                with open(output_user, "rb") as f:
                    st.image(output_user, caption="Generated QR Code", width=200)
                    st.download_button(
                        label=f"📥 Download qrcode{user_preference}",
                        data=f.read(),
                        file_name=f"qrcode{user_preference}",
                        mime=f"image/{user_preference.replace('.', '')}"
                    )

    # -------------------------------------------------------------
    # OPTION B: FILE UPLOADER (SINGLE FILE OR MULTI-PDF MERGE)
    # -------------------------------------------------------------
    else:
        uploaded_files = st.file_uploader("Drop File(s) or browse", accept_multiple_files=True)

        if uploaded_files:
            # MULTI-FILE MERGE (PDFs)
            if len(uploaded_files) > 1:
                all_pdfs = all(f.name.lower().endswith(".pdf") for f in uploaded_files)
                if all_pdfs:
                    st.info(f"Detected **{len(uploaded_files)} PDF Files** for merging")
                    target_ext = st.text_input("Enter Target Format", value=".pdf").strip().lower()
                    if target_ext and not target_ext.startswith("."):
                        target_ext = "." + target_ext

                    if st.button("Merge PDFs"):
                        if target_ext == ".pdf":
                            with tempfile.TemporaryDirectory() as tmpdir:
                                pdf_paths = []
                                for idx, uploaded_file in enumerate(uploaded_files):
                                    path = os.path.join(tmpdir, f"input_{idx}.pdf")
                                    with open(path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                                    pdf_paths.append(path)

                                output_path = os.path.join(tmpdir, "merged_output.pdf")
                                merge_pdfs(pdf_paths, output_path)

                                with open(output_path, "rb") as f:
                                    st.success("PDFs merged successfully!")
                                    st.download_button(
                                        label="📥 Download Merged PDF",
                                        data=f.read(),
                                        file_name="merged_output.pdf",
                                        mime="application/pdf"
                                    )
                        else:
                            st.error(f"Cannot Merge into {target_ext}")
                else:
                    st.warning("Multi-file batch processing currently supports merging **PDF files only**.")

            # SINGLE FILE CONVERSION
            elif len(uploaded_files) == 1:
                uploaded_file = uploaded_files[0]
                file_name = uploaded_file.name
                file_root, original = os.path.splitext(file_name)
                src_ext = original.lower()
                
                user_preference = st.text_input(f"Detected {original}. Enter target format:").strip().lower()
                if user_preference and not user_preference.startswith('.'):
                    user_preference = '.' + user_preference

                audio_file_for_video = None
                if src_ext in image_exts and user_preference in video_exts:
                    if st.checkbox("Add audio soundtrack?"):
                        audio_file_for_video = st.file_uploader("Upload Audio File", type=["mp3", "wav", "aac", "flac", "ogg"])

                if user_preference and st.button("Convert File"):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        user_input_path = os.path.join(tmpdir, file_name)
                        with open(user_input_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        output_path = os.path.join(tmpdir, f"{file_root}{user_preference}")
                        success = True

                        try:
                            if src_ext in ocr_supported_exts and user_preference == ".txt":
                                image_to_text(user_input_path, output_path)
                            elif src_ext and user_preference == ".csv":
                                df_raw = pd.read_csv(user_input_path)
                                df_clean = clean_data(df_raw)
                                df_clean.to_csv(output_path, index=False)
                            elif src_ext in image_exts and user_preference == ".gif":
                                image_to_gif(user_input_path, output_path)
                            elif (src_ext in image_exts or src_ext == ".pdf") and user_preference in [".xlsx", ".xls"]:
                                image_to_excel(user_input_path, output_path)
                            elif src_ext in image_exts and user_preference in image_exts:
                                convert_image(user_input_path, output_path)
                            elif src_ext in data_exts and user_preference in data_exts:
                                convert_data(user_input_path, output_path)
                            elif src_ext in document_exts and user_preference in image_exts:
                                convert_document(user_input_path, output_path)
                            elif src_ext in video_exts and user_preference in video_exts:
                                convert_video(user_input_path, output_path)
                            elif user_preference in base_map:
                                base_num = base_map[user_preference]
                                file_to_base(user_input_path, output_path, base_type=base_num)
                            elif src_ext in base_map:
                                base_num = base_map[src_ext]
                                base_to_file(user_input_path, output_path, base_type=base_num)
                            elif src_ext in audio_exts and user_preference in audio_exts:
                                convert_audio(user_input_path, output_path)
                            elif src_ext in video_exts and user_preference in audio_exts:
                                convert_audio(user_input_path, output_path)
                            elif src_ext in image_exts and user_preference in video_exts:
                                if audio_file_for_video is not None:
                                    audio_path = os.path.join(tmpdir, audio_file_for_video.name)
                                    with open(audio_path, "wb") as f_aud:
                                        f_aud.write(audio_file_for_video.getbuffer())
                                    add_audio_to_image(user_input_path, audio_path, output_path)
                                else:
                                    image_to_video(user_input_path, output_path)
                            else:
                                st.error(f"Cannot convert {src_ext} to {user_preference}")
                                success = False

                            if success and os.path.exists(output_path):
                                with open(output_path, "rb") as f:
                                    st.success("Conversion Completed")
                                    st.download_button(
                                        label=f"📥 Download {file_root}{user_preference}",
                                        data=f.read(),
                                        file_name=f"{file_root}{user_preference}"
                                    )

                        except Exception as e:
                            st.error(f"Error during conversion: {e}")

if __name__ == "__main__":
    main()