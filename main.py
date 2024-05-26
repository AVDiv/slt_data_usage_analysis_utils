import asyncio
from scrape_data import extract_daily_usage_to_csv

if __name__ == "__main__":
  asyncio.run(extract_daily_usage_to_csv())