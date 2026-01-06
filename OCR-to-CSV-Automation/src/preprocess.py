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
    Extract date and return in MM/DD/YYYY format (QuickBooks standard).
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
                        return date_obj.strftime('%m/%d/%Y')
                        
                elif date_type == 'ymd':
                    year, month, day = match
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%m/%d/%Y')
                    
                elif date_type == 'mdy' or date_type == 'timestamp':
                    month, day, year = match[:3] if date_type == 'timestamp' else match
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%m/%d/%Y')
                    
                elif date_type == 'short':
                    month, day, year = match
                    year = int(year)
                    year = 2000 + year if year < 50 else 1900 + year
                    date_obj = datetime(year, int(month), int(day))
                    return date_obj.strftime('%m/%d/%Y')
            except:
                continue
    
    return ""

# -------------------------------
# INVOICE NUMBER EXTRACTION
# -------------------------------
def extract_invoice_number(text):
    """
    Extract invoice/reference number.
    """
    patterns = [
        r'invoice\s+no[:\s]+(\S+)',
        r'invoice\s*#[:\s]*(\S+)',
        r'order\s+id[:\s]+(\S+)',
        r'#\s*(\d{5,})',
        r'tc#\s*(\d+)',
        r'op#\s*(\d+)',
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
    Extract vendor name cleanly without extra text.
    """
    lines = text.strip().split('\n')
    
    if invoice_type == 'invoice':
        seller_match = re.search(r'seller[:\s]+(.*?)(?:\n|Tax Id|Client:|$)', text, re.IGNORECASE | re.DOTALL)
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
        
        # Clean vendor name - remove special characters and extra words
        vendor = re.sub(r'^[^a-zA-Z]+', '', line_clean)
        
        # For receipts, take just the company name before any descriptive text
        if 'INVOICE' in vendor.upper():
            vendor = vendor.upper().split('INVOICE')[0].strip()
        
        # Remove stars and extra characters
        vendor = vendor.replace('*', ' ').replace('★', ' ')
        vendor = re.sub(r'\s+', ' ', vendor).strip()
        
        # Take first few words only
        words = vendor.split()
        if words:
            # For known stores, take specific format
            if 'WAL' in vendor.upper() and 'MART' in vendor.upper():
                return 'Walmart'
            elif 'SUPERSTORE' in vendor.upper():
                return 'SuperStore'
            
            # Otherwise take first 1-3 words
            vendor = ' '.join(words[:3])
            return vendor
    
    return "Unknown Vendor"

# -------------------------------
# SELLER/CLIENT EXTRACTION
# -------------------------------
def extract_seller_info(text):
    """
    Extract complete seller information for B2B invoices.
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
    Extract complete client/customer information.
    """
    # Try Client: format first (B2B invoices)
    client_match = re.search(r'client[:\s]+(.*?)(?=ITEMS|$)', text, re.IGNORECASE | re.DOTALL)
    if client_match:
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
    
    # Try Bill To: format (simple invoices)
    bill_match = re.search(r'bill\s+to[:\s]+(.*?)(?=ship\s+to|ship\s+mode|date|$)', text, re.IGNORECASE | re.DOTALL)
    if bill_match:
        bill_text = bill_match.group(1).strip()
        lines = [l.strip() for l in bill_text.split('\n') if l.strip()]
        
        return {
            'name': lines[0] if lines else '',
            'address': ', '.join(lines[1:]) if len(lines) > 1 else '',
            'tax_id': ''
        }
    
    return {'name': '', 'address': '', 'tax_id': ''}

def extract_ship_to(text):
    """
    Extract shipping address.
    """
    pattern = r'ship\s+to[:\s]+(.*?)(?=ship\s+mode|date|item|balance|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        ship_text = match.group(1).strip()
        ship_text = re.sub(r'\s+', ' ', ship_text)
        if len(ship_text) > 200:
            ship_text = ship_text[:200]
        return ship_text
    
    return ""

# -------------------------------
# AMOUNT EXTRACTION
# -------------------------------
def extract_amounts(text, invoice_type='invoice'):
    """
    Extract all financial amounts with proper decimal handling.
    """
    amounts = {
        'subtotal': '',
        'discount': '',
        'shipping': '',
        'tax': '',
        'vat': '',
        'total': '',
        'net_worth': '',
        'gross_worth': ''
    }
    
    # Define patterns for each amount type
    amount_patterns = {
        'subtotal': r'subtotal[:\s]+\$?\s*([\d,]+\.?\d{0,2})',
        'discount': r'discount[:\s\(]*\d*%?\)?[:\s]+\$?\s*([\d,]+\.?\d{0,2})',
        'shipping': r'shipping[:\s]+\$?\s*([\d,]+\.?\d{0,2})',
        'tax': r'(?:tax|vat(?!\s*\[))[:\s]+\$?\s*([\d,]+\.?\d{0,2})',
        'total': r'(?:total|balance\s+due)[:\s]+\$?\s*([\d,]+\.?\d{0,2})',
        'net_worth': r'net\s+worth[:\s]+\$?\s*([\d\s,]+\.?\d{0,2})',
        'vat': r'vat[:\s]+\$?\s*([\d\s,]+\.?\d{0,2})',
        'gross_worth': r'gross\s+worth[:\s]+\$?\s*([\d\s,]+\.?\d{0,2})',
    }
    
    for key, pattern in amount_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            amount_str = matches[-1].replace(',', '').replace(' ', '').strip()
            try:
                value = float(amount_str)
                amounts[key] = f"{value:.2f}"
            except:
                continue
    
    # Determine the primary total amount
    if amounts['total']:
        primary_total = amounts['total']
    elif amounts['gross_worth']:
        primary_total = amounts['gross_worth']
    elif amounts['subtotal']:
        primary_total = amounts['subtotal']
    else:
        # Fallback: find largest reasonable number
        numbers = re.findall(r'\$?\s*([\d,]+\.\d{2})', text)
        float_numbers = []
        for n in numbers:
            try:
                num = float(n.replace(',', ''))
                if 0 < num < 1000000:
                    float_numbers.append(num)
            except:
                continue
        primary_total = f"{max(float_numbers):.2f}" if float_numbers else ""
    
    amounts['amount'] = primary_total
    
    return amounts

# -------------------------------
# ITEMS EXTRACTION
# -------------------------------
def extract_items(text, invoice_type='invoice'):
    """
    Extract line items with descriptions.
    """
    items = []
    
    if invoice_type == 'invoice':
        # Method 1: Look for ITEMS section
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
        
        # Method 2: Look for Item/Quantity/Rate format (SuperStore style)
        if not items:
            item_match = re.search(r'Item\s+Quantity.*?\n(.*?)(?=Notes|Terms|Discount|Subtotal|$)', text, re.IGNORECASE | re.DOTALL)
            if item_match:
                item_text = item_match.group(1).strip()
                lines = item_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extract description (everything before quantity/amounts)
                    # Remove product codes like FUR-CH-4421
                    item_desc = re.sub(r'\s*\d+\s+\$[\d,.]+.*$', '', line)
                    item_desc = re.sub(r'[A-Z]{3}-[A-Z]{2}-\d+', '', item_desc)
                    item_desc = re.sub(r',?\s*(Chairs?|Furniture|Office|Technology|Supplies).*$', '', item_desc, flags=re.IGNORECASE)
                    item_desc = item_desc.strip().strip(',')
                    
                    if item_desc and len(item_desc) > 5:
                        items.append(item_desc)
    else:
        # Receipt format
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
                    item = re.sub(r'\s+[A-Z]$', '', item).strip()  # Remove single letter codes
                    
                    if item and len(item) > 2 and not item.isdigit():
                        items.append(item)
    
    return items[:20]

# -------------------------------
# CATEGORY/EXPENSE ACCOUNT
# -------------------------------
def extract_category(vendor, items=None):
    """
    Assign QuickBooks-compatible expense category.
    """
    text_to_check = vendor.lower()
    if items:
        text_to_check += ' ' + ' '.join(items).lower()
    
    # QuickBooks standard expense categories
    if any(k in text_to_check for k in ['walmart', 'grocery', 'food', 'market', 'banana', 'produce', 'supercenter']):
        return "Meals & Entertainment"
    elif any(k in text_to_check for k in ['computer', 'pc', 'laptop', 'desktop', 'gaming', 'dell', 'hp', 'electronics', 'tech']):
        return "Equipment"
    elif any(k in text_to_check for k in ['chair', 'desk', 'furniture', 'superstore', 'table', 'cabinet', 'office supplies']):
        return "Office Supplies"
    elif any(k in text_to_check for k in ['uber', 'lyft', 'taxi', 'transport', 'travel']):
        return "Travel"
    elif any(k in text_to_check for k in ['hotel', 'accommodation', 'lodging']):
        return "Travel"
    elif any(k in text_to_check for k in ['fuel', 'gas', 'petrol']):
        return "Auto & Truck Expenses"
    else:
        return "Other Business Expenses"

# -------------------------------
# MAIN EXTRACTION FUNCTION
# -------------------------------
def extract_invoice_data(text):
    """
    Extract all data in QuickBooks-compatible format.
    """
    text = clean_text(text)
    invoice_type = detect_invoice_type(text)
    
    vendor = extract_vendor(text, invoice_type)
    amounts = extract_amounts(text, invoice_type)
    items = extract_items(text, invoice_type)
    client = extract_client_info(text)
    
    # Build QuickBooks-compatible result
    result = {
        'Transaction Date': extract_date(text),
        'Vendor': vendor,
        'Ref Number': extract_invoice_number(text),
        'Amount': amounts['amount'],
        'Description': items[0] if items else '',
        'Memo': '; '.join(items) if items else '',
        'Category': extract_category(vendor, items),
        'Customer': client.get('name', ''),
        'Billable': 'No',
        'Tax Amount': amounts.get('tax', '') or amounts.get('vat', ''),
        'Subtotal': amounts['subtotal'],
        'Discount': amounts['discount'],
        'Shipping': amounts['shipping'],
        'Total': amounts['total'],
    }
    
    # Add shipping address if available
    ship_to = extract_ship_to(text)
    if ship_to:
        result['Shipping Address'] = ship_to
    
    # Add detailed fields for B2B invoices
    if invoice_type == 'invoice':
        seller = extract_seller_info(text)
        
        result.update({
            'Invoice Type': 'Bill',
            'Seller Name': seller.get('name', ''),
            'Seller Address': seller.get('address', ''),
            'Seller Tax ID': seller.get('tax_id', ''),
            'Customer Address': client.get('address', ''),
            'Customer Tax ID': client.get('tax_id', ''),
            'Net Worth': amounts.get('net_worth', ''),
            'Gross Worth': amounts.get('gross_worth', ''),
        })
    else:
        result['Invoice Type'] = 'Receipt'
    
    return result