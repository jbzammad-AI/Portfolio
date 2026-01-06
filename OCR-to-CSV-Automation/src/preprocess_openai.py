# src/preprocess.py

import re

# -------------------------------
# TEXT CLEANING
# -------------------------------
def clean_text(text):
    """
    Normalize OCR text.
    """
    text = text.replace('\r','\n')
    text = re.sub(r'\s+', ' ', text)  # collapse spaces
    return text.strip()

# -------------------------------
# GENERIC FALLBACK FUNCTIONS
# -------------------------------
def extract_generic_vendor(text):
    lines = text.strip().split('\n')
    for line in lines[:5]:
        letters_only = ''.join(c if c.isalpha() or c.isspace() else '' for c in line).strip()
        if letters_only:
            words = letters_only.split()
            return ' '.join(words[:5])
    return "Other"

def extract_generic_amount(text):
    numbers = re.findall(r'\d+[.,]\d+', text)
    float_numbers = []
    for n in numbers:
        try:
            num = float(n.replace(',', '.'))
            float_numbers.append(num)
        except:
            continue
    if not float_numbers:
        return 0.0
    totals = [num for num in float_numbers if num < 10000]
    return max(totals) if totals else max(float_numbers)

def extract_generic_date(text):
    match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b[A-Za-z]{3,9} \d{1,2} \d{4}\b', text)
    if match:
        return match.group(0)
    return ""

# -------------------------------
# STRUCTURED INVOICE EXTRACTION
# -------------------------------
def extract_invoice_fields(text):
    """
    Extract invoice-level fields.
    """
    data = {
        "Invoice Number": "",
        "Invoice Date": "",
        "Vendor": "",
        "Vendor Address": "",
        "Bill To": "",
        "Ship To": "",
        "Subtotal": "",
        "Shipping": "",
        "Total": "",
        "Balance Due": ""
    }

    lines = text.split('\n')

    # Vendor
    for line in lines:
        clean_line = line.strip()
        if clean_line and not re.search(r'invoice|bill|ship', clean_line, re.IGNORECASE):
            data["Vendor"] = clean_line
            break
    if not data["Vendor"]:
        data["Vendor"] = extract_generic_vendor(text)

    # Invoice Number
    match = re.search(r'(?:Invoice|INVOICE)[^\d]*(#|ID|No\.?)\s*([\w-]+)', text, re.IGNORECASE)
    if match:
        data["Invoice Number"] = match.group(2)

    # Invoice Date
    match = re.search(r'Date[: ]+\s*([A-Za-z0-9/ -]+)', text, re.IGNORECASE)
    if match:
        date_match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b[A-Za-z]{3,9} \d{1,2} \d{4}\b', match.group(1))
        if date_match:
            data["Invoice Date"] = date_match.group(0)
    else:
        data["Invoice Date"] = extract_generic_date(text)

    # Bill To
    match = re.search(r'Bill To[:\n]+\s*(.+)', text, re.IGNORECASE)
    if match:
        data["Bill To"] = match.group(1).strip()

    # Ship To
    match = re.search(r'Ship To[:\n]+\s*(.+)', text, re.IGNORECASE)
    if match:
        data["Ship To"] = match.group(1).strip()

    # Subtotal
    match = re.search(r'Subtotal[: ]+\$?\s*([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Subtotal"] = match.group(1).replace(',', '')

    # Shipping
    match = re.search(r'Shipping[: ]+\$?\s*([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Shipping"] = match.group(1).replace(',', '')

    # Total
    match = re.search(r'Total[: ]+\$?\s*([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Total"] = match.group(1).replace(',', '')
    else:
        data["Total"] = extract_generic_amount(text)

    # Balance Due
    match = re.search(r'Balance Due[: ]+\$?\s*([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Balance Due"] = match.group(1).replace(',', '')

    return data

# -------------------------------
# LINE ITEMS EXTRACTION
# -------------------------------
def extract_line_items(text):
    """
    Extract line items: Description, Quantity, Unit Price, Total
    """
    lines = text.split('\n')
    items = []

    for line in lines:
        # Basic pattern: Description ... Qty ... Price ... Total
        # Look for a line containing a number and price
        match = re.findall(r'([\w\s\-/!]+?)\s+(\d+[.,]?\d*)\s+.*?\$?(\d+[.,]?\d*)', line)
        if match:
            for m in match:
                desc, qty, price = m
                try:
                    qty = float(qty.replace(',', '.'))
                    price = float(price.replace(',', '.'))
                except:
                    continue
                items.append({
                    "Description": desc.strip(),
                    "Quantity": qty,
                    "Unit Price": price,
                    "Total": qty * price
                })
    return items

# -------------------------------
# CATEGORY EXTRACTION
# -------------------------------
def extract_category(vendor):
    vendor_lower = vendor.lower()
    if any(k in vendor_lower for k in ['walmart', 'aldi', 'lidl', 'supercenter']):
        return "Groceries"
    elif any(k in vendor_lower for k in ['amazon', 'ebay', 'shop']):
        return "Shopping"
    elif any(k in vendor_lower for k in ['uber', 'lyft', 'taxi']):
        return "Transport"
    else:
        return "Other"
