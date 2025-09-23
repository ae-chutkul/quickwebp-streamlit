import streamlit as st
from PIL import Image
import io
import zipfile
import time

# --- Credentials ---
USERNAME = "admin"
PASSWORD = ""


print(st.session_state)

# --- Initialize login state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    print(st.session_state)

    st.set_page_config(page_title="QuickWebP", page_icon="🚀")
    st.title(" Welcome to QuickWebP 🚀 ")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# Clear session state variables
def clear_all(): 
    keys_to_clear = ["zip_buffer", "converted", "converted_files", "success_message", "uploaded_files"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    print("clear_all: ", st.session_state)


def quickWebP():
    st.set_page_config(page_title="QuickWebP", page_icon="🚀")
    st.markdown("## 🚀 QuickWebP - Multiple Image Converter")

    # --- Initialize Session state in QuickWebP ---
    if "zip_buffer" not in st.session_state:
        st.session_state.zip_buffer = None
    if "converted" not in st.session_state:
        st.session_state.converted = False
    if "converted_files" not in st.session_state:
        st.session_state.converted_files = []   # store individual files
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    print("QuickWebP Session: ", st.session_state)

    # --- File uploader ---
    uploaded_files = st.file_uploader(
        "Choose images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,  
        key="uploader" 
    )
    
    print("Uploaded State: ", st.session_state)
    for file in uploaded_files:
        st.session_state.uploaded_files.append(file)
    
    print("\n\nst.session_state.uploaded_files: ", st.session_state.uploaded_files)

    # --- Show number of files uploaded ---
    if uploaded_files:
        total_file_size = sum(file.size for file in uploaded_files)
        total_files_count = len(uploaded_files)
        
        st.info(f"📂 {total_files_count} file(s) uploaded ({total_file_size / 1024:,.2f} KB)")


    # --- Radio Button for Quality ---
    compression_quality = st.radio(
        "Choose Lossy Compression",
        options=[50, 65, 75, 85, 95],  
        index=3,
        format_func=lambda x: f"{x}%"  # show with % sign
    )

    # --- Convert Button ---
    if st.button("🔄 Convert to WebP"):
        if not uploaded_files:
            st.error("⚠️ Upload at least one image before converting.")
        else:
            zip_buffer = io.BytesIO()
            progress_bar = st.progress(0)
            status_text = st.empty()

            start_time = time.time()

            total_original_size = 0
            total_webp_size = 0
            converted_files = []

            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for i, file in enumerate(uploaded_files):
                    # Original size
                    orig_size = file.size
                    # print(f"orig_size: {orig_size / 1024:.2f} KB")

                    total_original_size += orig_size

                    # Convert image
                    img = Image.open(file)
                    if file.type == "image/png":
                        img = img.convert("RGBA")    # Preserve transparency if PNG
                    else:
                        img = img.convert("RGB")

                    # Create individual memeroy buffer and save image into buffer.
                    img_bytes = io.BytesIO()
                    # print(f"imag_bytes: ", img_bytes)
                    img.save(img_bytes, "webp", quality=compression_quality, lossess=True)

                    # New file size in WEBP format (.getvalue() to access the value in memory buffer address)
                    webp_size = len(img_bytes.getvalue())
                    # Total File Size in WEBP Format
                    total_webp_size += webp_size

                    # Move the cursur to the beginning
                    img_bytes.seek(0)

                    new_filename_webp = file.name.rsplit(".", 1)[0] + ".webp"
                    zip_file.writestr(new_filename_webp, img_bytes.read())  # img_bytes.read() means read the entire content

                    converted_files.append((new_filename_webp, img_bytes.getvalue()))

                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)

                    status_text.text(f"Converting {file.name} ({i+1}/{len(uploaded_files)}) from {orig_size / 1024:.2f} KB to {webp_size / 1024:.2f} KB")
                        

            zip_buffer.seek(0)
            st.session_state.zip_buffer = zip_buffer
            st.session_state.converted = True
            st.session_state.converted_files = converted_files
            

            progress_bar.empty()
            status_text.text("")

            elapsed = time.time() - start_time
            elapsed_minutes = elapsed // 60
            elapsed_seconds = elapsed % 60

            if elapsed >= 120:
                st.session_state["success_message"] = f"✅ Converted {len(uploaded_files)} files ({total_webp_size / 1024:,.2f} KB) successfully in {int(elapsed_minutes)} minutes {elapsed_seconds:.2f} seconds"
            elif elapsed > 60:
                st.session_state["success_message"] = f"✅ Converted {len(uploaded_files)} files ({total_webp_size / 1024:,.2f} KB) successfully in {int(elapsed_minutes)} minute {elapsed_seconds:.2f} seconds"
            else:
                st.session_state["success_message"] = f"✅ Converted {len(uploaded_files)} files ({total_webp_size / 1024:,.2f} KB) successfully in {elapsed:.2f} seconds"
    

    # --- Download ---
    if st.session_state.converted and "success_message" in st.session_state:
        st.success(st.session_state["success_message"])

        if len(st.session_state.converted_files) <= 10:
            
            st.download_button(
                "📦 Download as ZIP",
                st.session_state.zip_buffer,
                file_name="converted_images_webp.zip",
                mime="application/zip"
            )

            with st.container():
                st.markdown("<div>", unsafe_allow_html=True)

                for fname, fbytes in st.session_state.converted_files:
                    file_size_kb = len(fbytes) / 1024

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**{fname}** ({file_size_kb:.2f} KB)")
                    with col2: 
                        st.download_button(
                        label=f"Download",
                        data=fbytes,
                        file_name=fname,
                        mime="image/webp",
                        key=f"dl_{fname}"  # unique key for each
                        )

                st.markdown("</div>", unsafe_allow_html=True) 

        else:
            st.download_button(
                "📦 Download All as ZIP",
                st.session_state.zip_buffer,
                file_name="converted_images_webp.zip",
                mime="application/zip"
            )
            
    st.write("-----------------------------------------------------")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.logged_in = False
        clear_all()
        st.rerun()
    

# --- Router ---
if not st.session_state.logged_in:
    login()
else:
    quickWebP()
