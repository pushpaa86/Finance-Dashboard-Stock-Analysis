# analytics.py
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Paths ----
BASE = Path(r"C:\Users\Asus\Desktop\finance-dashboard")
IN_CSV = BASE / "outputs" / "processed_prices.csv"
OUT_DIR = BASE / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Read processed data
df = pd.read_csv(IN_CSV, parse_dates=['Date'])
df = df.sort_values('Date').reset_index(drop=True)

# Use 'Adj Close' if present, otherwise 'Close'
price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
if price_col not in df.columns:
    raise ValueError(f"Neither 'Adj Close' nor 'Close' present in {IN_CSV.name}")

# Calculate daily returns
df['return'] = df[price_col].pct_change()

# Cumulative returns (starting at 1)
df['cumulative_return'] = (1 + df['return'].fillna(0)).cumprod()

# Rolling volatility (30 trading days)
df['rolling_vol_30d'] = df['return'].rolling(window=30).std() * np.sqrt(252)

# Simple moving averages
df['SMA_50'] = df[price_col].rolling(window=50).mean()
df['SMA_200'] = df[price_col].rolling(window=200).mean()

# KPI calculations
def cagr(series, start_date, end_date):
    start_val = series.iloc[0]
    end_val = series.iloc[-1]
    years = (end_date - start_date).days / 365.25
    if years <= 0:
        return np.nan
    return (end_val / start_val) ** (1 / years) - 1

start_date = df['Date'].iloc[0]
end_date = df['Date'].iloc[-1]
cagr_val = cagr(df[price_col].dropna(), start_date, end_date)

ann_vol = df['return'].std() * np.sqrt(252)
sharpe = None
if not np.isnan(ann_vol) and ann_vol != 0:
    rf = 0.0  # risk-free rate
    sharpe = (df['return'].mean() * 252 - rf) / ann_vol

# Max drawdown
cum = (1 + df['return'].fillna(0)).cumprod()
running_max = cum.cummax()
drawdown = (cum - running_max) / running_max
max_dd = drawdown.min()

# Save summary KPIs
kpis = {
    'start_date': start_date.strftime("%Y-%m-%d"),
    'end_date': end_date.strftime("%Y-%m-%d"),
    'CAGR': cagr_val,
    'Annualized Volatility': ann_vol,
    'Sharpe (ann.)': sharpe,
    'Max Drawdown': max_dd
}
kpi_df = pd.DataFrame([kpis])
kpi_df.to_csv(OUT_DIR / "kpis_summary.csv", index=False)
print("Saved KPIs to outputs/kpis_summary.csv")

# Save time-series summary
ts_cols = ['Date', price_col, 'return', 'cumulative_return', 'rolling_vol_30d', 'SMA_50', 'SMA_200']
df[ts_cols].to_csv(OUT_DIR / "timeseries_summary.csv", index=False)
print("Saved time-series to outputs/timeseries_summary.csv")

# --- Charts ---
plt.rcParams.update({'figure.max_open_warning': 0})

# 1) Cumulative return chart
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df['Date'], df['cumulative_return'])
ax.set_title('Cumulative Return')
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Return (x)')
fig.tight_layout()
fig.savefig(OUT_DIR / "cumulative_return.png")
plt.close(fig)

# 2) Price + SMAs
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df['Date'], df[price_col], label='Price')
if 'SMA_50' in df.columns: ax.plot(df['Date'], df['SMA_50'], label='SMA 50')
if 'SMA_200' in df.columns: ax.plot(df['Date'], df['SMA_200'], label='SMA 200')
ax.set_title('Price with 50/200 SMA')
ax.set_xlabel('Date')
ax.legend()
fig.tight_layout()
fig.savefig(OUT_DIR / "price_sma.png")
plt.close(fig)

# 3) Rolling volatility
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df['Date'], df['rolling_vol_30d'])
ax.set_title('30-day Rolling Annualized Volatility')
ax.set_xlabel('Date')
ax.set_ylabel('Volatility (annualized)')
fig.tight_layout()
fig.savefig(OUT_DIR / "rolling_volatility.png")
plt.close(fig)

print("Saved chart PNGs to outputs/*.png")
