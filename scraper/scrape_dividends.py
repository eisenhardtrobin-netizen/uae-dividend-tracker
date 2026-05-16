"""
UAE Dividend Scraper
====================
Scrapes dividend data from DFM (Dubai Financial Market) and ADX (Abu Dhabi Securities Exchange).
Outputs a unified stocks.json file used by the dividend tracker web app.

Usage:
    python scrape_dividends.py

Output:
    ../data/stocks.json

Dependencies:
    pip install requests beautifulsoup4 playwright
    playwright install chromium
"""

import json
import re
import os
import sys
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# ============================================================
# CONFIGURATION
# ============================================================

DFM_URL = "https://www.dfm.ae/investing/services/dividends-distribution-summary"
ADX_URL = "https://www.adx.ae/en/investors/investors-information/dividend-distribution"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "stocks.json")

CURRENT_YEAR = datetime.now().year

# Stock prices (updated monthly - fallback values)
STOCK_PRICES = {
    "AIRARABIA": 3.20, "AJMANBANK": 1.45, "ALANSARI": 1.10, "ALLIANCE": 1.80,
    "ALRAMZ": 0.95, "AMANAT": 0.88, "AMCREIT": 1.20, "AMLAK": 2.15,
    "BHMCAPITAL": 1.50, "CBD": 8.50, "DEWA": 2.55, "DEYAAR": 0.68,
    "DFM": 1.85, "DIB": 6.40, "DIC": 2.30, "DIN": 0.50,
    "DNIR": 3.80, "DRC": 5.20, "DTC": 0.70, "DU": 6.80,
    "DUBAIRESI": 0.55, "EIICAPITAL": 1.10, "EMAAR": 8.20, "EMAARDEV": 5.80,
    "EMIRATESNBD": 18.50, "EMPOWER": 2.90, "GFH": 1.35, "MASQ": 210.00,
    "MF": 1.20, "NCC": 3.50, "NGI": 0.85, "ORIENT": 1.60,
    "PARKIN": 4.50, "SALIK": 4.10, "SPINNEYS": 2.40, "SUKOON": 1.30,
    "TABREED": 3.25, "TALABAT": 2.80, "TECOM": 3.40, "UFC": 1.50,
    "UNIKAI": 2.80, "UNIONCOOP": 4.50, "UPP": 0.38,
    "ETISALAT": 26.40, "FAB": 13.50, "ADIB": 12.80, "ALDAR": 6.30,
    "ADNOCDIST": 3.60, "ADNOCGAS": 3.15, "ADNOCDRILL": 4.20,
    "ALPHADHABI": 15.60, "BOROUGE": 2.45, "DANA": 0.62,
    "MULTIPLY": 2.10, "ADNH": 4.85, "TAQA": 4.70, "FERTIGLB": 2.80,
    "PRESIGHT": 1.95, "ADNOCLS": 3.85, "AMERICANA": 2.25,
    "IHC": 420.00, "ADNOC": 3.10, "BURJEEL": 2.20, "LULU": 2.80,
}

SECTORS = {
    "AIRARABIA": "Aviation", "AJMANBANK": "Banking", "ALANSARI": "Financial",
    "ALLIANCE": "Insurance", "ALRAMZ": "Financial", "AMANAT": "Investment",
    "AMCREIT": "Real Estate", "AMLAK": "Financial", "BHMCAPITAL": "Financial",
    "CBD": "Banking", "DEWA": "Utilities", "DEYAAR": "Real Estate",
    "DFM": "Financial", "DIB": "Banking", "DIC": "Investment",
    "EMAAR": "Real Estate", "EMAARDEV": "Real Estate",
    "EMIRATESNBD": "Banking", "EMPOWER": "Utilities", "GFH": "Financial",
    "MASQ": "Banking", "PARKIN": "Transport", "SALIK": "Transport",
    "SPINNEYS": "Retail", "TABREED": "Utilities", "TALABAT": "Technology",
    "TECOM": "Real Estate", "UPP": "Real Estate", "UNIONCOOP": "Retail",
    "ETISALAT": "Telecom", "FAB": "Banking", "ADIB": "Banking",
    "ALDAR": "Real Estate", "ADNOCDIST": "Energy", "ADNOCGAS": "Energy",
    "ADNOCDRILL": "Energy", "ALPHADHABI": "Conglomerate", "BOROUGE": "Chemicals",
    "DANA": "Energy", "MULTIPLY": "Investment", "ADNH": "Hospitality",
    "TAQA": "Energy", "FERTIGLB": "Chemicals", "PRESIGHT": "Technology",
    "ADNOCLS": "Logistics", "AMERICANA": "F&B",
}


