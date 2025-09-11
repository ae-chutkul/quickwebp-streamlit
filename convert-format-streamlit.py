import streamlit as st
from PIL import Image
import io
import zipfile
import time


# st.title("Multi-Image WebP Converter")

st.set_page_config(page_title="QuickWebP", page_icon="🖼️")
st.markdown("## 🖼️ QuickWebP - Multiple Image Converter")


DEFAULT_QUALITY = 85

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


# --- Slider ---
quality = st.slider(
    "Compression Quality (20% to 95%)",
    min_value=20,
    max_value=95,
    value=DEFAULT_QUALITY
)
st.write(f"Selected Quality: {quality}%")


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
                total_original_size += orig_size

                # Convert image
                img = Image.open(file).convert("RGB")
                img_bytes = io.BytesIO()
                img.save(img_bytes, "webp", quality=quality)

                webp_size = len(img_bytes.getvalue())
                total_webp_size += webp_size

                img_bytes.seek(0)
                new_name = file.name.rsplit(".", 1)[0] + ".webp"
                zip_file.writestr(new_name, img_bytes.read())

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
        st.success(f"✅ Converted {len(uploaded_files)} files ({total_webp_size/1024:.2f} KB) successfully in {elapsed:.2f} seconds")
                    
                   


# --- Download ---
if st.session_state.converted and st.session_state.zip_buffer:
    st.download_button(
        "📥 Download All as ZIP",
        st.session_state.zip_buffer,
        file_name="converted_images_webp.zip",
        mime="application/zip"
    )
