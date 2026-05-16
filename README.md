# UAE Dividend Tracker

A web-based tool that tracks dividend payments for all companies listed on DFM (Dubai Financial Market) and ADX (Abu Dhabi Securities Exchange).

## Features

- 📅 **Full-year calendar** with color-coded dividend events
- 🏆 **Top Dividends ranking** by yield (filterable: upcoming only / include past)
- ⭐ **Favorites system** — star stocks for your personal watchlist
- 📥 **Download .ics files** — add reminders to Outlook/Google Calendar
- ⏰ **Custom reminder days** — choose when to be alerted before buy-by dates
- 🔍 **Search & filter** — by name, ticker, exchange, sector, or time window
- 🌙 **Dark/Light mode** toggle
- 📱 **Responsive** — works on desktop and mobile

## Project Structure

```
uae-dividend-tracker/
├── index.html              # Main web app (single-page, self-contained)
├── data/
│   └── stocks.json         # Dividend data (auto-updated monthly)
├── scraper/
│   ├── scrape_dividends.py # Python scraper for DFM & ADX
│   └── requirements.txt    # Python dependencies
├── .github/
│   └── workflows/
│       └── update-dividends.yml  # GitHub Actions monthly cron
└── README.md
```

## Setup

### 1. Host on GitHub Pages (free)

1. Create a new GitHub repository
2. Upload all files from this folder
3. Go to **Settings → Pages → Source → Deploy from branch (main)**
4. Your tool is live at `https://yourusername.github.io/uae-dividend-tracker/`

### 2. Enable Automated Updates

The GitHub Action runs automatically on the **1st of every month at 10:00 AM Dubai time**.

It will:
1. Scrape latest dividend data from DFM.ae and ADX.ae
2. Update `data/stocks.json`
3. Auto-commit the changes → your live site updates automatically

You can also trigger it manually: **Actions → Update UAE Dividend Data → Run workflow**

### 3. Local Development

```bash
# Install Python dependencies
cd scraper
pip install -r requirements.txt
playwright install chromium

# Run the scraper manually
python scrape_dividends.py

# Serve locally
cd ..
python -m http.server 8000
# Open http://localhost:8000
```

## Data Sources

| Exchange | Source | Method |
|----------|--------|--------|
| DFM | [dfm.ae/dividends-distribution-summary](https://www.dfm.ae/investing/services/dividends-distribution-summary) | HTML scraping (static table) |
| ADX | [adx.ae/dividend-distribution](https://www.adx.ae/en/investors/investors-information/dividend-distribution) | Playwright browser (dynamic) + manual fallback |

## Updating Stock Prices

Stock prices in `scraper/scrape_dividends.py` (the `STOCK_PRICES` dict) should be updated periodically for accurate yield calculations. In future versions, this could be automated via a market data API.

## Sharing

Just share the GitHub Pages link with friends! No account or installation needed.

## License

Free to use and modify. Not financial advice — always verify dates with DFM/ADX before trading.
