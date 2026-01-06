import streamlit as st
import os
from src.ocr_extractor import file_to_text
from src.preprocess import clean_text, extract_invoice_fields, extract_line_items, extract_category
import pandas as pd
from PIL import Image

# -----------------------
# Save summary CSV
# -----------------------
def save_invoice_summary(data_dict, original_filename, output_folder="data/processed"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    path = os.path.join(output_folder, f"{base_name}_summary.csv")
    df = pd.DataFrame([data_dict])
    df["Category"] = extract_category(data_dict.get("Vendor",""))
    df.to_csv(path, index=False)
    return path

# -----------------------
# Save line items CSV
# -----------------------
def save_line_items(items, original_filename, output_folder="data/processed"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    path = os.path.join(output_folder, f"{base_name}_items.csv")
    df = pd.DataFrame(items)
    df.to_csv(path, index=False)
    return path

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Invoice OCR → CSV", layout="wide")
st.title("Invoice & Receipt OCR Extractor with Line Items")

uploaded_files = st.file_uploader(
    "Upload PDFs / Images",
    type=["pdf","png","jpg","jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"File: {uploaded_file.name}")

        # Save temporarily
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Show image if applicable
        ext = uploaded_file.name.lower().split('.')[-1]
        if ext in ["png","jpg","jpeg"]:
            image = Image.open(file_path)
            st.image(image, caption="Uploaded Image", use_column_width=True)

        # OCR text
        raw_text = file_to_text(file_path)
        text_clean = clean_text(raw_text)
        st.text_area("OCR Extracted Text", text_clean, height=200)

        # Extract invoice summary
        summary_data = extract_invoice_fields(text_clean)
        st.subheader("Invoice Summary")
        st.dataframe(summary_data, use_container_width=True)

        # Extract line items
        line_items = extract_line_items(text_clean)
        if line_items:
            st.subheader("Line Items")
            st.dataframe(pd.DataFrame(line_items), use_container_width=True)
        else:
            st.info("No line items detected.")

        # Save CSVs
        summary_csv = save_invoice_summary(summary_data, uploaded_file.name)
        items_csv = save_line_items(line_items, uploaded_file.name)

        # Download buttons
        with open(summary_csv, "rb") as f:
            st.download_button(
                label=f"Download Summary CSV",
                data=f,
                file_name=os.path.basename(summary_csv),
                mime="text/csv"
            )
        with open(items_csv, "rb") as f:
            st.download_button(
                label=f"Download Line Items CSV",
                data=f,
                file_name=os.path.basename(items_csv),
                mime="text/csv"
            )

        # Cleanup temp file
        os.remove(file_path)
