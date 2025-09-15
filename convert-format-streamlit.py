import streamlit as st
from PIL import Image
import io
import zipfile
import time


# st.title("Multi-Image WebP Converter")

st.set_page_config(page_title="QuickWebP", page_icon="🖼️")
st.markdown("## 🖼️ QuickWebP - Multiple Image Converter")


DEFAULT_COMPRESSION_QUALITY = 85

# --- Session state ---
if "zip_buffer" not in st.session_state:
    st.session_state.zip_buffer = None
if "converted" not in st.session_state:
    st.session_state.converted = False

# --- File uploader ---
uploaded_files = st.file_uploader(
    "Choose images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)


# --- Show number of files uploaded ---
if uploaded_files:
    total_file_size = sum(file.size for file in uploaded_files)
    st.info(f"📂 {len(uploaded_files)} file(s) uploaded ({total_file_size / 1024:.2f} KB)")


# --- Radio Button for Quality ---
compression_quality = st.radio(
    "Choose Compression Quality",
    options=[50, 65, 75, 85, 95],   # you can adjust these
    index=3,  # default = 85
    format_func=lambda x: f"{x}%"  # show with % sign
)

# --- Convert Button ---
if st.button("🔄 Convert to WebP"):
    if not uploaded_files:
        st.warning("⚠️ Upload at least one image before converting.")
    else:
        zip_buffer = io.BytesIO()
        progress_bar = st.progress(0)
        status_text = st.empty()

        start_time = time.time()

        total_original_size = 0
        total_webp_size = 0

        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, file in enumerate(uploaded_files):
                # Original size
                orig_size = file.size
                # print(f"orig_size: {orig_size / 1024:.2f} KB")

                total_original_size += orig_size

                # Convert image
                img = Image.open(file).convert("RGB")

                # Create individual memeroy buffer and save image into buffer.
                img_bytes = io.BytesIO()
                # print(f"imag_bytes: ", img_bytes)
                img.save(img_bytes, "webp", quality=compression_quality)

                # New file size in WEBP format (.getvalue() to access the value in memory buffer address)
                webp_size = len(img_bytes.getvalue())
                # Total File Size in WEBP Format
                total_webp_size += webp_size

                # Move the cursur to the beginning
                img_bytes.seek(0)

                new_filename_webp = file.name.rsplit(".", 1)[0] + ".webp"
                zip_file.writestr(new_filename_webp, img_bytes.read())  # img_bytes.read() means read the entire content

                # Update progress
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)

                status_text.text(f"Converting {file.name} ({i+1}/{len(uploaded_files)}) from {orig_size / 1024:.2f} KB to {webp_size / 1024:.2f} KB")
                    

        zip_buffer.seek(0)
        st.session_state.zip_buffer = zip_buffer
        st.session_state.converted = True
        progress_bar.empty()
        status_text.text("")
        elapsed = time.time() - start_time
        if elapsed > 60:
            elapsed_minutes = elapsed // 60
            elapsed_seconds = elapsed % 60
            st.success(f"✅ Converted {len(uploaded_files)} files ({total_webp_size / 1024:.2f} KB) successfully in {elapsed_minutes} minutes {elapsed_seconds} seconds")
        else:
            st.success(f"✅ Converted {len(uploaded_files)} files ({total_webp_size / 1024:.2f} KB) successfully in {elapsed:.2f} seconds")

        
                    
                
# --- Download ---
if st.session_state.converted and st.session_state.zip_buffer:
    st.download_button(
        "📥 Download All as ZIP",
        st.session_state.zip_buffer,
        file_name="converted_images_webp.zip",
        mime="application/zip"
    )
