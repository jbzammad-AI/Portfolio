# src/preprocess.py
import re
from datetime import datetime

# -------------------------------
# TEXT CLEANING
# -------------------------------
def clean_text(text):
    """
    Normalize OCR text while preserving structure.
    """
    text = text.replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

# -------------------------------
# INVOICE TYPE DETECTION
# -------------------------------
def detect_invoice_type(text):
    """
    Detect if this is a retail receipt or formal invoice.
    Returns: 'receipt' or 'invoice'
    """
    text_lower = text.lower()
    
    receipt_indicators = ['supercenter', 'items sold', 'cash tend', 'change due', 
                          'thank you for shopping', 'store #', 'st#', 'op#']
    
    invoice_indicators = ['invoice no', 'seller:', 'client:', 'bill to:', 
                         'ship to:', 'tax id:', 'iban:', 'vat [%]', 'gross worth']
    
    receipt_score = sum(1 for indicator in receipt_indicators if indicator in text_lower)
    invoice_score = sum(1 for indicator in invoice_indicators if indicator in text_lower)
    
    return 'receipt' if receipt_score > invoice_score else 'invoice'

# -------------------------------
# DATE EXTRACTION
# -------------------------------
def extract_date(text):
    """
    Extract date in various formats and normalize to YYYY-MM-DD.
    """
    patterns = [
        (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})[,\s]+(\d{4})\b', 'text_month'),
        (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', 'mdy'),
        (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2})\b', 'short'),
        (r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b', 'ymd'),
        (r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\s+\d{1,2}:\d{2}', 'timestamp'),
    ]
    
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    for pattern, date_type in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if date_type == 'text_month':
                    month_str, day, year = match
                    month = month_map.get(month_str.lower()[:3])
                    if month:
                        date_obj = datetime(int(year), month, int(day))
                        return date_obj.strftime('%Y-%m-%d')
                        
                elif date_type == 'ymd':
                    year, month, day = match
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
                    
                elif date_type == 'mdy' or date_type == 'timestamp':
                    month, day, year = match[:3] if date_type == 'timestamp' else match
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
                    
                elif date_type == 'short':
                    month, day, year = match
                    year = int(year)
                    year = 2000 + year if year < 50 else 1900 + year
                    date_obj = datetime(year, int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
            except:
                continue
    
    return ""

# -------------------------------
# INVOICE NUMBER EXTRACTION
# -------------------------------
def extract_invoice_number(text):
    """
    Extract invoice number from various formats.
    """
    patterns = [
        r'invoice\s+no[:\s]+(\S+)',
        r'invoice\s*#[:\s]*(\S+)',
        r'order\s+id[:\s]+(\S+)',
        r'tc#\s*(\d+)',
        r'#\s*(\d{5,})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""

# -------------------------------
# VENDOR/COMPANY EXTRACTION
# -------------------------------
def extract_vendor(text, invoice_type='invoice'):
    """
    Extract vendor/company name based on invoice type.
    """
    lines = text.strip().split('\n')
    
    if invoice_type == 'invoice':
        seller_match = re.search(r'seller[:\s]+(.*?)(?:\n.*?Tax Id|Client:|$)', text, re.IGNORECASE | re.DOTALL)
        if seller_match:
            seller_text = seller_match.group(1)
            first_line = seller_text.split('\n')[0].strip()
            return first_line if first_line else "Unknown Vendor"
    
    for i, line in enumerate(lines[:10]):
        line_clean = line.strip()
        
        if not line_clean or line_clean.upper() in ['INVOICE', 'RECEIPT', 'BILL']:
            continue
        
        if re.match(r'^[#\d\s-]+$', line_clean):
            continue
        
        if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', line_clean):
            continue
        
        vendor = re.sub(r'^[^a-zA-Z]+', '', line_clean)
        vendor = re.split(r'\s{2,}|\t', vendor)[0]
        vendor = re.sub(r'[^a-zA-Z\s&\'-★].*$', '', vendor).strip()
        
        if vendor and len(vendor) >= 3:
            words = vendor.split()
            if len(words) > 6:
                vendor = ' '.join(words[:6])
            return vendor
    
    return "Unknown Vendor"

# -------------------------------
# SELLER/CLIENT EXTRACTION
# -------------------------------
def extract_seller_info(text):
    """
    Extract complete seller information.
    """
    seller_match = re.search(r'seller[:\s]+(.*?)(?=Client:|ITEMS|$)', text, re.IGNORECASE | re.DOTALL)
    if not seller_match:
        return {}
    
    seller_text = seller_match.group(1)
    lines = [l.strip() for l in seller_text.split('\n') if l.strip()]
    
    info = {
        'name': lines[0] if lines else '',
        'address': '',
        'tax_id': '',
        'iban': ''
    }
    
    address_lines = []
    for line in lines[1:4]:
        if 'tax id' in line.lower() or 'iban' in line.lower():
            break
        address_lines.append(line)
    info['address'] = ', '.join(address_lines)
    
    tax_match = re.search(r'tax\s+id[:\s]+(\S+)', seller_text, re.IGNORECASE)
    if tax_match:
        info['tax_id'] = tax_match.group(1)
    
    iban_match = re.search(r'iban[:\s]+(\S+)', seller_text, re.IGNORECASE)
    if iban_match:
        info['iban'] = iban_match.group(1)
    
    return info

def extract_client_info(text):
    """
    Extract complete client information.
    """
    client_match = re.search(r'client[:\s]+(.*?)(?=ITEMS|$)', text, re.IGNORECASE | re.DOTALL)
    if not client_match:
        return {}
    
    client_text = client_match.group(1)
    lines = [l.strip() for l in client_text.split('\n') if l.strip()]
    
    info = {
        'name': lines[0] if lines else '',
        'address': '',
        'tax_id': ''
    }
    
    address_lines = []
    for line in lines[1:]:
        if 'tax id' in line.lower():
            break
        address_lines.append(line)
    info['address'] = ', '.join(address_lines)
    
    tax_match = re.search(r'tax\s+id[:\s]+(\S+)', client_text, re.IGNORECASE)
    if tax_match:
        info['tax_id'] = tax_match.group(1)
    
    return info

# -------------------------------
# ADDRESS EXTRACTION
# -------------------------------
def extract_address(text, address_type='bill'):
    """
    Extract billing or shipping address.
    """
    if address_type.lower() == 'bill':
        pattern = r'bill\s+to[:\s]+(.*?)(?=ship\s+to|ship\s+mode|date|item|notes|$)'
    else:
        pattern = r'ship\s+to[:\s]+(.*?)(?=ship\s+mode|date|item|notes|balance|$)'
    
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        address = match.group(1).strip()
        address = re.sub(r'\s+', ' ', address)
        if len(address) > 200:
            address = address[:200]
        return address.strip()
    
    return ""

# -------------------------------
# AMOUNT EXTRACTION
# -------------------------------
def extract_amounts(text, invoice_type='invoice'):
    """
    Extract financial amounts based on invoice type.
    """
    amounts = {
        'subtotal': 0.0,
        'discount': 0.0,
        'shipping': 0.0,
        'tax': 0.0,
        'vat': 0.0,
        'total': 0.0,
        'net_worth': 0.0,
        'gross_worth': 0.0,
        'amount': 0.0
    }
    
    if invoice_type == 'invoice':
        patterns = {
            'net_worth': r'net\s+worth[:\s]+\$?\s*([\d\s,]+\.?\d*)',
            'vat': r'vat[:\s]+\$?\s*([\d\s,]+\.?\d*)',
            'gross_worth': r'gross\s+worth[:\s]+\$?\s*([\d\s,]+\.?\d*)',
        }
    else:
        patterns = {
            'subtotal': r'subtotal[:\s]+\$?\s*([\d,]+\.?\d*)',
            'discount': r'discount[:\s\(]*\d*%?\)?[:\s]+\$?\s*([\d,]+\.?\d*)',
            'tax': r'tax[:\s]+\$?\s*([\d,]+\.?\d*)',
        }
    
    common_patterns = {
        'total': r'total[:\s]+\$?\s*([\d\s,]+\.?\d*)',
        'balance_due': r'balance\s+due[:\s]+\$?\s*([\d,]+\.?\d*)',
        'shipping': r'shipping[:\s]+\$?\s*([\d,]+\.?\d*)',
    }
    patterns.update(common_patterns)
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            amount_str = matches[-1].replace(',', '').replace(' ', '')
            try:
                value = float(amount_str)
                if key == 'balance_due':
                    amounts['total'] = value
                else:
                    amounts[key] = value
            except:
                continue
    
    if amounts['total'] > 0:
        amounts['amount'] = amounts['total']
    elif amounts['gross_worth'] > 0:
        amounts['amount'] = amounts['gross_worth']
    elif amounts['subtotal'] > 0:
        amounts['amount'] = amounts['subtotal']
    
    if amounts['amount'] == 0:
        numbers = re.findall(r'\$?\s*([\d,]+\.\d{2})', text)
        float_numbers = []
        for n in numbers:
            try:
                num = float(n.replace(',', ''))
                if 0 < num < 1000000:
                    float_numbers.append(num)
            except:
                continue
        if float_numbers:
            amounts['amount'] = max(float_numbers)
    
    return amounts

# -------------------------------
# ITEMS EXTRACTION
# -------------------------------
def extract_items(text, invoice_type='invoice'):
    """
    Extract line items from invoice/receipt.
    """
    items = []
    
    if invoice_type == 'invoice':
        item_section = re.search(r'ITEMS\s+(.*?)(?=SUMMARY|Total|Notes|Terms|$)', text, re.IGNORECASE | re.DOTALL)
        
        if item_section:
            section_text = item_section.group(1)
            lines = section_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or any(h in line.lower() for h in ['description', 'qty', 'quantity', 'net price', 'no.', 'rate', 'amount']):
                    continue
                
                parts = line.split()
                if len(parts) > 2:
                    start_idx = 1 if parts[0].rstrip('.').isdigit() else 0
                    desc_parts = []
                    for part in parts[start_idx:]:
                        if re.match(r'^\d+[.,]\d+$', part) or part in ['each', 'piece']:
                            break
                        desc_parts.append(part)
                    
                    if desc_parts:
                        description = ' '.join(desc_parts)
                        if len(description) > 10:
                            items.append(description)
        
        if not items:
            item_match = re.search(r'Item\s+(.*?)(?=Notes|Terms|Discount|Subtotal|$)', text, re.IGNORECASE | re.DOTALL)
            if item_match:
                item_text = item_match.group(1).strip()
                lines = item_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or 'quantity' in line.lower() or 'rate' in line.lower():
                        continue
                    if re.match(r'^[\d\s\.,\$]+$', line):
                        continue
                    
                    item_desc = re.sub(r'[A-Z]{3}-[A-Z]{2}-\d+', '', line)
                    item_desc = re.sub(r',?\s*(Chairs?|Furniture|Office|Technology|Supplies).*$', '', item_desc, flags=re.IGNORECASE)
                    item_desc = item_desc.strip().strip(',')
                    
                    if item_desc and len(item_desc) > 5:
                        items.append(item_desc)
    else:
        lines = text.split('\n')
        in_items = False
        
        for line in lines:
            line_upper = line.upper()
            
            if 'MANAGER' in line_upper or 'ST#' in line_upper:
                in_items = True
                continue
            
            if any(k in line_upper for k in ['SUBTOTAL', 'TOTAL', 'ITEMS SOLD', 'DISCOUNT']):
                break
            
            if in_items:
                if re.search(r'\d+\.\d{2}', line):
                    item = re.sub(r'\d+\.\d{2}.*$', '', line).strip()
                    item = re.sub(r'^\d+\s+lb.*?@', '', item).strip()
                    item = re.sub(r'^\d{10,}', '', item).strip()
                    
                    if item and len(item) > 2 and not item.isdigit():
                        items.append(item)
    
    return items[:20]

# -------------------------------
# CATEGORY EXTRACTION
# -------------------------------
def extract_category(vendor, items=None):
    """
    Assign category based on vendor name and items.
    """
    text_to_check = vendor.lower()
    if items:
        text_to_check += ' ' + ' '.join(items).lower()
    
    if any(k in text_to_check for k in ['walmart', 'grocery', 'food', 'market', 'banana', 'produce', 'supercenter']):
        return "Groceries"
    elif any(k in text_to_check for k in ['computer', 'pc', 'laptop', 'desktop', 'gaming', 'dell', 'hp', 'electronics']):
        return "Electronics"
    elif any(k in text_to_check for k in ['chair', 'desk', 'furniture', 'office', 'superstore', 'table', 'cabinet', 'manager']):
        return "Office/Furniture"
    elif any(k in text_to_check for k in ['uber', 'lyft', 'taxi', 'transport']):
        return "Transport"
    elif any(k in text_to_check for k in ['amazon', 'ebay', 'shop', 'store']):
        return "Shopping"
    else:
        return "Other"

# -------------------------------
# MAIN EXTRACTION FUNCTION
# -------------------------------
def extract_invoice_data(text):
    """
    Extract all relevant data from invoice text.
    """
    text = clean_text(text)
    invoice_type = detect_invoice_type(text)
    
    vendor = extract_vendor(text, invoice_type)
    amounts = extract_amounts(text, invoice_type)
    items = extract_items(text, invoice_type)
    
    result = {
        'Invoice_Number': extract_invoice_number(text),
        'Date': extract_date(text),
        'Vendor': vendor,
        'Invoice_Type': invoice_type,
        'Amount': amounts['amount'],
        'Subtotal': amounts['subtotal'],
        'Discount': amounts['discount'],
        'Shipping': amounts['shipping'],
        'Tax': amounts['tax'],
        'VAT': amounts['vat'],
        'Total': amounts['total'],
        'Items': '; '.join(items) if items else '',
        'Category': extract_category(vendor, items)
    }
    
    if invoice_type == 'invoice':
        seller = extract_seller_info(text)
        client = extract_client_info(text)
        
        result.update({
            'Seller_Name': seller.get('name', ''),
            'Seller_Address': seller.get('address', ''),
            'Seller_Tax_ID': seller.get('tax_id', ''),
            'Seller_IBAN': seller.get('iban', ''),
            'Client_Name': client.get('name', ''),
            'Client_Address': client.get('address', ''),
            'Client_Tax_ID': client.get('tax_id', ''),
            'Net_Worth': amounts['net_worth'],
            'Gross_Worth': amounts['gross_worth']
        })
    else:
        result.update({
            'Bill_To': extract_address(text, 'bill'),
            'Ship_To': extract_address(text, 'ship')
        })
    
    return result