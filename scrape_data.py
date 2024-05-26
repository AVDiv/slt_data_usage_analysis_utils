import os
from dotenv import load_dotenv
import traceback
import logging
from datetime import datetime, timedelta
import aiohttp
import pandas as pd

files_name = f'daily-usage-{datetime.now().strftime("%d-%m-%Y_%H:%M:%S")}'

load_dotenv()
logging.basicConfig(filename=f'data/{files_name}.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('Scraper')

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
            if response.status != 200 or not data['isSuccess']:
                traceback.print_exception(Exception(
f"""\033[1;31m
Error occured when requesting for data (Status Code: {response.status}):
\tError Message from API: {data['errorMessege']}
\tException Details from API: {data['exceptionDetail']}
\033[0m"""
                ))
                logger.error(
f"""
Error occured when requesting for data (Status Code: {response.status}):
\tError Message from API: {data['errorMessege']}
\tException Details from API: {data['exceptionDetail']}
"""
                )
                exit(1)
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
            if response.status != 200 or not data['isSuccess']:
                traceback.print_exception(Exception(
f"""\033[1;31m
Error occured when requesting for data (Status Code: {response.status}):
\tError Message from API: {data['errorMessege']}
\tException Details from API: {data['exceptionDetail']}
\033[0m"""
                ))
                logger.error(
f"""
Error occured when requesting for data (Status Code: {response.status}):
\tError Message from API: {data['errorMessege']}
\tException Details from API: {data['exceptionDetail']}
"""
                )
                exit(1)
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
            if response.status != 200 or not data['isSuccess']:
                traceback.print_exception(Exception(
f"""\033[1;31m
Error occured when requesting for data (Status Code: {response.status}):
\tError Message from API: {data['errorMessege']}
\tException Details from API: {data['exceptionDetail']}
\033[0m"""
                ))
                logger.error(
f"""
Error occured when requesting for data (Status Code: {response.status}):
\tError Message from API: {data['errorMessege']}
\tException Details from API: {data['exceptionDetail']}
"""
                )
                exit(1)
            return data



async def extract_daily_usage_to_csv():
    print("\033[1mExtracting daily usage stats for each month!")
    logger.info("Extracting daily usage stats for each month!")
    month_index = 0
    print("Starting data collection...")
    logger.info("Starting data collection...")
    df_structure = {
        'Date': [],
        'Usage Unit': [],
        'Total Usage': [],
        'Standard Package Total Usage': [],
        'Standard Package Peak Download': [],
        'Standard Package Peak Upload': [],
        'Standard Package Off-Peak Download': [],
        'Standard Package Off-Peak Upload': [],
        'Loyalty Data Total Usage': [],
        'Meet Max Package Total Usage': []
    }
    stat_df = pd.DataFrame(columns=list(df_structure.keys()), index=["Date"])
    current_extraction_date = datetime.today()
    print('\033[1;33m')
    while True:
      print(f'[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {month_index: <4}: Attempting to extract data of {current_extraction_date.strftime('%b-%Y')}...\t', end='')
      logger.debug(f'[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {month_index: <4}: Attempting to extract data of {current_extraction_date.strftime('%b-%Y')}...\t')
      data = await get_daily_usage_previous_months(
          subscriber_id=CONSTANTS['SUBSCRIBER_ID'],
          month_index=month_index
          )
      usage_stats = data['dataBundle']['dailylist']
      temp_df = pd.DataFrame(columns=list(df_structure.keys()), index=["Date"])
      for usage_stat in usage_stats:
        df_row_data = {
            'Date': usage_stat['date'],
            'Usage Unit': usage_stat['volumeunit'] ,
            'Total Usage': usage_stat['daily_total_usage']
        }
        if usage_stat['usages'] != None:
          for package_stats in usage_stat['usages']:
              if package_stats['sorter'] == 1:
                df_row_data['Standard Package Total Usage'] = package_stats['volume']
                df_row_data['Standard Package Peak Download'] = package_stats['volumes']['pdl']
                df_row_data['Standard Package Peak Upload'] = package_stats['volumes']['pul']
                df_row_data['Standard Package Off-Peak Download'] = package_stats['volumes']['opdl']
                df_row_data['Standard Package Off-Peak Upload'] = package_stats['volumes']['opul']
              elif package_stats['offer_name'] == 'Loyalty':
                df_row_data['Loyalty Data Total Usage'] = package_stats['volume']
              elif package_stats['offer_name'] == 'Meet Max' or package_stats['offer_name'] == 'Meet Lite':
                df_row_data['Meet Max Package Total Usage'] = package_stats['volume']
              else:
                print(f'\n\tSkipping package "{package_stats['offer_name']}" as it\'s not included in the list.')
                logger.warn(f'\n\tSkipping package "{package_stats["offer_name"]}" as it\'s not included in the list.')
        temp_df = temp_df._append(df_row_data, ignore_index=True)
      temp_df = temp_df[1:]
      if len(temp_df[temp_df['Total Usage'] == '0.0']) == len(temp_df):
          print('No more data')
          logger.debug('No more data')
          break
      else:
          print('Done!')
          logger.debug('Done!')
      month_index += 1
      stat_df = pd.concat([stat_df, temp_df], ignore_index=True)
      current_extraction_date -= timedelta(days=30)
    print('\033[0m')
    stat_df.to_csv(f'data/{files_name}.csv')
    print("\033[1;32mFinished data collection!\033[0m")
    logger.info('Finished data collection!')