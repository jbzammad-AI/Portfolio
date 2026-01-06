import streamlit as st
import os
from src.ocr_extractor import file_to_text
from src.preprocess import clean_text, extract_invoice_data, extract_category
import pandas as pd
from PIL import Image

# -----------------------
# Function to save CSV
# -----------------------
def save_csv_individual(data_dict, original_filename, output_folder="data/processed"):
    """
    Save extracted invoice data to CSV file.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    output_path = os.path.join(output_folder, f"{base_name}.csv")
    
    # Create DataFrame from dictionary
    df = pd.DataFrame([data_dict])
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    return output_path

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Invoice OCR → CSV", layout="wide")
st.title("📄 Invoice & Receipt OCR Extractor")

st.markdown("""
Upload your invoices or receipts (PDF or images) and the system will automatically:
- Extract text using OCR
- Identify invoice type (Receipt or Formal Invoice)
- Extract all relevant fields (date, vendor, amounts, items, etc.)
- Export to CSV format
""")

uploaded_files = st.file_uploader(
    "Upload PDFs / Images",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    # Create a container for progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, uploaded_file in enumerate(uploaded_files):
        # Update progress
        progress = (idx + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        st.divider()
        st.subheader(f"📝 File: {uploaded_file.name}")
        
        # Create columns for layout
        col1, col2 = st.columns([1, 1])
        
        # Save temporarily
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Show image if applicable
        ext = uploaded_file.name.lower().split('.')[-1]
        if ext in ["png", "jpg", "jpeg"]:
            with col1:
                st.markdown("**Original Image:**")
                image = Image.open(file_path)
                st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # OCR text extraction (use appropriate column based on file type)
        if ext in ["png", "jpg", "jpeg"]:
            with col2:
                with st.spinner("Extracting text with OCR..."):
                    raw_text = file_to_text(file_path)
                    text_clean = clean_text(raw_text)
                
                st.markdown("**Extracted Text:**")
                with st.expander("View OCR Text", expanded=False):
                    st.text_area("OCR Output", text_clean, height=200, key=f"ocr_{idx}")
        else:
            # For PDFs, show in full width
            with st.spinner("Extracting text with OCR..."):
                raw_text = file_to_text(file_path)
                text_clean = clean_text(raw_text)
            
            st.markdown("**Extracted Text:**")
            with st.expander("View OCR Text", expanded=False):
                st.text_area("OCR Output", text_clean, height=200, key=f"ocr_{idx}")
        
        # Extract invoice fields
        with st.spinner("Analyzing invoice structure..."):
            invoice_data = extract_invoice_data(text_clean)
        
        # Display extracted data
        st.subheader("📊 Extracted Invoice Data")
        
        # Show invoice type badge
        invoice_type = invoice_data.get('Invoice_Type', 'unknown')
        if invoice_type == 'receipt':
            st.markdown("🧾 **Type:** Retail Receipt")
        else:
            st.markdown("📋 **Type:** Formal Invoice")
        
        # Create a more readable display
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("**Basic Information:**")
            basic_info = {
                'Invoice Number': invoice_data.get('Invoice_Number', 'N/A'),
                'Date': invoice_data.get('Date', 'N/A'),
                'Vendor': invoice_data.get('Vendor', 'N/A'),
                'Category': invoice_data.get('Category', 'N/A'),
            }
            st.json(basic_info)
        
        with col_right:
            st.markdown("**Financial Summary:**")
            financial_info = {
                'Total Amount': f"${invoice_data.get('Amount', 0):.2f}",
                'Subtotal': f"${invoice_data.get('Subtotal', 0):.2f}",
                'Tax/VAT': f"${max(invoice_data.get('Tax', 0), invoice_data.get('VAT', 0)):.2f}",
                'Discount': f"${invoice_data.get('Discount', 0):.2f}",
            }
            st.json(financial_info)
        
        # Show items if available
        items = invoice_data.get('Items', '')
        if items:
            st.markdown("**Items:**")
            items_list = items.split('; ')
            for item in items_list[:5]:  # Show first 5 items
                st.markdown(f"- {item}")
            if len(items_list) > 5:
                st.markdown(f"*... and {len(items_list) - 5} more items*")
        
        # Show full data in expandable section
        with st.expander("View All Extracted Fields", expanded=False):
            # Convert to DataFrame for better display
            df_display = pd.DataFrame([invoice_data]).T
            df_display.columns = ['Value']
            df_display.index.name = 'Field'
            # Replace empty values with 'N/A' for better readability
            df_display['Value'] = df_display['Value'].apply(lambda x: 'N/A' if x == '' or x == 0.0 else x)
            st.dataframe(df_display, use_container_width=True)
        
        # Save CSV
        try:
            csv_path = save_csv_individual(invoice_data, uploaded_file.name)
            
            # Download button
            with open(csv_path, "rb") as f:
                st.download_button(
                    label=f"📥 Download CSV for {uploaded_file.name}",
                    data=f,
                    file_name=os.path.basename(csv_path),
                    mime="text/csv",
                    key=f"download_{idx}"
                )
            
            st.success(f"✅ Successfully processed and saved to: {csv_path}")
        except Exception as e:
            st.error(f"❌ Error saving CSV: {str(e)}")
        
        # Cleanup temp file
        try:
            os.remove(file_path)
        except:
            pass
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"🎉 All {len(uploaded_files)} file(s) processed successfully!")
    
    # Option to download all CSVs as a combined file
    if len(uploaded_files) > 1:
        st.divider()
        st.subheader("📦 Combined Export")
        
        if st.button("Generate Combined CSV"):
            # Combine all CSVs
            all_data = []
            for uploaded_file in uploaded_files:
                base_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
                csv_path = os.path.join("data/processed", f"{base_name}.csv")
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    df['Source_File'] = uploaded_file.name
                    all_data.append(df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                combined_csv_path = "data/processed/combined_invoices.csv"
                combined_df.to_csv(combined_csv_path, index=False)
                
                with open(combined_csv_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Combined CSV",
                        data=f,
                        file_name="combined_invoices.csv",
                        mime="text/csv"
                    )
                
                st.dataframe(combined_df, use_container_width=True)

else:
    st.info("👆 Please upload one or more invoice files to begin processing.")
    
    # Show example
    with st.expander("ℹ️ What types of invoices are supported?"):
        st.markdown("""
        This system supports:
        
        1. **Retail Receipts** (e.g., Walmart, grocery stores)
           - Store name, date, items purchased
           - Subtotal, tax, discounts, total
           - Payment method
        
        2. **Formal Business Invoices** (B2B)
           - Invoice number, date
           - Seller and client information
           - Line items with quantities and prices
           - Net worth, VAT, gross worth
           - Tax IDs, IBAN
        
        3. **Simple Invoices**
           - Bill to / Ship to addresses
           - Items and amounts
           - Order IDs
        
        The system automatically detects the invoice type and extracts relevant fields!
        """)