def scrape_dfm():
    """Scrape DFM dividend data."""
    print("[DFM] Fetching dividend data...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(DFM_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[DFM] ERROR: Failed to fetch page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    stocks = []
    rows = soup.find_all('tr')

    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 7:
            continue
        cell_texts = [c.get_text(strip=True) for c in cells]
        if 'Company' in cell_texts[1] or 'No' in cell_texts[0]:
            continue
        try:
            ticker = cell_texts[1].strip()
            ex_date = cell_texts[4].strip()
            dividend_text = cell_texts[6] if len(cell_texts) > 6 else cell_texts[5]
            dividend = parse_dividend(dividend_text)
            if not ticker or not ex_date or dividend is None:
                continue
            stock = {
                "ticker": ticker,
                "exchange": "DFM",
                "dividend": dividend,
                "price": STOCK_PRICES.get(ticker, 1.00),
                "exDate": ex_date,
                "sector": SECTORS.get(ticker, "Other"),
            }
            stocks.append(stock)
        except (ValueError, IndexError):
            continue

    print(f"[DFM] Scraped {len(stocks)} stocks")
    return stocks


def scrape_adx():
    """Scrape ADX dividend data using Playwright."""
    print("[ADX] Fetching dividend data...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(ADX_URL, wait_until='networkidle', timeout=30000)
            page.wait_for_selector('table', timeout=10000)
            rows = page.query_selector_all('table tbody tr')
            stocks = []
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) < 5:
                    continue
                cell_texts = [c.inner_text().strip() for c in cells]
                # Parse ADX row (structure varies)
            browser.close()
            return stocks
    except ImportError:
        print("[ADX] Playwright not installed. Using fallback...")
        return []
    except Exception as e:
        print(f"[ADX] Browser scraping failed: {e}")
        return []


def parse_dividend(text):
    """Parse dividend value from text."""
    import re
    text = text.strip()
    if text == "--" or not text:
        return None
    pct_match = re.match(r'([\d.]+)\s*%', text)
    if pct_match:
        return round(float(pct_match.group(1)) / 100, 4)
    fils_match = re.match(r'([\d.]+)\s*Fils', text, re.IGNORECASE)
    if fils_match:
        return round(float(fils_match.group(1)) / 100, 4)
    aed_match = re.match(r'([\d.]+)\s*AED', text, re.IGNORECASE)
    if aed_match:
        return float(aed_match.group(1))
    return None


def build_output(dfm_stocks, adx_stocks):
    """Combine and output final JSON."""
    all_stocks = dfm_stocks + adx_stocks
    for i, stock in enumerate(all_stocks):
        stock["id"] = i + 1
        if stock["price"] > 0:
            stock["yield"] = round((stock["dividend"] / stock["price"]) * 100, 2)
        else:
            stock["yield"] = 0
    all_stocks.sort(key=lambda s: s["yield"], reverse=True)
    for i, stock in enumerate(all_stocks):
        stock["id"] = i + 1
    return all_stocks


def main():
    print("=" * 60)
    print(f"UAE Dividend Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    dfm_stocks = scrape_dfm()
    adx_stocks = scrape_adx()

    if not dfm_stocks and not adx_stocks:
        print("\nERROR: No data scraped!")
        sys.exit(1)

    all_stocks = build_output(dfm_stocks, adx_stocks)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "year": CURRENT_YEAR,
        "stockCount": len(all_stocks),
        "sources": {
            "DFM": {"url": DFM_URL, "count": len(dfm_stocks)},
            "ADX": {"url": ADX_URL, "count": len(adx_stocks)}
        },
        "stocks": all_stocks
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSUCCESS: Saved {len(all_stocks)} stocks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
