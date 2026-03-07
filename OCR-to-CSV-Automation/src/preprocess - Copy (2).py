# src/preprocess.py

import re

# -------------------------------
# TEXT CLEANING
# -------------------------------
def clean_text(text):
    """
    Normalize OCR text.
    """
    text = text.replace('\r','\n')  # normalize line breaks
    text = re.sub(r'\s+', ' ', text)  # replace multiple spaces with single
    return text.strip()


# -------------------------------
# GENERIC EXTRACTION FUNCTIONS
# -------------------------------
def extract_generic_vendor(text):
    """
    Generic fallback for receipts: first meaningful line, first 2-5 words.
    """
    lines = text.strip().split('\n')
    for line in lines[:5]:
        letters_only = ''.join(c if c.isalpha() or c.isspace() else '' for c in line).strip()
        if letters_only:
            words = letters_only.split()
            return ' '.join(words[:5])
    return "Other"


def extract_generic_amount(text):
    """
    Generic fallback: largest number under 10000
    """
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
    """
    Generic date extraction
    """
    match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{2,4}\b', text)
    if match:
        return match.group(0)
    return ""


# -------------------------------
# STRUCTURED INVOICE EXTRACTION
# -------------------------------
def extract_invoice_fields(text):
    """
    Extract structured invoice fields if present.
    Fallbacks to generic extraction when fields not found.
    """
    # Initialize all fields
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

    # Vendor (structured)
    for line in lines:
        if 'invoice' not in line.lower() and 'bill' not in line.lower() and 'ship' not in line.lower():
            data["Vendor"] = line.strip()
            break
    if not data["Vendor"]:
        data["Vendor"] = extract_generic_vendor(text)

    # Invoice Number
    match = re.search(r'(?:Invoice|INVOICE)[^\d]*(#|ID|No\.?)\s*([\w-]+)', text, re.IGNORECASE)
    if match:
        data["Invoice Number"] = match.group(2)

    # Invoice Date
    match = re.search(r'(?:Date[: ]+|Date of issue[: ]+)([\w\s/-]+)', text, re.IGNORECASE)
    if match:
        data["Invoice Date"] = match.group(1).strip()
    else:
        data["Invoice Date"] = extract_generic_date(text)

    # Bill To
    match = re.search(r'Bill To[:\n]+([\w\s,]+)', text, re.IGNORECASE)
    if match:
        data["Bill To"] = match.group(1).strip()

    # Ship To
    match = re.search(r'Ship To[:\n]+([\w\s,]+)', text, re.IGNORECASE)
    if match:
        data["Ship To"] = match.group(1).strip()

    # Subtotal
    match = re.search(r'Subtotal[: ]+\$?([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Subtotal"] = match.group(1).replace(',', '')

    # Shipping
    match = re.search(r'Shipping[: ]+\$?([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Shipping"] = match.group(1).replace(',', '')

    # Total
    match = re.search(r'Total[: ]+\$?([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Total"] = match.group(1).replace(',', '')
    else:
        # fallback generic amount
        data["Total"] = extract_generic_amount(text)

    # Balance Due
    match = re.search(r'Balance Due[: ]+\$?([\d.,]+)', text, re.IGNORECASE)
    if match:
        data["Balance Due"] = match.group(1).replace(',', '')

    return data


# -------------------------------
# CATEGORY EXTRACTION
# -------------------------------
def extract_category(vendor):
    """
    Simple keyword-based category assignment. Extendable to ML.
    """
    vendor_lower = vendor.lower()
    if any(k in vendor_lower for k in ['walmart', 'aldi', 'lidl', 'supercenter']):
        return "Groceries"
    elif any(k in vendor_lower for k in ['amazon', 'ebay', 'shop']):
        return "Shopping"
    elif any(k in vendor_lower for k in ['uber', 'lyft', 'taxi']):
        return "Transport"
    else:
        return "Other"
