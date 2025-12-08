import re
import pdfplumber
from datetime import datetime

def clean_merchant(description):
    """
    Cleans the merchant name by removing store numbers, cities, and common junk text.
    """
    # Remove "Card Purchase" or "POS Purchase"
    desc = re.sub(r'(Card Purchase|POS Purchase)', '', description, flags=re.IGNORECASE)
    
    # Remove dates like 08/20
    desc = re.sub(r'\d{2}/\d{2}', '', desc)
    
    # Remove store numbers (e.g., #1234, Store 567)
    desc = re.sub(r'(#\d+|Store\s*\d+)', '', desc, flags=re.IGNORECASE)
    
    # Remove common city names or state codes (Simplified list for now)
    # In a real app, this would be a more comprehensive list or NLP model
    desc = re.sub(r'\b(LONG BEACH|LOS ANGELES|CA|USA)\b', '', desc, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    return re.sub(r'\s+', ' ', desc).strip().title()

def tag_category(clean_merchant_name):
    """
    Categorizes the transaction based on the cleaned merchant name.
    """
    merchant_lower = clean_merchant_name.lower()
    
    rules = {
        'Subscription': ['netflix', 'spotify', 'hulu', 'disney', 'prime video'],
        'Groceries': ['vons', 'ralphs', 'target', 'walmart', 'trader joe', 'whole foods'],
        'Utilities': ['edison', 'spectrum', 'water', 'gas', 'electric'],
        'Food': ['chick-fil-a', 'starbucks', 'mcdonald', 'burger', 'pizza', 'cafe', 'restaurant'],
        'Transport': ['uber', 'lyft', 'shell', 'chevron', 'gas station'],
        'Shopping': ['amazon', 'best buy', 'clothing', 'shoe']
    }
    
    for category, keywords in rules.items():
        if any(keyword in merchant_lower for keyword in keywords):
            return category
            
    return 'Uncategorized'

def parse_pdf(file_path):
    transactions = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            for line in lines:
                # Regex to capture Date, Description, Amount, and optional Balance
                # Format: MM/DD Description ... Amount ... Balance
                # Example: 01/15 VONS #1234 LONG BEACH -50.00 1200.00
                
                # Try to match with balance first
                match_with_balance = re.match(r'(\d{2}/\d{2})\s+(.+?)\s+(-?\d+\.\d{2})\s+(\d+\.\d{2})', line)
                
                if match_with_balance:
                    date_str, desc, amount_str, balance_str = match_with_balance.groups()
                    balance = float(balance_str)
                else:
                    # Fallback to just amount
                    match_no_balance = re.match(r'(\d{2}/\d{2})\s+(.+?)\s+(-?\d+\.\d{2})', line)
                    if match_no_balance:
                        date_str, desc, amount_str = match_no_balance.groups()
                        balance = None
                    else:
                        continue

                # Add current year (assuming 2025 for now, or infer from file name)
                current_year = datetime.now().year
                try:
                    date_obj = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y")
                except ValueError:
                    continue # Skip invalid dates
                
                amount = float(amount_str)
                
                # Determine Type
                tx_type = 'debit' if amount < 0 else 'credit'
                
                # Clean Merchant
                merchant_clean = clean_merchant(desc)
                
                # Categorize
                category = tag_category(merchant_clean)
                
                transactions.append({
                    'date': date_obj,
                    'description': desc.strip(),
                    'amount': amount,
                    'category': category,
                    'vendor': desc.strip(), # Keep original as vendor for now, or use clean
                    'merchant_clean': merchant_clean,
                    'type': tx_type,
                    'balance_after': balance
                })
    return transactions
