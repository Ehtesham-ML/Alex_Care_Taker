import pdfplumber
import pandas as pd
import re
import os
# Input and output directories
input_dir = "input"
output_dir = "output"
# Columns to extract
columns = [
    "Client", "Suffix", "Name", "Rate Type", "Quantity", "Rate", "Subtotal", "Care Level",
    "Six Month Begin", "Days Attended", "Days Absent", "Total Days Absent", "C1 Days Absent",
    "Holidays", "Approved Days", "C1 Days", "Gross Pay", "Weekly Fee", "Fee Due",
    "Total Net Adjusted Pay", "Special Needs", "Previously Paid", "Difference Paid"
]
# Dictionary to hold data for each provider name
provider_data = {}
# Helper: parse payment lines
def parse_payment_line(line):
    line = re.sub(r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)(\$\d+(?:,\d{3})*(?:\.\d{2})?)', r'\1 \2', line)
    parts = line.split()
    if len(parts) < 20:
        return None
    row_data = []
    try:
        client, suffix = parts[0], parts[1]
        if not (re.match(r'^\d{8}$', client) and re.match(r'^\d{2}$', suffix)):
            return None
        row_data += [client, suffix]
        name_parts = []
        i = 2
        while i < len(parts) and re.match(r'^[A-Za-z]+$', parts[i]):
            name_parts.append(parts[i])
            i += 1
        if not name_parts:
            return None
        row_data.append(' '.join(name_parts))
        if i >= len(parts) or not re.match(r'^[WD]$', parts[i]):
            return None
        row_data.append(parts[i]); i += 1
        if i >= len(parts) or not re.match(r'^\d+\.\d{2}$', parts[i]):
            return None
        row_data.append(parts[i]); i += 1
        for _ in range(17):
            if i >= len(parts):
                return None
            row_data.append(parts[i]); i += 1
        if len(row_data) == len(columns):
            return row_data
        else:
            return None
    except:
        return None
def fallback_parse(line):
    pattern = r'''
        (\d{8})\s+(\d{2})\s+([A-Za-z]+\s+[A-Za-z]+)\s+([WD])\s+(\d+\.\d{2})\s*
        (\$\d+(?:,\d{3})*(?:\.\d{2})?)\s*(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+([A-Z])\s+
        (\d{1,2}/\d{2})\s+(.+)
    '''
    match = re.match(pattern, line, re.VERBOSE)
    if match:
        groups = list(match.groups())
        remaining = groups[9].split()
        result = groups[:9] + remaining
        if len(result) >= len(columns):
            return result[:len(columns)]
        elif len(result) >= 20:
            while len(result) < len(columns):
                result.append("")
            return result
    return None
# Process each PDF
for filename in os.listdir(input_dir):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_dir, filename)
        print(f":page_facing_up: Processing {filename}")
        with pdfplumber.open(pdf_path) as pdf:
            provider_name = None
            rows = []
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("Provider ") and "Provider number" not in line:
                        provider_name = line.strip()
                        print(f":label: Found Provider: {provider_name}")
                    if re.match(r'^\d{8}', line):
                        parsed_row = parse_payment_line(line)
                        if parsed_row:
                            rows.append(parsed_row)
                        else:
                            fallback_row = fallback_parse(line)
                            if fallback_row:
                                rows.append(fallback_row)
            if provider_name and rows:
                provider_name = ' '.join(provider_name.split())
                if provider_name not in provider_data:
                    provider_data[provider_name] = []
                provider_data[provider_name].extend(rows)
                print(f":white_tick: Added {len(rows)} rows for {provider_name}")
# Save merged data to separate Excel file per provider
os.makedirs(output_dir, exist_ok=True)
# Define formatting functions
def format_currency(val):
    try:
        return "${:,.2f}".format(float(val.replace('$', '').replace(',', '')))
    except:
        return val
def format_number(val):
    try:
        return "{:.2f}".format(float(val))
    except:
        return val
if provider_data:
    for provider, data in provider_data.items():
        df = pd.DataFrame(data, columns=columns)
        # Apply formatting to relevant columns
        currency_cols = ["Rate", "Subtotal", "Gross Pay", "Fee Due", "Total Net Adjusted Pay", "Previously Paid", "Difference Paid"]
        numeric_cols = ["Quantity", "Weekly Fee"]
        for col in currency_cols:
            if col in df.columns:
                df[col] = df[col].apply(format_currency)
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(format_number)
        # Ensure uniqueness by dropping duplicate rows
        df.drop_duplicates(inplace=True)
        # Save or append
        safe_provider_name = re.sub(r'[\\/*?:"<>|]', "_", provider)
        excel_path = os.path.join(output_dir, f"{safe_provider_name}.xlsx")
        if os.path.exists(excel_path):
            existing_df = pd.read_excel(excel_path, dtype=str).fillna("")
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(inplace=True)
            combined_df.to_excel(excel_path, index=False)
            print(f":file_folder: Appended {len(df)} rows to existing file for '{provider}'")
        else:
            df.to_excel(excel_path, index=False)
            print(f":file_folder: Saved {len(df)} rows for '{provider}' to '{excel_path}'")
else:
    print(":warning: No data found in any PDF.")