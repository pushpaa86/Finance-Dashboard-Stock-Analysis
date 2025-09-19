# ingest.py
from pathlib import Path
import pandas as pd

# ---- EDIT ONLY IF YOU WANT A DIFFERENT PATH ----
DATA_DIR = Path(r"C:\Users\Asus\Desktop\finance-dashboard\Data")  # where your yahoo_data.xlsx is
OUT_DIR = Path(r"C:\Users\Asus\Desktop\finance-dashboard\outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
# -----------------------------------------------

# Input filename (change if your file name differs)
input_file = DATA_DIR / "yahoo_data.xlsx"

# Read Excel (first sheet)
df = pd.read_excel(input_file, sheet_name=0)

# Normalize column names (strip spaces)
df.columns = [c.strip() for c in df.columns]

# Convert Date column to datetime (handles formats like "Apr 28, 2023")
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
else:
    raise ValueError("No 'Date' column found in the Excel file.")

# Rename columns to standard names if they differ
rename_map = {}
for col in df.columns:
    low = col.lower()
    if 'close' in low and 'adj' not in low:
        rename_map[col] = 'Close'
    if 'adj close' in low or 'adj' in low and 'close' in low:
        rename_map[col] = 'Adj Close'
    if 'open' in low:
        rename_map[col] = 'Open'
    if 'high' in low:
        rename_map[col] = 'High'
    if 'low' in low:
        rename_map[col] = 'Low'
    if 'volume' in low:
        rename_map[col] = 'Volume'
df = df.rename(columns=rename_map)

# Sort by date ascending and reset index
df = df.sort_values('Date').reset_index(drop=True)

# Save cleaned CSV for downstream scripts and Power BI
out_csv = OUT_DIR / "processed_prices.csv"
df.to_csv(out_csv, index=False, date_format="%Y-%m-%d")
print(f"Saved processed CSV: {out_csv}")
