import os
from dotenv import load_dotenv
from datetime import datetime
import aiohttp

load_dotenv()

CONSTANTS = {
  'BASE_URL': "https://omniscapp.slt.lk/mobitelint/slt/api",
  'ACCESS_TOKEN': os.getenv('ACCESS_TOKEN'),
  'CLIENT_ID': os.getenv('CLIENT_ID'),
	'SUBSCRIBER_ID': os.getenv('SUBSCRIBER_ID'),
  # 'SUBSCRIBER_EMAIL': os.getenv('SUBSCRIBER_EMAIL'),
	# 'SUBSCRIBER_PASSWORD': os.getenv('SUBSCRIBER_PASSWORD'),
}

HEADERS = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 
  'Accept-Language': 'en-US,en;q=0.9',
  'Authorization': f'bearer {CONSTANTS["ACCESS_TOKEN"]}',
  'X-Ibm-Client-Id': CONSTANTS['CLIENT_ID']
}

async def get_daily_usage_previous_months(
    *,
    subscriber_id: str,
    bill_date: int = 1,
    month_index: int = 2
):
  url = f"{CONSTANTS['BASE_URL']}/BBVAS/EnhancedPreviousDailyUsage?subscriberID={subscriber_id}&billDate={bill_date}&monthIndex={month_index}"
  async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


async def get_daily_usage_current_month(
    *,
    subscriber_id: str,
    bill_date: int = 1
):
  url = f"{CONSTANTS['BASE_URL']}/BBVAS/EnhancedCurrentDailyUsage?subscriberID={subscriber_id}&billDate={bill_date}"
  async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


async def get_protocol_report(
    *,
    subscriber_id: str,
    date: datetime
):
  url = f"{CONSTANTS['BASE_URL']}/BBVAS/ProtocolReport?subscriberID={subscriber_id}&date={date.strftime('%Y-%m-%d')}"
  async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            data = await response.json()
            return data

